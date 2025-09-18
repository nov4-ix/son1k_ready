#!/usr/bin/env node

/**
 * Test Worker Automation - Son1k Suno Bridge
 * 
 * Este script simula el comportamiento del worker automático de la extensión
 * para probar el sistema de polling y procesamiento automático de jobs.
 */

const https = require('https');
const http = require('http');

const API_BASE = 'http://localhost:8000';
const WORKER_ID = 'test-worker-automation-' + Date.now();

// Simular el comportamiento del worker
class WorkerSimulator {
  constructor() {
    this.status = 'offline';
    this.currentJobId = null;
    this.jobsCompleted = 0;
    this.jobsFailed = 0;
    this.pollingInterval = null;
    this.heartbeatInterval = null;
  }

  async start() {
    console.log(`🤖 Starting worker simulation - ID: ${WORKER_ID}`);
    this.status = 'online';
    
    // Start polling
    this.pollingInterval = setInterval(() => this.pollForJobs(), 10000);
    
    // Start heartbeat
    this.heartbeatInterval = setInterval(() => this.sendHeartbeat(), 30000);
    
    // Send initial heartbeat
    await this.sendHeartbeat();
    
    console.log('✅ Worker simulation started');
    console.log('🔄 Polling for jobs every 10 seconds...');
  }

  async stop() {
    console.log('🛑 Stopping worker simulation...');
    this.status = 'offline';
    
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
    
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    
    console.log('❌ Worker simulation stopped');
  }

  async pollForJobs() {
    if (this.status === 'busy') {
      console.log('⏳ Worker busy, skipping poll...');
      return;
    }

    try {
      console.log('🔍 Polling for jobs...');
      const job = await this.makeRequest('GET', `/api/worker/jobs/next?worker_id=${WORKER_ID}`);
      
      if (job.job_id) {
        console.log('📋 New job received:', job);
        await this.processJob(job);
      } else {
        console.log('💤 No jobs available');
      }
    } catch (error) {
      console.error('❌ Error polling jobs:', error.message);
    }
  }

  async processJob(job) {
    try {
      this.status = 'busy';
      this.currentJobId = job.job_id;
      
      console.log(`🎵 Processing job ${job.job_id}...`);
      console.log(`   Prompt: ${job.prompt}`);
      console.log(`   Mode: ${job.mode}`);
      console.log(`   Timeout: ${job.timeout_at}`);
      
      // Update to processing
      await this.updateJobStatus(job.job_id, 'processing');
      
      // Simulate processing time (10-15 seconds)
      const processingTime = 10000 + Math.random() * 5000;
      console.log(`⏳ Simulating processing for ${Math.round(processingTime/1000)} seconds...`);
      
      await new Promise(resolve => setTimeout(resolve, processingTime));
      
      // Simulate success/failure (90% success rate)
      const success = Math.random() > 0.1;
      
      if (success) {
        // Complete successfully
        await this.updateJobStatus(job.job_id, 'completed', {
          audio_url: `https://example.com/audio/${job.job_id}.mp3`,
          preview_url: `https://example.com/preview/${job.job_id}.mp3`
        });
        
        this.jobsCompleted++;
        console.log(`✅ Job ${job.job_id} completed successfully!`);
      } else {
        // Fail
        await this.updateJobStatus(job.job_id, 'failed', {
          error_message: 'Simulated processing error'
        });
        
        this.jobsFailed++;
        console.log(`❌ Job ${job.job_id} failed`);
      }
      
    } catch (error) {
      console.error(`❌ Error processing job ${job.job_id}:`, error.message);
      this.jobsFailed++;
    } finally {
      this.status = 'online';
      this.currentJobId = null;
    }
  }

  async updateJobStatus(jobId, status, extraData = {}) {
    try {
      await this.makeRequest('POST', `/api/jobs/${jobId}/update`, {
        status,
        ...extraData
      });
      console.log(`📝 Job ${jobId} status updated to: ${status}`);
    } catch (error) {
      console.error(`❌ Error updating job status:`, error.message);
    }
  }

  async sendHeartbeat() {
    try {
      await this.makeRequest('POST', '/api/worker/heartbeat', {
        worker_id: WORKER_ID,
        status: this.status,
        version: '2.0.0-simulator',
        current_job_id: this.currentJobId,
        jobs_completed: this.jobsCompleted,
        jobs_failed: this.jobsFailed
      });
      
      console.log(`💓 Heartbeat sent - Status: ${this.status} | Completed: ${this.jobsCompleted} | Failed: ${this.jobsFailed}`);
    } catch (error) {
      console.error('❌ Error sending heartbeat:', error.message);
    }
  }

  makeRequest(method, path, data = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(API_BASE + path);
      
      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        method: method,
        headers: {
          'Content-Type': 'application/json'
        }
      };

      const req = http.request(options, (res) => {
        let body = '';
        
        res.on('data', (chunk) => {
          body += chunk;
        });
        
        res.on('end', () => {
          try {
            const response = body ? JSON.parse(body) : {};
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(response);
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${response.error || body}`));
            }
          } catch (error) {
            reject(new Error(`Parse error: ${error.message}`));
          }
        });
      });

      req.on('error', (error) => {
        reject(error);
      });

      if (data) {
        req.write(JSON.stringify(data));
      }
      
      req.end();
    });
  }
}

// Main execution
async function main() {
  const worker = new WorkerSimulator();
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...');
    await worker.stop();
    process.exit(0);
  });

  try {
    await worker.start();
    
    // Keep running until interrupted
    console.log('\n💡 Worker simulation running. Press Ctrl+C to stop.\n');
    
  } catch (error) {
    console.error('❌ Error starting worker simulation:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}