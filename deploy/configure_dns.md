# 🌐 Configuración DNS para son1kvers3.com

## Registros DNS a configurar en IONOS:

### Registros A (IPv4):
```
Tipo: A
Nombre: @
Valor: [IP_DEL_SERVIDOR]
TTL: 3600

Tipo: A  
Nombre: www
Valor: [IP_DEL_SERVIDOR]
TTL: 3600

Tipo: A
Nombre: api
Valor: [IP_DEL_SERVIDOR]  
TTL: 3600
```

### Registro CNAME (Alias):
```
Tipo: CNAME
Nombre: app
Valor: son1kvers3.com
TTL: 3600
```

## URLs finales:
- Frontend: https://son1kvers3.com
- API: https://api.son1kvers3.com
- Documentación: https://api.son1kvers3.com/docs
- Health: https://api.son1kvers3.com/health

## Verificación:
```bash
# Verificar DNS
dig son1kvers3.com
dig www.son1kvers3.com
dig api.son1kvers3.com

# Test de conectividad
curl https://son1kvers3.com
curl https://api.son1kvers3.com/health
```
