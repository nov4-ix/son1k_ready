// Voice Cloning Integration System for Son1kVers3
// Supports so-VITS, XTTR, and cloud-based voice cloning

class VoiceCloningSystem {
  constructor() {
    this.userTier = 'free'; // free, pro, enterprise
    this.voiceModels = new Map();
    this.isInitialized = false;
    this.apiEndpoints = {
      huggingface: 'https://api-inference.huggingface.co/models',
      elevenlabs: 'https://api.elevenlabs.io/v1',
      azure: 'https://your-region.cognitiveservices.azure.com',
      resemble: 'https://app.resemble.ai/api/v2'
    };
  }

  async initialize() {
    try {
      await this.loadUserTier();
      await this.setupVoiceModels();
      this.isInitialized = true;
      console.log('Voice Cloning System initialized');
    } catch (error) {
      console.error('Failed to initialize Voice Cloning System:', error);
    }
  }

  async loadUserTier() {
    // Get user tier from authentication
    const token = localStorage.getItem('authToken');
    if (token) {
      try {
        const response = await fetch('/api/user/profile', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const user = await response.json();
        this.userTier = user.tier || 'free';
      } catch (error) {
        this.userTier = 'free';
      }
    }
  }

  async setupVoiceModels() {
    const models = {
      'free': {
        'so-vits': {
          name: 'so-vits-svc-4.0',
          provider: 'huggingface',
          modelId: 'lj1995/VoiceConversionWebUI',
          maxDuration: 30, // seconds
          quality: 'standard'
        },
        'bark': {
          name: 'Bark Voice Cloning',
          provider: 'huggingface',
          modelId: 'suno/bark',
          maxDuration: 60,
          quality: 'high'
        }
      },
      'pro': {
        'so-vits': {
          name: 'so-vits-svc-4.0-pro',
          provider: 'elevenlabs',
          modelId: 'eleven_multilingual_v2',
          maxDuration: 120,
          quality: 'high'
        },
        'xttr': {
          name: 'XTTR-v2-pro',
          provider: 'azure',
          modelId: 'neural-voice',
          maxDuration: 120,
          quality: 'high'
        },
        'elevenlabs': {
          name: 'ElevenLabs Voice Cloning',
          provider: 'elevenlabs',
          modelId: 'eleven_multilingual_v2',
          maxDuration: 300,
          quality: 'premium'
        }
      },
      'enterprise': {
        'so-vits': {
          name: 'so-vits-svc-4.0-enterprise',
          provider: 'resemble',
          modelId: 'custom-voice-model',
          maxDuration: 600,
          quality: 'professional'
        },
        'xttr': {
          name: 'XTTR-v2-enterprise',
          provider: 'azure',
          modelId: 'custom-neural-voice',
          maxDuration: 600,
          quality: 'professional'
        },
        'elevenlabs': {
          name: 'ElevenLabs Pro',
          provider: 'elevenlabs',
          modelId: 'eleven_multilingual_v2',
          maxDuration: 1800,
          quality: 'studio'
        },
        'custom': {
          name: 'Custom Voice Model',
          provider: 'custom',
          modelId: 'user-trained-model',
          maxDuration: 3600,
          quality: 'studio'
        }
      }
    };

    this.voiceModels = new Map(Object.entries(models[this.userTier]));
  }

  async cloneVoice(audioFile, text, voiceSettings = {}) {
    if (!this.isInitialized) {
      throw new Error('Voice Cloning System not initialized');
    }

    const model = this.selectBestModel(voiceSettings);
    const result = await this.processVoiceCloning(audioFile, text, model);
    
    return {
      success: true,
      audioUrl: result.audioUrl,
      model: model.name,
      duration: result.duration,
      quality: model.quality,
      tier: this.userTier
    };
  }

  selectBestModel(voiceSettings) {
    const { quality = 'standard', duration = 30, style = 'natural' } = voiceSettings;
    
    // Select model based on user tier and requirements
    if (this.userTier === 'enterprise') {
      return this.voiceModels.get('custom') || this.voiceModels.get('elevenlabs');
    } else if (this.userTier === 'pro') {
      return this.voiceModels.get('elevenlabs') || this.voiceModels.get('so-vits');
    } else {
      return this.voiceModels.get('so-vits');
    }
  }

  async processVoiceCloning(audioFile, text, model) {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('text', text);
    formData.append('model', model.modelId);
    formData.append('settings', JSON.stringify({
      quality: model.quality,
      maxDuration: model.maxDuration
    }));

    switch (model.provider) {
      case 'huggingface':
        return await this.processWithHuggingFace(formData, model);
      case 'elevenlabs':
        return await this.processWithElevenLabs(formData, model);
      case 'azure':
        return await this.processWithAzure(formData, model);
      case 'resemble':
        return await this.processWithResemble(formData, model);
      case 'custom':
        return await this.processWithCustomModel(formData, model);
      default:
        throw new Error(`Unsupported provider: ${model.provider}`);
    }
  }

  async processWithHuggingFace(formData, model) {
    const response = await fetch(`${this.apiEndpoints.huggingface}/${model.modelId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
        'Content-Type': 'multipart/form-data'
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Hugging Face API error: ${response.statusText}`);
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    
    return {
      audioUrl,
      duration: this.getAudioDuration(audioBlob)
    };
  }

  async processWithElevenLabs(formData, model) {
    const response = await fetch(`${this.apiEndpoints.elevenlabs}/text-to-speech/${model.modelId}`, {
      method: 'POST',
      headers: {
        'xi-api-key': process.env.ELEVENLABS_API_KEY,
        'Content-Type': 'multipart/form-data'
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`ElevenLabs API error: ${response.statusText}`);
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    
    return {
      audioUrl,
      duration: this.getAudioDuration(audioBlob)
    };
  }

  async processWithAzure(formData, model) {
    const response = await fetch(`${this.apiEndpoints.azure}/text-to-speech/3.1-preview1/batchsynthesis`, {
      method: 'POST',
      headers: {
        'Ocp-Apim-Subscription-Key': process.env.AZURE_API_KEY,
        'Content-Type': 'multipart/form-data'
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Azure API error: ${response.statusText}`);
    }

    const result = await response.json();
    const audioUrl = await this.pollForAudioUrl(result.operationId);
    
    return {
      audioUrl,
      duration: this.getAudioDurationFromUrl(audioUrl)
    };
  }

  async processWithResemble(formData, model) {
    const response = await fetch(`${this.apiEndpoints.resemble}/projects/${model.modelId}/synthesize`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${process.env.RESEMBLE_API_KEY}`,
        'Content-Type': 'multipart/form-data'
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Resemble API error: ${response.statusText}`);
    }

    const result = await response.json();
    const audioUrl = result.item.audio_url;
    
    return {
      audioUrl,
      duration: this.getAudioDurationFromUrl(audioUrl)
    };
  }

  async processWithCustomModel(formData, model) {
    // Custom model processing (could be your own API)
    const response = await fetch('/api/voice/custom-clone', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        'Content-Type': 'multipart/form-data'
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Custom model API error: ${response.statusText}`);
    }

    const result = await response.json();
    
    return {
      audioUrl: result.audioUrl,
      duration: result.duration
    };
  }

  async pollForAudioUrl(operationId) {
    // Poll for Azure batch synthesis completion
    const maxAttempts = 30;
    let attempts = 0;

    while (attempts < maxAttempts) {
      const response = await fetch(`${this.apiEndpoints.azure}/text-to-speech/3.1-preview1/batchsynthesis/${operationId}`, {
        headers: {
          'Ocp-Apim-Subscription-Key': process.env.AZURE_API_KEY
        }
      });

      const result = await response.json();
      
      if (result.status === 'Succeeded') {
        return result.outputs.result;
      } else if (result.status === 'Failed') {
        throw new Error('Azure synthesis failed');
      }

      await new Promise(resolve => setTimeout(resolve, 2000));
      attempts++;
    }

    throw new Error('Azure synthesis timeout');
  }

  getAudioDuration(audioBlob) {
    return new Promise((resolve) => {
      const audio = new Audio();
      audio.onloadedmetadata = () => resolve(audio.duration);
      audio.src = URL.createObjectURL(audioBlob);
    });
  }

  async getAudioDurationFromUrl(audioUrl) {
    return new Promise((resolve) => {
      const audio = new Audio();
      audio.onloadedmetadata = () => resolve(audio.duration);
      audio.src = audioUrl;
    });
  }

  // Voice model management
  async uploadVoiceSample(audioFile, voiceName) {
    if (this.userTier === 'free') {
      throw new Error('Voice upload requires Pro or Enterprise tier');
    }

    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('name', voiceName);
    formData.append('tier', this.userTier);

    const response = await fetch('/api/voice/upload-sample', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        'Content-Type': 'multipart/form-data'
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error('Failed to upload voice sample');
    }

    return await response.json();
  }

  async trainVoiceModel(voiceId, trainingData) {
    if (this.userTier !== 'enterprise') {
      throw new Error('Voice training requires Enterprise tier');
    }

    const response = await fetch('/api/voice/train-model', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        voiceId,
        trainingData,
        tier: this.userTier
      })
    });

    if (!response.ok) {
      throw new Error('Failed to train voice model');
    }

    return await response.json();
  }

  // Integration with Ghost Studio
  async integrateWithGhostStudio(audioFile, transformPrompt) {
    const voiceSettings = this.extractVoiceSettings(transformPrompt);
    const text = this.extractTextFromPrompt(transformPrompt);
    
    if (!text) {
      throw new Error('No text found in transform prompt');
    }

    return await this.cloneVoice(audioFile, text, voiceSettings);
  }

  extractVoiceSettings(prompt) {
    const settings = {
      quality: 'standard',
      duration: 30,
      style: 'natural'
    };

    if (prompt.includes('alta calidad') || prompt.includes('premium')) {
      settings.quality = 'high';
    }
    if (prompt.includes('profesional') || prompt.includes('studio')) {
      settings.quality = 'professional';
    }
    if (prompt.includes('largo') || prompt.includes('extended')) {
      settings.duration = 120;
    }
    if (prompt.includes('corto') || prompt.includes('short')) {
      settings.duration = 15;
    }
    if (prompt.includes('emocional') || prompt.includes('emotional')) {
      settings.style = 'emotional';
    }
    if (prompt.includes('robótico') || prompt.includes('robotic')) {
      settings.style = 'robotic';
    }

    return settings;
  }

  extractTextFromPrompt(prompt) {
    // Extract text to be spoken from the prompt
    // This could be enhanced with NLP
    const textMatch = prompt.match(/"([^"]+)"/);
    if (textMatch) {
      return textMatch[1];
    }

    // Fallback: extract text after certain keywords
    const keywords = ['decir', 'hablar', 'texto', 'letra'];
    for (const keyword of keywords) {
      const index = prompt.indexOf(keyword);
      if (index !== -1) {
        return prompt.substring(index + keyword.length).trim();
      }
    }

    return null;
  }

