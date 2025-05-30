from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from datetime import datetime
import json

class WeatherWebSocket:
    """
    Classe para gerenciar conexões WebSocket para dados meteorológicos
    """
    
    def __init__(self, socketio: SocketIO, weather_service):
        self.socketio = socketio
        self.weather_service = weather_service
        self.active_connections = {}
        
        # Registrar como observador do serviço meteorológico
        self.weather_service.add_observer(self)
        
        # Registrar eventos WebSocket
        self._register_events()
    
    def _register_events(self):
        """Registrar eventos WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect():
            client_id = request.sid
            self.active_connections[client_id] = {
                'connected_at': datetime.utcnow(),
                'subscribed_cities': []
            }
            
            emit('connection_established', {
                'client_id': client_id,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Conectado ao serviço meteorológico'
            })
            
            print(f"Cliente conectado: {client_id}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            client_id = request.sid
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            
            print(f"Cliente desconectado: {client_id}")
        
        @self.socketio.on('subscribe_city')
        def handle_subscribe_city(data):
            """Subscrever atualizações de uma cidade específica"""
            client_id = request.sid
            city_name = data.get('city_name')
            
            if client_id in self.active_connections and city_name:
                if city_name not in self.active_connections[client_id]['subscribed_cities']:
                    self.active_connections[client_id]['subscribed_cities'].append(city_name)
                    join_room(f"city_{city_name}")
                    
                    emit('subscription_confirmed', {
                        'city_name': city_name,
                        'message': f'Subscrito a atualizações de {city_name}'
                    })
                    
                    # Enviar dados mais recentes da cidade
                    latest_data = self.weather_service.get_latest_weather(city_name)
                    if latest_data:
                        emit('weather_data', {
                            'city': city_name,
                            'data': latest_data[0],
                            'type': 'latest'
                        })
        
        @self.socketio.on('unsubscribe_city')
        def handle_unsubscribe_city(data):
            """Cancelar subscrição de uma cidade"""
            client_id = request.sid
            city_name = data.get('city_name')
            
            if client_id in self.active_connections and city_name:
                if city_name in self.active_connections[client_id]['subscribed_cities']:
                    self.active_connections[client_id]['subscribed_cities'].remove(city_name)
                    leave_room(f"city_{city_name}")
                    
                    emit('unsubscription_confirmed', {
                        'city_name': city_name,
                        'message': f'Subscrição cancelada para {city_name}'
                    })
        
        @self.socketio.on('get_weather_status')
        def handle_get_weather_status():
            """Obter status geral do sistema meteorológico"""
            status = {
                'collecting': self.weather_service.is_collecting,
                'active_connections': len(self.active_connections),
                'available_cities': [city['name'] for city in self.weather_service.cities],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            emit('weather_status', status)
        
        @self.socketio.on('request_latest_data')
        def handle_request_latest_data(data):
            """Solicitar dados mais recentes"""
            city_name = data.get('city_name')
            latest_data = self.weather_service.get_latest_weather(city_name)
            
            emit('latest_weather_data', {
                'city': city_name,
                'data': latest_data,
                'timestamp': datetime.utcnow().isoformat()
            })
    
    def update(self, data):
        """
        Método do Observer Pattern - chamado quando há novos dados meteorológicos
        
        Args:
            data (Dict): Dados meteorológicos atualizados
        """
        city_name = data.get('city')
        
        if city_name:
            # Enviar para todos os clientes subscritos à cidade
            self.socketio.emit('weather_update', {
                'city': city_name,
                'data': data['data'],
                'timestamp': data['timestamp'],
                'type': 'real_time'
            }, room=f"city_{city_name}")
            
            # Enviar para todos os clientes conectados (broadcast geral)
            self.socketio.emit('general_weather_update', {
                'city': city_name,
                'summary': {
                    'temperature': data['data']['main']['temp'],
                    'humidity': data['data']['main']['humidity'],
                    'description': data['data']['weather'][0]['description']
                },
                'timestamp': data['timestamp']
            })
    
    def broadcast_system_message(self, message: str, message_type: str = 'info'):
        """Enviar mensagem do sistema para todos os clientes conectados"""
        self.socketio.emit('system_message', {
            'message': message,
            'type': message_type,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_connection_stats(self):
        """Obter estatísticas das conexões"""
        return {
            'total_connections': len(self.active_connections),
            'connections': {
                client_id: {
                    'connected_at': conn_info['connected_at'].isoformat(),
                    'subscribed_cities': conn_info['subscribed_cities']
                }
                for client_id, conn_info in self.active_connections.items()
            }
        }
