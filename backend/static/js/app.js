// Configuração da API
const API_BASE = 'http://127.0.0.1:5000/api';

// Função para buscar dados do sistema
async function fetchSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/weather/status`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('system-status').innerHTML = `
                <div class="weather-item">
                    <span class="status-indicator ${data.status.collecting ? 'status-online' : 'status-offline'}"></span>
                    <span>Coleta: ${data.status.collecting ? 'Ativa' : 'Inativa'}</span>
                </div>
                <div class="weather-item">
                    <span class="weather-icon">🏙️</span>
                    <span>Cidades: ${data.status.cities_monitored}</span>
                </div>
                <div class="weather-item">
                    <span class="weather-icon">📊</span>
                    <span>Registos recentes: ${data.status.recent_records}</span>
                </div>
                <div class="weather-item">
                    <span class="weather-icon">🔑</span>
                    <span>API: ${data.status.api_key_configured ? 'Configurada' : 'Não configurada'}</span>
                </div>
            `;
        }
    } catch (error) {
        document.getElementById('system-status').innerHTML = `
            <div style="color: #f56565;">❌ Erro ao carregar status</div>
        `;
    }
}

// Função para buscar cidades e dados meteorológicos
async function fetchCitiesWeather() {
    try {
        const [citiesResponse, weatherResponse] = await Promise.all([
            fetch(`${API_BASE}/weather/cities`),
            fetch(`${API_BASE}/weather/current`)
        ]);

        const citiesData = await citiesResponse.json();
        const weatherData = await weatherResponse.json();

        if (citiesData.success && weatherData.success) {
            renderCities(citiesData.cities, weatherData.data);
        }
    } catch (error) {
        document.getElementById('cities-container').innerHTML = `
            <div style="color: #f56565;">❌ Erro ao carregar dados das cidades</div>
        `;
    }
}

// Função para renderizar cidades
function renderCities(cities, weatherData) {
    const container = document.getElementById('cities-container');
    
    if (cities.length === 0) {
        container.innerHTML = '<div>Nenhuma cidade encontrada</div>';
        return;
    }

    const citiesHTML = cities.map(city => {
        const cityWeather = weatherData.find(w => w.name === city.name);
        
        return `
            <div class="city-card">
                <div class="city-name">${city.name}</div>
                <div style="color: #666; margin-bottom: 10px;">Região: ${city.region}</div>
                
                ${cityWeather ? `
                    <div class="weather-info">
                        <div class="weather-item">
                            <span class="weather-icon">🌡️</span>
                            <span>${Math.round(cityWeather.main.temp)}°C</span>
                        </div>
                        <div class="weather-item">
                            <span class="weather-icon">💧</span>
                            <span>${cityWeather.main.humidity}%</span>
                        </div>
                        <div class="weather-item">
                            <span class="weather-icon">🌬️</span>
                            <span>${cityWeather.wind.speed} m/s</span>
                        </div>
                        <div class="weather-item">
                            <span class="weather-icon">☁️</span>
                            <span>${cityWeather.weather[0].description}</span>
                        </div>
                    </div>
                    <button class="btn" onclick="analyzeCity('${city.name}')">
                        🔍 Analisar Condições
                    </button>
                ` : `
                    <div style="color: #666;">Dados não disponíveis</div>
                `}
            </div>
        `;
    }).join('');

    container.innerHTML = `<div class="cities-grid">${citiesHTML}</div>`;
}

// Função para analisar condições de uma cidade
async function analyzeCity(cityName) {
    try {
        const response = await fetch(`${API_BASE}/weather/analyze/${encodeURIComponent(cityName)}`);
        const data = await response.json();
        
        if (data.success) {
            alert(`Análise para ${cityName}:\n\n${data.alerts.length} alertas gerados.\n\nConsulte a seção de alertas para mais detalhes.`);
            fetchAlerts(); // Atualizar alertas
        } else {
            alert(`Erro ao analisar ${cityName}: ${data.error}`);
        }
    } catch (error) {
        alert(`Erro de conexão ao analisar ${cityName}`);
    }
}

// Função para buscar alertas
async function fetchAlerts() {
    try {
        const response = await fetch(`${API_BASE}/alerts`);
        const data = await response.json();
        
        if (data.success) {
            // Resumo dos alertas
            const summary = document.getElementById('alerts-summary');
            summary.innerHTML = `
                <div class="weather-item">
                    <span class="weather-icon">🚨</span>
                    <span>Total: ${data.count}</span>
                </div>
                <div class="weather-item">
                    <span class="weather-icon">🔴</span>
                    <span>Alto: ${data.alerts.filter(a => a.level === 'alto').length}</span>
                </div>
                <div class="weather-item">
                    <span class="weather-icon">🟡</span>
                    <span>Médio: ${data.alerts.filter(a => a.level === 'médio').length}</span>
                </div>
            `;

            // Alertas detalhados
            const detailed = document.getElementById('detailed-alerts');
            if (data.alerts.length === 0) {
                detailed.innerHTML = '<div style="color: #68d391;">✅ Nenhum alerta ativo</div>';
            } else {
                const alertsHTML = data.alerts.map(alert => `
                    <div class="alert ${alert.level === 'alto' ? 'high' : alert.level === 'médio' ? 'medium' : 'low'}">
                        <div style="font-weight: bold; margin-bottom: 5px;">
                            ${alert.city_name} - ${alert.alert_type.replace('_', ' ').toUpperCase()}
                        </div>
                        <div style="margin-bottom: 10px;">${alert.message}</div>
                        <div style="font-style: italic; color: #666;">
                            💡 ${alert.recommendation}
                        </div>
                        <div style="margin-top: 10px;">
                            <button class="btn" onclick="acknowledgeAlert(${alert.id})">✅ Reconhecer</button>
                        </div>
                    </div>
                `).join('');
                detailed.innerHTML = alertsHTML;
            }
        }
    } catch (error) {
        document.getElementById('alerts-summary').innerHTML = `
            <div style="color: #f56565;">❌ Erro ao carregar alertas</div>
        `;
    }
}

// Função para reconhecer alerta
async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            alert('Alerta reconhecido com sucesso!');
            fetchAlerts(); // Recarregar alertas
        } else {
            alert('Erro ao reconhecer alerta');
        }
    } catch (error) {
        alert('Erro de conexão');
    }
}

// Inicializar dashboard
async function initDashboard() {
    await Promise.all([
        fetchSystemStatus(),
        fetchCitiesWeather(),
        fetchAlerts()
    ]);
}

// Carregar dados na inicialização
document.addEventListener('DOMContentLoaded', initDashboard);

// Atualizar dados a cada 30 segundos
setInterval(initDashboard, 30000);