/**
 * Son1k Consent Banner
 * Manejo de cookies y consentimientos GDPR/CCPA
 */

(function() {
    'use strict';

    // Configuración del banner
    const CONSENT_CONFIG = {
        cookieName: 'son1k_consent',
        cookieExpiry: 365, // días
        apiBase: '/api/legal',
        requiredConsents: ['essential', 'functional'],
        optionalConsents: ['analytics', 'marketing']
    };

    // Estado de consentimientos
    let currentConsents = {
        essential: true,     // Siempre true, no se puede deshabilitar
        functional: true,    // Siempre true, necesario para el servicio
        analytics: false,    // Opcional
        marketing: false     // Opcional
    };

    // Verificar si ya hay consentimiento guardado
    function checkExistingConsent() {
        const consent = getCookie(CONSENT_CONFIG.cookieName);
        if (consent) {
            try {
                const parsed = JSON.parse(consent);
                currentConsents = { ...currentConsents, ...parsed };
                return true;
            } catch (e) {
                console.warn('Error parsing consent cookie:', e);
            }
        }
        return false;
    }

    // Mostrar banner de consentimiento
    function showConsentBanner() {
        if (checkExistingConsent()) {
            initializeServices();
            return;
        }

        const banner = createConsentBanner();
        document.body.appendChild(banner);
        
        // Mostrar banner con animación
        setTimeout(() => {
            banner.classList.add('show');
        }, 100);
    }

    // Crear HTML del banner
    function createConsentBanner() {
        const banner = document.createElement('div');
        banner.id = 'son1k-consent-banner';
        banner.innerHTML = `
            <div class="consent-content">
                <div class="consent-header">
                    <h3>🍪 Gestión de Cookies</h3>
                    <p>Utilizamos cookies para mejorar tu experiencia. Puedes personalizar tus preferencias a continuación.</p>
                </div>
                
                <div class="consent-options">
                    <div class="consent-group">
                        <div class="consent-item">
                            <label class="consent-label">
                                <input type="checkbox" id="consent-essential" checked disabled>
                                <span class="consent-name">Esenciales</span>
                                <span class="consent-required">(Requeridas)</span>
                            </label>
                            <p class="consent-description">Cookies necesarias para el funcionamiento básico del sitio.</p>
                        </div>
                        
                        <div class="consent-item">
                            <label class="consent-label">
                                <input type="checkbox" id="consent-functional" checked disabled>
                                <span class="consent-name">Funcionales</span>
                                <span class="consent-required">(Requeridas)</span>
                            </label>
                            <p class="consent-description">Mantienen tu sesión y preferencias del sitio.</p>
                        </div>
                        
                        <div class="consent-item">
                            <label class="consent-label">
                                <input type="checkbox" id="consent-analytics">
                                <span class="consent-name">Analytics</span>
                                <span class="consent-optional">(Opcional)</span>
                            </label>
                            <p class="consent-description">Nos ayudan a mejorar el servicio analizando el uso.</p>
                        </div>
                        
                        <div class="consent-item">
                            <label class="consent-label">
                                <input type="checkbox" id="consent-marketing">
                                <span class="consent-name">Marketing</span>
                                <span class="consent-optional">(Opcional)</span>
                            </label>
                            <p class="consent-description">Personalizan anuncios y comunicaciones.</p>
                        </div>
                    </div>
                </div>
                
                <div class="consent-actions">
                    <button id="consent-accept-all" class="consent-btn consent-btn-primary">
                        Aceptar Todo
                    </button>
                    <button id="consent-accept-selected" class="consent-btn consent-btn-secondary">
                        Aceptar Seleccionados
                    </button>
                    <button id="consent-reject-optional" class="consent-btn consent-btn-minimal">
                        Solo Esenciales
                    </button>
                </div>
                
                <div class="consent-footer">
                    <p>
                        <a href="/privacy" target="_blank">Política de Privacidad</a> | 
                        <a href="/terms" target="_blank">Términos y Condiciones</a>
                    </p>
                </div>
            </div>
        `;

        // Añadir estilos
        addConsentStyles();
        
        // Añadir event listeners
        setTimeout(() => {
            setupEventListeners(banner);
        }, 100);

        return banner;
    }

    // Añadir estilos CSS
    function addConsentStyles() {
        if (document.getElementById('son1k-consent-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'son1k-consent-styles';
        styles.textContent = `
            #son1k-consent-banner {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.95);
                backdrop-filter: blur(10px);
                color: white;
                padding: 0;
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                transform: translateY(100%);
                transition: transform 0.3s ease;
                max-height: 80vh;
                overflow-y: auto;
            }
            
            #son1k-consent-banner.show {
                transform: translateY(0);
            }
            
            .consent-content {
                max-width: 800px;
                margin: 0 auto;
                padding: 30px 20px;
            }
            
            .consent-header h3 {
                margin: 0 0 10px 0;
                font-size: 1.3rem;
                color: #ffd700;
            }
            
            .consent-header p {
                margin: 0 0 25px 0;
                opacity: 0.9;
                line-height: 1.5;
            }
            
            .consent-options {
                margin-bottom: 25px;
            }
            
            .consent-group {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
            }
            
            .consent-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .consent-label {
                display: flex;
                align-items: center;
                gap: 10px;
                cursor: pointer;
                font-weight: 600;
                margin-bottom: 8px;
            }
            
            .consent-label input {
                width: 18px;
                height: 18px;
                accent-color: #ffd700;
            }
            
            .consent-required {
                color: #ff6b6b;
                font-size: 12px;
                font-weight: normal;
            }
            
            .consent-optional {
                color: #3498db;
                font-size: 12px;
                font-weight: normal;
            }
            
            .consent-description {
                font-size: 13px;
                opacity: 0.8;
                margin: 0;
                line-height: 1.4;
            }
            
            .consent-actions {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }
            
            .consent-btn {
                padding: 12px 24px;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 14px;
            }
            
            .consent-btn-primary {
                background: linear-gradient(45deg, #ff6b6b, #ffd700);
                color: white;
            }
            
            .consent-btn-secondary {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            
            .consent-btn-minimal {
                background: transparent;
                color: #ccc;
                border: 1px solid #666;
            }
            
            .consent-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }
            
            .consent-footer {
                text-align: center;
                opacity: 0.7;
                font-size: 12px;
            }
            
            .consent-footer a {
                color: #ffd700;
                text-decoration: none;
            }
            
            .consent-footer a:hover {
                text-decoration: underline;
            }
            
            @media (max-width: 768px) {
                .consent-content {
                    padding: 20px 15px;
                }
                
                .consent-group {
                    grid-template-columns: 1fr;
                }
                
                .consent-actions {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .consent-btn {
                    width: 100%;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }

    // Configurar event listeners
    function setupEventListeners(banner) {
        const acceptAllBtn = banner.querySelector('#consent-accept-all');
        const acceptSelectedBtn = banner.querySelector('#consent-accept-selected');
        const rejectOptionalBtn = banner.querySelector('#consent-reject-optional');

        acceptAllBtn.addEventListener('click', () => {
            currentConsents = {
                essential: true,
                functional: true,
                analytics: true,
                marketing: true
            };
            saveConsent();
            hideBanner(banner);
            initializeServices();
        });

        acceptSelectedBtn.addEventListener('click', () => {
            currentConsents = {
                essential: true,
                functional: true,
                analytics: banner.querySelector('#consent-analytics').checked,
                marketing: banner.querySelector('#consent-marketing').checked
            };
            saveConsent();
            hideBanner(banner);
            initializeServices();
        });

        rejectOptionalBtn.addEventListener('click', () => {
            currentConsents = {
                essential: true,
                functional: true,
                analytics: false,
                marketing: false
            };
            saveConsent();
            hideBanner(banner);
            initializeServices();
        });
    }

    // Guardar consentimiento
    function saveConsent() {
        const consentData = {
            ...currentConsents,
            timestamp: new Date().toISOString(),
            version: '1.0'
        };

        setCookie(CONSENT_CONFIG.cookieName, JSON.stringify(consentData), CONSENT_CONFIG.cookieExpiry);
        
        // Registrar en el backend si hay usuario logueado
        const userId = getCurrentUserId();
        if (userId) {
            fetch('/api/legal/consent/privacy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    marketing_consent: currentConsents.marketing,
                    analytics_consent: currentConsents.analytics
                })
            }).catch(err => console.warn('Error saving consent to backend:', err));
        }
    }

    // Ocultar banner
    function hideBanner(banner) {
        banner.classList.remove('show');
        setTimeout(() => {
            banner.remove();
        }, 300);
    }

    // Inicializar servicios según consentimientos
    function initializeServices() {
        if (currentConsents.analytics) {
            initializeAnalytics();
        }

        if (currentConsents.marketing) {
            initializeMarketing();
        }

        // Disparar evento personalizado
        window.dispatchEvent(new CustomEvent('son1kConsentUpdated', {
            detail: currentConsents
        }));
    }

    // Inicializar Google Analytics (ejemplo)
    function initializeAnalytics() {
        if (window.gtag) return; // Ya inicializado

        // Google Analytics 4
        const script = document.createElement('script');
        script.async = true;
        script.src = 'https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX';
        document.head.appendChild(script);

        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        window.gtag = gtag;
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXXX', {
            anonymize_ip: true,
            cookie_expires: 63072000, // 2 años
        });

        console.log('📊 Analytics inicializado');
    }

    // Inicializar marketing (ejemplo)
    function initializeMarketing() {
        // Facebook Pixel, etc.
        console.log('📢 Marketing inicializado');
    }

    // Utilidades para cookies
    function setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    }

    function getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    // Obtener ID del usuario actual (implementar según tu sistema)
    function getCurrentUserId() {
        // Implementar lógica para obtener user ID
        // Podría venir del localStorage, sessionStorage, JWT, etc.
        return localStorage.getItem('son1k_user_id') || null;
    }

    // API pública para cambiar consentimientos
    window.Son1kConsent = {
        show: showConsentBanner,
        
        getConsents: () => currentConsents,
        
        updateConsent: (type, value) => {
            if (type in currentConsents && type !== 'essential' && type !== 'functional') {
                currentConsents[type] = value;
                saveConsent();
                initializeServices();
            }
        },
        
        revokeAll: () => {
            currentConsents = {
                essential: true,
                functional: true,
                analytics: false,
                marketing: false
            };
            saveConsent();
            // Recargar página para aplicar cambios
            window.location.reload();
        }
    };

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', showConsentBanner);
    } else {
        showConsentBanner();
    }

})();