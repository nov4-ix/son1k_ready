#!/bin/bash
# 🔍 Son1kVers3 Production Verification Script
# Ejecutar DESPUÉS del deployment para verificar que todo funciona

set -e

echo "🔍 SON1KVERS3 PRODUCTION VERIFICATION"
echo "===================================="

DOMAIN="son1kvers3.com"
API_URL="https://$DOMAIN"

echo ""
echo "🌐 [1/8] Testing domain resolution..."
if dig +short $DOMAIN | grep -q '^[0-9]'; then
    echo "✅ DNS resolution working"
    IP=$(dig +short $DOMAIN)
    echo "   IP: $IP"
else
    echo "❌ DNS not resolved yet - check propagation"
    echo "   Visit: https://dnschecker.org/"
fi

echo ""
echo "🔒 [2/8] Testing SSL certificate..."
if curl -s -I https://$DOMAIN | grep -q "HTTP/2 200\|HTTP/1.1 200"; then
    echo "✅ SSL certificate working"
    echo "   HTTPS accessible"
else
    echo "❌ SSL certificate issue"
    echo "   Check: sudo certbot certificates"
fi

echo ""
echo "🔧 [3/8] Testing API health endpoint..."
HEALTH_RESPONSE=$(curl -s $API_URL/api/health || echo "ERROR")
if echo "$HEALTH_RESPONSE" | grep -q '"ok":true'; then
    echo "✅ API health check passed"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "❌ API health check failed"
    echo "   Response: $HEALTH_RESPONSE"
    echo "   Check: sudo systemctl status son1kvers3"
fi

echo ""
echo "👤 [4/8] Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST $API_URL/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test-'$(date +%s)'@son1k.com","password":"test123","name":"Test User"}' || echo "ERROR")

if echo "$REGISTER_RESPONSE" | grep -q '"access_token"'; then
    echo "✅ User registration working"
    TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "   Token generated successfully"
else
    echo "❌ User registration failed"
    echo "   Response: $REGISTER_RESPONSE"
fi

echo ""
echo "🔑 [5/8] Testing authentication endpoint..."
if [ ! -z "$TOKEN" ]; then
    AUTH_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" $API_URL/api/auth/me || echo "ERROR")
    if echo "$AUTH_RESPONSE" | grep -q '"email"'; then
        echo "✅ Authentication working"
        echo "   User data retrieved successfully"
    else
        echo "❌ Authentication failed"
        echo "   Response: $AUTH_RESPONSE"
    fi
else
    echo "⏭️  Skipping authentication test (no token)"
fi

echo ""
echo "🎵 [6/8] Testing song creation endpoint..."
if [ ! -z "$TOKEN" ]; then
    SONG_RESPONSE=$(curl -s -X POST $API_URL/api/songs/create \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{"prompt":"Test song","lyrics":"Test lyrics","mode":"original"}' || echo "ERROR")
    
    if echo "$SONG_RESPONSE" | grep -q '"id"\|"success"'; then
        echo "✅ Song creation working"
        echo "   Job queued successfully"
    else
        echo "❌ Song creation failed"
        echo "   Response: $SONG_RESPONSE"
    fi
else
    echo "⏭️  Skipping song creation test (no token)"
fi

echo ""
echo "🤖 [7/8] Testing worker endpoints..."
WORKER_RESPONSE=$(curl -s $API_URL/api/jobs/pending?worker_id=test-worker || echo "ERROR")
if echo "$WORKER_RESPONSE" | grep -q 'job_id\|No jobs'; then
    echo "✅ Worker endpoints working"
    echo "   Job polling functional"
else
    echo "❌ Worker endpoints failed"
    echo "   Response: $WORKER_RESPONSE"
fi

echo ""
echo "📊 [8/8] System health summary..."

# Check system services
echo "🔧 System Services:"
if systemctl is-active --quiet son1kvers3; then
    echo "   ✅ son1kvers3 service: ACTIVE"
else
    echo "   ❌ son1kvers3 service: INACTIVE"
fi

if systemctl is-active --quiet nginx; then
    echo "   ✅ nginx service: ACTIVE"
else
    echo "   ❌ nginx service: INACTIVE"
fi

# Check ports
echo "🌐 Network Ports:"
if netstat -tln | grep -q ":8000"; then
    echo "   ✅ Backend port 8000: LISTENING"
else
    echo "   ❌ Backend port 8000: NOT LISTENING"
fi

if netstat -tln | grep -q ":80\|:443"; then
    echo "   ✅ Web ports 80/443: LISTENING"
else
    echo "   ❌ Web ports 80/443: NOT LISTENING"
fi

# Check disk space
echo "💾 Disk Usage:"
DISK_USAGE=$(df -h /var/www/son1kvers3 | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "   ✅ Disk space: ${DISK_USAGE}% used"
else
    echo "   ⚠️  Disk space: ${DISK_USAGE}% used (consider cleanup)"
fi

echo ""
echo "🎯 VERIFICATION SUMMARY"
echo "======================"
echo ""
echo "🌐 Frontend: https://$DOMAIN"
echo "🔧 API Health: $API_URL/api/health"
echo "📊 System Status: $(systemctl is-active son1kvers3)"
echo ""

# Final recommendation
if curl -s $API_URL/api/health | grep -q '"ok":true'; then
    echo "🎉 SUCCESS: Son1kVers3 is LIVE and ready for production!"
    echo ""
    echo "✅ Next steps:"
    echo "   1. Test Chrome extension connection"
    echo "   2. Register real user accounts"
    echo "   3. Generate first songs"
    echo "   4. Monitor logs: sudo journalctl -u son1kvers3 -f"
    echo ""
    echo "🚀 Son1kVers3 is ready to serve customers!"
else
    echo "❌ ISSUES DETECTED: Some components need attention"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check logs: sudo journalctl -u son1kvers3 -f"
    echo "   2. Restart service: sudo systemctl restart son1kvers3"
    echo "   3. Check nginx: sudo nginx -t"
    echo "   4. Verify DNS: dig $DOMAIN"
fi

echo ""
echo "📋 Useful commands:"
echo "   sudo systemctl status son1kvers3    # Check service"
echo "   sudo journalctl -u son1kvers3 -f    # View logs"
echo "   sudo systemctl restart son1kvers3   # Restart"
echo "   sudo nginx -t && sudo systemctl reload nginx  # Reload nginx"
echo "   curl $API_URL/api/health            # Test API"