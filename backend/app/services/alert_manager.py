from typing import List, Optional
from datetime import datetime, timedelta
from app.models import db
from app.models.alert import VineyardAlert as AlertModel, AlertTypeEnum, AlertLevelEnum
from app.services.vineyard_analyzer import VineyardAlert, AlertType, AlertLevel


class AlertManager:
    """
    Gestor de alertas vitícolas
    
    Responsável por armazenar, recuperar e gerir alertas gerados
    pelo sistema de análise meteorológica.
    """
    
    def __init__(self):
        self.alert_history_days = 30  # Manter histórico por 30 days
    
    def save_alert(self, alert: VineyardAlert) -> AlertModel:
        """
        Guarda um alerta na base de dados
        
        Args:
            alert: Alerta a guardar
            
        Returns:
            AlertModel: Modelo guardado na BD
        """
        # Converter enums
        alert_type_enum = AlertTypeEnum(alert.alert_type.value)
        alert_level_enum = AlertLevelEnum(alert.level.value)
        
        # Verificar se já existe alerta similar ativo
        existing_alert = AlertModel.query.filter_by(
            alert_type=alert_type_enum,
            city_id=alert.city_id,
            is_active=True
        ).first()
        
        if existing_alert:
            # Atualizar alerta existente
            existing_alert.level = alert_level_enum
            existing_alert.message = alert.message
            existing_alert.recommendation = alert.recommendation
            existing_alert.expires_at = alert.expires_at
            existing_alert.created_at = datetime.utcnow()
            db.session.commit()
            return existing_alert
        else:
            # Criar novo alerta
            new_alert = AlertModel(
                alert_type=alert_type_enum,
                level=alert_level_enum,
                message=alert.message,
                recommendation=alert.recommendation,
                city_id=alert.city_id,
                city_name=alert.city_name,
                expires_at=alert.expires_at
            )
            db.session.add(new_alert)
            db.session.commit()
            return new_alert
    
    def get_active_alerts(self, city_id: Optional[int] = None) -> List[AlertModel]:
        """
        Recupera alertas ativos
        
        Args:
            city_id: ID da cidade (opcional)
            
        Returns:
            Lista de alertas ativos
        """
        query = AlertModel.query.filter_by(is_active=True)
        
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        # Filtrar alertas não expirados
        now = datetime.utcnow()
        query = query.filter(
            db.or_(
                AlertModel.expires_at.is_(None),
                AlertModel.expires_at > now
            )
        )
        
        return query.order_by(AlertModel.created_at.desc()).all()
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """
        Marca um alerta como reconhecido
        
        Args:
            alert_id: ID do alerta
            
        Returns:
            True se sucesso, False caso contrário
        """
        alert = AlertModel.query.get(alert_id)
        if alert:
            alert.is_acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def deactivate_alert(self, alert_id: int) -> bool:
        """
        Desativa um alerta
        
        Args:
            alert_id: ID do alerta
            
        Returns:
            True se sucesso, False caso contrário
        """
        alert = AlertModel.query.get(alert_id)
        if alert:
            alert.is_active = False
            db.session.commit()
            return True
        return False
    
    def cleanup_expired_alerts(self):
        """Remove alertas expirados da base de dados"""
        now = datetime.utcnow()
        
        # Desativar alertas expirados
        expired_alerts = AlertModel.query.filter(
            AlertModel.expires_at < now,
            AlertModel.is_active == True
        ).all()
        
        for alert in expired_alerts:
            alert.is_active = False
        
        # Remover alertas antigos do histórico
        old_threshold = now - timedelta(days=self.alert_history_days)
        AlertModel.query.filter(
            AlertModel.created_at < old_threshold,
            AlertModel.is_active == False
        ).delete()
        
        db.session.commit()
    
    def get_alert_statistics(self, city_id: Optional[int] = None, 
                           days: int = 7) -> Dict:
        """
        Retorna estatísticas de alertas
        
        Args:
            city_id: ID da cidade (opcional)
            days: Número de dias para análise
            
        Returns:
            Dicionário com estatísticas
        """
        since = datetime.utcnow() - timedelta(days=days)
        query = AlertModel.query.filter(AlertModel.created_at >= since)
        
        if city_id:
            query = query.filter_by(city_id=city_id)
        
        alerts = query.all()
        
        stats = {
            "total_alerts": len(alerts),
            "by_type": {},
            "by_level": {},
            "active_alerts": len([a for a in alerts if a.is_active]),
            "acknowledged_alerts": len([a for a in alerts if a.is_acknowledged])
        }
        
        # Contar por tipo
        for alert in alerts:
            alert_type = alert.alert_type.value
            stats["by_type"][alert_type] = stats["by_type"].get(alert_type, 0) + 1
        
        # Contar por nível
        for alert in alerts:
            alert_level = alert.level.value
            stats["by_level"][alert_level] = stats["by_level"].get(alert_level, 0) + 1
        
        return stats