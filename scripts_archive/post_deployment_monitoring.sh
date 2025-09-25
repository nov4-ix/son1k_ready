#!/bin/bash
# 📊 Son1kVers3 Post-Deployment Monitoring Setup
# Configurar monitoreo completo después del deployment

set -e

echo "📊 SON1KVERS3 POST-DEPLOYMENT MONITORING SETUP"
echo "=============================================="

DOMAIN="son1kvers3.com"
APP_DIR="/var/www/son1kvers3"
LOG_DIR="/var/log/son1kvers3"

echo ""
echo "📁 [1/6] Setting up enhanced logging..."

# Create comprehensive log structure
sudo mkdir -p $LOG_DIR/{backend,nginx,worker,health,performance}
sudo chown -R $USER:$USER $LOG_DIR

# Enhanced health check script
sudo tee /usr/local/bin/son1k_advanced_health.sh > /dev/null <<'EOF'
#!/bin/bash
DOMAIN="son1kvers3.com"
LOG_FILE="/var/log/son1kvers3/health/detailed.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Test API health
API_HEALTH=$(curl -s -w "%{http_code}" https://$DOMAIN/api/health -o /tmp/health_response.json)
if [ "$API_HEALTH" = "200" ]; then
    echo "[$TIMESTAMP] ✅ API Health: OK" >> $LOG_FILE
else
    echo "[$TIMESTAMP] ❌ API Health: FAILED (HTTP $API_HEALTH)" >> $LOG_FILE
    # Auto-restart on repeated failures
    FAILURES=$(tail -10 $LOG_FILE | grep -c "FAILED" || echo 0)
    if [ "$FAILURES" -gt 2 ]; then
        echo "[$TIMESTAMP] 🔄 Auto-restarting service after $FAILURES failures" >> $LOG_FILE
        sudo systemctl restart son1kvers3
    fi
fi

# Test database connectivity
DB_TEST=$(cd $APP_DIR/backend && source venv/bin/activate && python -c "
try:
    from app.db import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('OK')
except Exception as e:
    print(f'FAILED: {e}')
" 2>/dev/null)

if [ "$DB_TEST" = "OK" ]; then
    echo "[$TIMESTAMP] ✅ Database: OK" >> $LOG_FILE
else
    echo "[$TIMESTAMP] ❌ Database: $DB_TEST" >> $LOG_FILE
fi

# Test worker connectivity
WORKER_COUNT=$(curl -s https://$DOMAIN/api/jobs/pending?worker_id=health-check | grep -o 'job_id\|No jobs' | wc -l)
echo "[$TIMESTAMP] 🤖 Worker endpoint: Responding ($WORKER_COUNT)" >> $LOG_FILE

# System resources
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
DISK_USAGE=$(df -h /var/www/son1kvers3 | tail -1 | awk '{print $5}' | sed 's/%//')

echo "[$TIMESTAMP] 📊 Resources: CPU ${CPU_USAGE}%, RAM ${MEM_USAGE}%, Disk ${DISK_USAGE}%" >> $LOG_FILE

# Alert on high usage
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "[$TIMESTAMP] ⚠️  HIGH CPU USAGE: ${CPU_USAGE}%" >> $LOG_FILE
fi
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "[$TIMESTAMP] ⚠️  HIGH MEMORY USAGE: ${MEM_USAGE}%" >> $LOG_FILE
fi
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$TIMESTAMP] ⚠️  HIGH DISK USAGE: ${DISK_USAGE}%" >> $LOG_FILE
fi
EOF

sudo chmod +x /usr/local/bin/son1k_advanced_health.sh

echo "✅ Enhanced health monitoring configured"

echo ""
echo "⏰ [2/6] Setting up advanced cron jobs..."

# Remove old basic health check
(crontab -l 2>/dev/null | grep -v son1k_health.sh || true) | crontab -

# Add comprehensive monitoring
(crontab -l 2>/dev/null; cat <<'EOF'
# Son1kVers3 Enhanced Monitoring
*/5 * * * * /usr/local/bin/son1k_advanced_health.sh
*/30 * * * * echo "$(date): System heartbeat" >> /var/log/son1kvers3/health/heartbeat.log
0 */6 * * * find /var/log/son1kvers3 -name "*.log" -size +100M -exec truncate -s 50M {} \;
0 3 * * * /usr/local/bin/son1k_backup.sh
EOF
) | crontab -

echo "✅ Advanced cron jobs configured"

echo ""
echo "💾 [3/6] Setting up automated backup system..."

sudo tee /usr/local/bin/son1k_backup.sh > /dev/null <<EOF
#!/bin/bash
# Son1kVers3 Automated Backup
BACKUP_DIR="/backup/son1kvers3"
TIMESTAMP=\$(date '+%Y%m%d_%H%M%S')

# Create backup directory
mkdir -p \$BACKUP_DIR

# Backup database
cp $APP_DIR/backend/son1k_production.db \$BACKUP_DIR/database_\$TIMESTAMP.db

# Backup configuration
tar -czf \$BACKUP_DIR/config_\$TIMESTAMP.tar.gz \
    /etc/nginx/sites-available/son1kvers3.com \
    /etc/systemd/system/son1kvers3.service \
    $APP_DIR/backend/app/settings.py

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "database_*.db" -mtime +7 -delete
find \$BACKUP_DIR -name "config_*.tar.gz" -mtime +7 -delete

echo "\$(date): Backup completed - \$TIMESTAMP" >> /var/log/son1kvers3/health/backup.log
EOF

sudo chmod +x /usr/local/bin/son1k_backup.sh
sudo mkdir -p /backup/son1kvers3

echo "✅ Automated backup system configured"

echo ""
echo "📈 [4/6] Setting up performance monitoring..."

sudo tee /usr/local/bin/son1k_performance.sh > /dev/null <<'EOF'
#!/bin/bash
# Performance monitoring for Son1kVers3
PERF_LOG="/var/log/son1kvers3/performance/metrics.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# API response time
API_TIME=$(curl -s -w "%{time_total}" -o /dev/null https://son1kvers3.com/api/health)
echo "[$TIMESTAMP] API_RESPONSE_TIME: ${API_TIME}s" >> $PERF_LOG

# Active connections
CONNECTIONS=$(netstat -an | grep :8000 | grep ESTABLISHED | wc -l)
echo "[$TIMESTAMP] ACTIVE_CONNECTIONS: $CONNECTIONS" >> $PERF_LOG

# Process info
SON1K_PID=$(pgrep -f "uvicorn app.main:app" || echo "0")
if [ "$SON1K_PID" != "0" ]; then
    CPU_PROC=$(ps -p $SON1K_PID -o %cpu --no-headers 2>/dev/null || echo "0")
    MEM_PROC=$(ps -p $SON1K_PID -o %mem --no-headers 2>/dev/null || echo "0")
    echo "[$TIMESTAMP] PROCESS_CPU: ${CPU_PROC}%" >> $PERF_LOG
    echo "[$TIMESTAMP] PROCESS_MEM: ${MEM_PROC}%" >> $PERF_LOG
else
    echo "[$TIMESTAMP] PROCESS_STATUS: NOT_RUNNING" >> $PERF_LOG
fi

# Log rotation for performance logs
if [ $(wc -l < $PERF_LOG) -gt 10000 ]; then
    tail -5000 $PERF_LOG > ${PERF_LOG}.tmp
    mv ${PERF_LOG}.tmp $PERF_LOG
fi
EOF

sudo chmod +x /usr/local/bin/son1k_performance.sh

# Add performance monitoring to cron
(crontab -l 2>/dev/null; echo "*/10 * * * * /usr/local/bin/son1k_performance.sh") | crontab -

echo "✅ Performance monitoring configured"

echo ""
echo "🚨 [5/6] Setting up alerting system..."

sudo tee /usr/local/bin/son1k_alerts.sh > /dev/null <<'EOF'
#!/bin/bash
# Alert system for Son1kVers3
ALERT_LOG="/var/log/son1kvers3/health/alerts.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Check for recent failures
RECENT_FAILURES=$(grep "$(date '+%Y-%m-%d %H:')" /var/log/son1kvers3/health/detailed.log | grep -c "FAILED" || echo 0)

if [ "$RECENT_FAILURES" -gt 3 ]; then
    echo "[$TIMESTAMP] ALERT: Multiple failures detected ($RECENT_FAILURES in last hour)" >> $ALERT_LOG
    
    # Try to auto-recover
    echo "[$TIMESTAMP] Attempting auto-recovery..." >> $ALERT_LOG
    sudo systemctl restart son1kvers3
    sleep 10
    
    # Test if recovery worked
    if curl -s https://son1kvers3.com/api/health | grep -q '"ok":true'; then
        echo "[$TIMESTAMP] AUTO-RECOVERY: SUCCESS" >> $ALERT_LOG
    else
        echo "[$TIMESTAMP] AUTO-RECOVERY: FAILED - Manual intervention needed" >> $ALERT_LOG
    fi
fi

# Check disk space alert
DISK_USAGE=$(df /var/www/son1kvers3 | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
    echo "[$TIMESTAMP] ALERT: Critical disk usage ${DISK_USAGE}%" >> $ALERT_LOG
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ "$MEM_USAGE" -gt 90 ]; then
    echo "[$TIMESTAMP] ALERT: Critical memory usage ${MEM_USAGE}%" >> $ALERT_LOG
fi
EOF

sudo chmod +x /usr/local/bin/son1k_alerts.sh

# Add alerting to cron
(crontab -l 2>/dev/null; echo "*/15 * * * * /usr/local/bin/son1k_alerts.sh") | crontab -

echo "✅ Alerting system configured"

echo ""
echo "📊 [6/6] Creating monitoring dashboard script..."

sudo tee /usr/local/bin/son1k_dashboard.sh > /dev/null <<'EOF'
#!/bin/bash
# Son1kVers3 Monitoring Dashboard
clear

echo "📊 SON1KVERS3 LIVE MONITORING DASHBOARD"
echo "======================================"
echo "$(date)"
echo ""

# Service Status
echo "🔧 SERVICE STATUS:"
printf "   %-20s %s\n" "son1kvers3:" "$(systemctl is-active son1kvers3)"
printf "   %-20s %s\n" "nginx:" "$(systemctl is-active nginx)"
echo ""

# API Health
echo "🌐 API HEALTH:"
API_RESPONSE=$(curl -s https://son1kvers3.com/api/health 2>/dev/null || echo '{"ok":false}')
if echo "$API_RESPONSE" | grep -q '"ok":true'; then
    echo "   ✅ API Status: HEALTHY"
else
    echo "   ❌ API Status: UNHEALTHY"
fi

API_TIME=$(curl -s -w "%{time_total}" -o /dev/null https://son1kvers3.com/api/health 2>/dev/null || echo "ERROR")
echo "   ⏱️  Response Time: ${API_TIME}s"
echo ""

# System Resources
echo "📊 SYSTEM RESOURCES:"
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_INFO=$(free -h | grep Mem)
MEM_USED=$(echo $MEM_INFO | awk '{print $3}')
MEM_TOTAL=$(echo $MEM_INFO | awk '{print $2}')
DISK_INFO=$(df -h /var/www/son1kvers3 | tail -1)
DISK_USAGE=$(echo $DISK_INFO | awk '{print $5}')
DISK_AVAIL=$(echo $DISK_INFO | awk '{print $4}')

printf "   %-15s %s\n" "CPU Usage:" "${CPU_USAGE}%"
printf "   %-15s %s / %s\n" "Memory:" "$MEM_USED" "$MEM_TOTAL"
printf "   %-15s %s (%s available)\n" "Disk:" "$DISK_USAGE" "$DISK_AVAIL"
echo ""

# Recent Activity
echo "📋 RECENT ACTIVITY (Last 10 entries):"
if [ -f /var/log/son1kvers3/health/detailed.log ]; then
    tail -10 /var/log/son1kvers3/health/detailed.log | while read line; do
        if echo "$line" | grep -q "✅"; then
            echo "   $line"
        elif echo "$line" | grep -q "❌"; then
            echo "   $line"
        else
            echo "   $line"
        fi
    done
else
    echo "   No activity logs found"
fi
echo ""

# Active Connections
CONNECTIONS=$(netstat -an | grep :8000 | grep ESTABLISHED | wc -l 2>/dev/null || echo "0")
echo "🔗 ACTIVE CONNECTIONS: $CONNECTIONS"
echo ""

# Quick Stats
if [ -f /var/log/son1kvers3/health/detailed.log ]; then
    TODAY_SUCCESSES=$(grep "$(date '+%Y-%m-%d')" /var/log/son1kvers3/health/detailed.log | grep -c "✅" || echo "0")
    TODAY_FAILURES=$(grep "$(date '+%Y-%m-%d')" /var/log/son1kvers3/health/detailed.log | grep -c "❌" || echo "0")
    echo "📈 TODAY'S STATS:"
    echo "   ✅ Successful checks: $TODAY_SUCCESSES"
    echo "   ❌ Failed checks: $TODAY_FAILURES"
    echo ""
fi

echo "🎯 USEFUL COMMANDS:"
echo "   sudo journalctl -u son1kvers3 -f     # Live logs"
echo "   sudo systemctl restart son1kvers3    # Restart service"
echo "   curl https://son1kvers3.com/api/health # Test API"
echo "   ./son1k_dashboard.sh                  # Refresh dashboard"
EOF

sudo chmod +x /usr/local/bin/son1k_dashboard.sh

echo "✅ Monitoring dashboard configured"

echo ""
echo "🎉 POST-DEPLOYMENT MONITORING SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "📊 Monitoring Features Configured:"
echo "   ✅ Enhanced health checks (every 5 minutes)"
echo "   ✅ Performance monitoring (every 10 minutes)"
echo "   ✅ Automated alerting (every 15 minutes)"
echo "   ✅ Auto-recovery on failures"
echo "   ✅ Daily automated backups"
echo "   ✅ Log rotation and cleanup"
echo "   ✅ Real-time dashboard"
echo ""
echo "📁 Log Locations:"
echo "   📊 Main logs: /var/log/son1kvers3/"
echo "   🔍 Health logs: /var/log/son1kvers3/health/"
echo "   📈 Performance: /var/log/son1kvers3/performance/"
echo "   💾 Backups: /backup/son1kvers3/"
echo ""
echo "🎛️ Monitoring Commands:"
echo "   sudo /usr/local/bin/son1k_dashboard.sh    # Live dashboard"
echo "   tail -f /var/log/son1kvers3/health/detailed.log # Live health"
echo "   crontab -l                                # View all cron jobs"
echo ""
echo "🚀 Son1kVers3 monitoring is now enterprise-grade!"

# Run initial dashboard
echo ""
echo "🔄 Running initial dashboard..."
sleep 2
sudo /usr/local/bin/son1k_dashboard.sh