  // Usage tracking and limits
  getUsageStats() {
    return {
      tier: this.userTier,
      monthlyUsage: this.getMonthlyUsage(),
      limits: this.getTierLimits(),
      remaining: this.getRemainingUsage()
    };
  }

  getTierLimits() {
    const limits = {
      'free': { monthlyMinutes: 30, maxDuration: 30, quality: 'standard' },
      'pro': { monthlyMinutes: 300, maxDuration: 120, quality: 'high' },
      'enterprise': { monthlyMinutes: 1800, maxDuration: 600, quality: 'professional' }
    };
    return limits[this.userTier];
  }

  getMonthlyUsage() {
    // Get from localStorage or API
    const usage = localStorage.getItem('voiceUsage');
    return usage ? JSON.parse(usage) : { minutes: 0, requests: 0 };
  }

  getRemainingUsage() {
    const limits = this.getTierLimits();
    const usage = this.getMonthlyUsage();
    return {
      minutes: Math.max(0, limits.monthlyMinutes - usage.minutes),
      requests: Math.max(0, limits.monthlyRequests - usage.requests)
    };
  }

  updateUsage(duration) {
    const usage = this.getMonthlyUsage();
    usage.minutes += duration / 60;
    usage.requests += 1;
    localStorage.setItem('voiceUsage', JSON.stringify(usage));
  }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = VoiceCloningSystem;
} else {
  window.VoiceCloningSystem = VoiceCloningSystem;
}
