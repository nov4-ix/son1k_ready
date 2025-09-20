# Configuración DNS en IONOS para son1kvers3.com

## Credenciales
- Dominio: son1kvers3.com
- Usuario: (usar el dominio)
- Contraseña: iloveMusic!90

## Pasos en el panel IONOS:

1. **Acceder al panel**:
   - URL: https://www.ionos.com/
   - Login con credenciales del dominio

2. **Configurar registros DNS**:
   ```
   # Registro A principal
   @ (root)          A    [IP_DEL_SERVIDOR]
   
   # Subdominios
   www              A    [IP_DEL_SERVIDOR]
   api              A    [IP_DEL_SERVIDOR]
   
   # Opcional: CDN
   cdn              CNAME son1kvers3.com
   ```

3. **Verificar propagación**:
   ```bash
   dig son1kvers3.com
   dig api.son1kvers3.com
   ```

## Después de configurar DNS:

1. **SSL con Let's Encrypt**:
   ```bash
   certbot --nginx -d son1kvers3.com -d www.son1kvers3.com -d api.son1kvers3.com
   ```

2. **Verificar servicios**:
   - Frontend: https://son1kvers3.com
   - API: https://api.son1kvers3.com/docs
   - Health: https://api.son1kvers3.com/health
