// Configuración de producción para Son1k
window.SON1K_CONFIG = {
    API_BASE_URL: 'https://api.son1kvers3.com',
    DOMAIN: 'son1kvers3.com',
    ENVIRONMENT: 'production',
    VERSION: '3.0.0',
    FEATURES: {
        TRANSPARENT_GENERATION: true,
        DYNAMIC_NAMING: true,
        REAL_TIME_UPDATES: true
    }
};

console.log('🎵 Son1k Production Config Loaded');
console.log('🌐 API:', window.SON1K_CONFIG.API_BASE_URL);
console.log('✅ Transparent Generation Enabled');
