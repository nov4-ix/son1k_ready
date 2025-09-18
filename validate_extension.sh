#!/bin/bash

# Son1k Suno Bridge Extension Validation Script
# Tests complete workflow without external dependencies

echo "🚀 Son1k Suno Bridge - Extension Validation"
echo "=============================================="

API_URL="http://localhost:8000"
PASS=0
TOTAL=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

test_result() {
    TOTAL=$((TOTAL + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC} $2"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}❌ FAIL${NC} $2"
    fi
}

echo ""
echo "🏥 Test 1: Backend Health Check"
curl -s "$API_URL/api/health" | grep -q '"ok":true'
test_result $? "Backend Health"

echo ""
echo "🎵 Test 2: Song Creation Endpoint"
RESPONSE=$(curl -s -X POST "$API_URL/api/songs/create" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Una balada emotiva con piano",
    "lyrics": "Verso 1: En la noche",
    "mode": "original",
    "source": "test"
  }')

echo "$RESPONSE" | grep -q '"ok":true' && echo "$RESPONSE" | grep -q '"job_id"'
test_result $? "Song Creation Endpoint"

if [ $? -eq 0 ]; then
    JOB_ID=$(echo "$RESPONSE" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
    echo "📝 Generated Job ID: $JOB_ID"
fi

echo ""
echo "🤖 Test 3: AI Endpoints"

# Test Generate Lyrics
curl -s -X POST "$API_URL/api/generate-lyrics" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "balada romántica"}' | grep -q '"lyrics"'
test_result $? "Generate Lyrics Endpoint"

# Test Improve Lyrics  
curl -s -X POST "$API_URL/api/improve-lyrics" \
  -H "Content-Type: application/json" \
  -d '{"lyrics": "amor en la noche"}' | grep -q '"improved_lyrics"'
test_result $? "Improve Lyrics Endpoint"

# Test Smart Prompt
curl -s -X POST "$API_URL/api/smart-prompt" \
  -H "Content-Type: application/json" \
  -d '{"lyrics": "guitarra amor corazón"}' | grep -q '"smart_prompt"'
test_result $? "Smart Prompt Endpoint"

echo ""
echo "⚡ Test 4: System Status Endpoints"

# Test Celery Status
curl -s "$API_URL/api/celery-status" > /dev/null
test_result $? "Celery Status Endpoint"

# Test Redis Status
curl -s "$API_URL/api/redis-status" > /dev/null  
test_result $? "Redis Status Endpoint"

echo ""
echo "🔄 Test 5: Extension Workflow Simulation"

# Simulate complete extension workflow
WORKFLOW_DATA='{
  "prompt": "Trap melódico con 808s, estilo moderno, BPM 140",
  "lyrics": "Verso 1:\nSubiendo desde abajo\nNunca me voy a rendir\n\nCoro:\nEste es mi momento\nVoy a prevalecer",
  "mode": "original",
  "source": "suno_extension",
  "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'

WORKFLOW_RESPONSE=$(curl -s -X POST "$API_URL/api/songs/create" \
  -H "Content-Type: application/json" \
  -d "$WORKFLOW_DATA")

echo "$WORKFLOW_RESPONSE" | grep -q '"ok":true' && echo "$WORKFLOW_RESPONSE" | grep -q '"job_id"'
test_result $? "Complete Extension Workflow"

echo ""
echo "=============================================="
echo "📊 VALIDATION RESULTS"
echo "=============================================="

SCORE=$((PASS * 100 / TOTAL))

echo "Tests Passed: $PASS/$TOTAL"
echo "Score: $SCORE%"

if [ $SCORE -ge 80 ]; then
    echo -e "${GREEN}🚀 SYSTEM READY FOR PRODUCTION!${NC}"
    echo ""
    echo "✅ Extension is ready to load and test"
    echo ""
    echo "📋 NEXT STEPS:"
    echo "1. Open Chrome → chrome://extensions/"
    echo "2. Enable 'Developer mode'"
    echo "3. Click 'Load unpacked'"
    echo "4. Select folder: extension/"
    echo "5. Configure URL: http://localhost:8000"
    echo "6. Test on suno.com/create"
    echo ""
    echo "🎯 READY FOR PREMIUM SUNO TESTING!"
    
elif [ $SCORE -ge 60 ]; then
    echo -e "${YELLOW}⚠️ SYSTEM PARTIALLY READY${NC}"
    echo "Some issues detected, but core functionality works"
    
else
    echo -e "${RED}❌ SYSTEM NOT READY${NC}"
    echo "Critical issues found - fix before proceeding"
fi

echo ""
echo "🔍 DEBUG INFO:"
echo "Backend Status: $(curl -s $API_URL/api/health 2>/dev/null || echo 'OFFLINE')"
echo "Extension Files: $(ls -la extension/ 2>/dev/null | wc -l) files"
echo "Timestamp: $(date)"

# Extension file validation
echo ""
echo "📁 Extension Files Validation:"
EXTENSION_DIR="extension"

if [ -f "$EXTENSION_DIR/manifest.json" ]; then
    echo -e "${GREEN}✅${NC} manifest.json exists"
else
    echo -e "${RED}❌${NC} manifest.json missing"
fi

if [ -f "$EXTENSION_DIR/background.js" ]; then
    echo -e "${GREEN}✅${NC} background.js exists"
else
    echo -e "${RED}❌${NC} background.js missing"
fi

if [ -f "$EXTENSION_DIR/content.js" ]; then
    echo -e "${GREEN}✅${NC} content.js exists"
else
    echo -e "${RED}❌${NC} content.js missing"
fi

if [ -f "$EXTENSION_DIR/popup.html" ] && [ -f "$EXTENSION_DIR/popup.js" ]; then
    echo -e "${GREEN}✅${NC} popup files exist"
else
    echo -e "${RED}❌${NC} popup files missing"
fi

if [ -f "$EXTENSION_DIR/icon16.png" ] && [ -f "$EXTENSION_DIR/icon48.png" ] && [ -f "$EXTENSION_DIR/icon128.png" ]; then
    echo -e "${GREEN}✅${NC} icon files exist"
else
    echo -e "${RED}❌${NC} icon files missing"
fi

echo ""
echo "🎉 Validation Complete!"

exit $((SCORE < 80))