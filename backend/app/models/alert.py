from app.models.base import db, datetime
from sqlalchemy import Enum as SQLEnum
import enum


class AlertLevelEnum(enum.Enum):
    LOW = "baixo"
    MEDIUM = "médio"
    HIGH = "alto"
    CRITICAL = "crítico"


class AlertTypeEnum(enum.Enum):
    IRRIGATION = "rega"
    FUNGAL_RISK = "risco_fungos"
    HARVEST_SUGGESTION = "sugestao_colheita"
    WEATHER_WARNING = "aviso_meteorologico"


class VineyardAlert(db.Model):
    """Modelo para armazenar alertas vitícolas"""
    __tablename__ = 'vineyard_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(SQLEnum(AlertTypeEnum), nullable=False)
    level = db.Column(SQLEnum(AlertLevelEnum), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    city_id = db.Column(db.Integer, nullable=False)
    city_name = db.Column(db.String(100), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            "id": self.id,
            "alert_type": self.alert_type.value,
            "level": self.level.value,
            "message": self.message,
            "recommendation": self.recommendation,
            "city_id": self.city_id,
            "city_name": self.city_name,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "is_acknowledged": self.is_acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }
    
    def __repr__(self):
        return f'<VineyardAlert {self.alert_type.value} - {self.level.value} - {self.city_name}>'

