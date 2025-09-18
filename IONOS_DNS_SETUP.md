# 🌐 IONOS DNS Configuration for son1kvers3.com

## 📋 STEP-BY-STEP DNS SETUP

### 1. Access IONOS Control Panel
1. Go to https://www.ionos.com/
2. Login with your credentials (password: iloveMusic!90)
3. Navigate to **Domains & SSL** → **Domains**
4. Click on **son1kvers3.com**

### 2. Configure DNS Records

#### Required A Records:
```
Record Type: A
Name: @               (root domain)
Value: [YOUR_VPS_IP]
TTL: 3600

Record Type: A  
Name: www
Value: [YOUR_VPS_IP]
TTL: 3600
```

#### Alternative CNAME Setup:
```
Record Type: A
Name: @
Value: [YOUR_VPS_IP]
TTL: 3600

Record Type: CNAME
Name: www
Value: son1kvers3.com
TTL: 3600
```

### 3. Get Your VPS IP Address

Once you have your IONOS VPS running, get the IP with:
```bash
# On your VPS
curl -s ifconfig.me
# or
ip addr show
```

### 4. DNS Propagation

- **Propagation Time**: 24-48 hours (typically 2-6 hours)
- **Check Status**: Use https://dnschecker.org/
- **Test Command**: `nslookup son1kvers3.com`

### 5. Verify DNS Configuration

```bash
# Test A record
dig son1kvers3.com A

# Test www subdomain  
dig www.son1kvers3.com A

# Test from different locations
nslookup son1kvers3.com 8.8.8.8
```

## 🚀 NEXT STEPS AFTER DNS

1. **Wait for propagation** (check with dnschecker.org)
2. **Deploy to VPS** using deploy_production.sh
3. **SSL Certificate** will be automatic with Let's Encrypt
4. **Test endpoints**:
   - https://son1kvers3.com/api/health
   - https://son1kvers3.com (frontend)

## 🔧 IONOS Control Panel Path

1. **Login** → https://www.ionos.com/
2. **Domains** → Domains & SSL
3. **son1kvers3.com** → DNS Management
4. **Add Records** → Configure A/CNAME records
5. **Save Changes** → Wait for propagation

## ⚡ Quick Test Commands

```bash
# Test when DNS is ready
curl -I https://son1kvers3.com
curl https://son1kvers3.com/api/health

# Check SSL certificate
openssl s_client -connect son1kvers3.com:443 -servername son1kvers3.com
```

## 📊 Expected Timeline

- **DNS Setup**: 5 minutes
- **DNS Propagation**: 2-6 hours  
- **VPS Deployment**: 15 minutes
- **SSL Certificate**: Automatic
- **Total**: ~3-7 hours (mostly waiting)

## 🎯 Final Result

✅ https://son1kvers3.com → Production platform
✅ https://www.son1kvers3.com → Redirects to main
✅ SSL certificate active
✅ Backend API responding
✅ Chrome extension connected