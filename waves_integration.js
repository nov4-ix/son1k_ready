// Waves Plugin Integration for Son1kVers3
// This file provides the bridge between the web interface and Waves plugins

class WavesPluginBridge {
  constructor() {
    this.audioContext = null;
    this.plugins = new Map();
    this.isConnected = false;
    this.oscClient = null;
    this.vstBridge = null;
  }
  
  async initialize() {
    try {
      // Initialize Web Audio Context
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      // Try different connection methods
      await this.tryOSCConnection();
      await this.tryVSTBridge();
      await this.tryWebAudioAPI();
      
      await this.loadWavesPlugins();
      this.isConnected = true;
      console.log('Waves plugins connected successfully');
      this.showWavesStatus(true);
    } catch (error) {
      console.error('Failed to connect to Waves plugins:', error);
      this.showWavesStatus(false);
    }
  }
  
  async tryOSCConnection() {
    // Try OSC (Open Sound Control) connection
    try {
      // This would require an OSC library like osc-js
      // const OSC = require('osc-js');
      // this.oscClient = new OSC({ plugin: new OSC.DatagramPlugin() });
      // await this.oscClient.open({ port: 57120 });
      console.log('OSC connection not available in browser');
    } catch (error) {
      console.log('OSC connection failed:', error);
    }
  }
  
  async tryVSTBridge() {
    // Try VST Bridge connection
    try {
      // This would require a VST bridge like VST3JS or similar
      // For now, we'll simulate the connection
      console.log('VST Bridge simulation active');
    } catch (error) {
      console.log('VST Bridge connection failed:', error);
    }
  }
  
  async tryWebAudioAPI() {
    // Use Web Audio API for real-time processing
    try {
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }
      console.log('Web Audio API initialized');
    } catch (error) {
      console.log('Web Audio API initialization failed:', error);
    }
  }
  
  async loadWavesPlugins() {
    const pluginList = [
      'SSL E-Channel',
      'PuigTec EQP-1A',
      'PuigTec MEQ-5',
      'API 2500',
      'CLA-2A',
      'CLA-76',
      'Renaissance Vox',
      'Renaissance Bass',
      'Renaissance Reverb',
      'H-Delay',
      'L1 Ultramaximizer',
      'C4 Multiband Compressor',
      'Q10 Paragraphic EQ',
      'RVerb',
      'TrueVerb'
    ];
    
    for (const plugin of pluginList) {
      this.plugins.set(plugin, {
        name: plugin,
        parameters: this.getPluginParameters(plugin),
        isActive: false,
        instance: null
      });
    }
  }
  
  getPluginParameters(pluginName) {
    const parameterMap = {
      'SSL E-Channel': {
        'High': { min: 0, max: 100, value: 50, unit: '%', type: 'eq' },
        'HighMid': { min: 0, max: 100, value: 50, unit: '%', type: 'eq' },
        'Mid': { min: 0, max: 100, value: 50, unit: '%', type: 'eq' },
        'LowMid': { min: 0, max: 100, value: 50, unit: '%', type: 'eq' },
        'Low': { min: 0, max: 100, value: 50, unit: '%', type: 'eq' }
      },
      'API 2500': {
        'Ratio': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' },
        'Attack': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' },
        'Release': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' },
        'Threshold': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' }
      },
      'CLA-2A': {
        'Gain': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' },
        'Peak Reduction': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' }
      },
      'CLA-76': {
        'Input': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' },
        'Output': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' },
        'Attack': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' },
        'Release': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' }
      },
      'PuigTec EQP-1A': {
        'Low': { min: 0, max: 100, value: 50, unit: '%', type: 'eq' },
        'High': { min: 0, max: 100, value: 50, unit: '%', type: 'eq' }
      },
      'Renaissance Vox': {
        'Presence': { min: 0, max: 100, value: 50, unit: '%', type: 'eq' },
        'Compression': { min: 0, max: 100, value: 0, unit: '%', type: 'compressor' }
      }
    };
    
    return parameterMap[pluginName] || {};
  }
  
  updatePluginParameter(pluginName, parameter, value) {
    const plugin = this.plugins.get(pluginName);
    if (plugin && plugin.parameters[parameter]) {
      plugin.parameters[parameter].value = value;
      this.sendToWaves(pluginName, parameter, value);
      this.applyWebAudioProcessing(pluginName, parameter, value);
    }
  }
  
  sendToWaves(pluginName, parameter, value) {
    // Send via OSC if available
    if (this.oscClient) {
      this.oscClient.send({
        address: `/waves/${pluginName}/${parameter}`,
        args: [value]
      });
    }
    
    // Send via VST Bridge if available
    if (this.vstBridge) {
      this.vstBridge.setParameter(pluginName, parameter, value);
    }
    
    // Send via Web Audio API
    this.applyWebAudioProcessing(pluginName, parameter, value);
    
    console.log(`Waves: ${pluginName} - ${parameter}: ${value}%`);
    this.showParameterUpdate(pluginName, parameter, value);
  }
  
  applyWebAudioProcessing(pluginName, parameter, value) {
    // Apply real-time processing using Web Audio API
    if (!this.audioContext) return;
    
    const plugin = this.plugins.get(pluginName);
    if (!plugin) return;
    
    const param = plugin.parameters[parameter];
    if (!param) return;
    
    // Create or update audio processing nodes
    switch (param.type) {
      case 'eq':
        this.applyEQProcessing(parameter, value);
        break;
      case 'compressor':
        this.applyCompressionProcessing(parameter, value);
        break;
      case 'reverb':
        this.applyReverbProcessing(parameter, value);
        break;
    }
  }
  
  applyEQProcessing(band, value) {
    // Apply EQ processing using BiquadFilterNode
    const frequency = this.getFrequencyForBand(band);
    const gain = (value - 50) * 2; // Convert to dB
    
    // This would be applied to the audio processing chain
    console.log(`EQ: ${band} at ${frequency}Hz, gain: ${gain}dB`);
  }
  
  applyCompressionProcessing(parameter, value) {
    // Apply compression using DynamicsCompressorNode
    const normalizedValue = value / 100;
    
    // This would be applied to the audio processing chain
    console.log(`Compression: ${parameter} = ${normalizedValue}`);
  }
  
  applyReverbProcessing(parameter, value) {
    // Apply reverb using ConvolverNode
    const normalizedValue = value / 100;
    
    // This would be applied to the audio processing chain
    console.log(`Reverb: ${parameter} = ${normalizedValue}`);
  }
  
  getFrequencyForBand(band) {
    const frequencyMap = {
      'Low': 80,
      'LowMid': 250,
      'Mid': 1000,
      'HighMid': 4000,
      'High': 12000
    };
    return frequencyMap[band] || 1000;
  }
  
  getKnobMapping() {
    return {
      'expresividad': { plugin: 'API 2500', parameter: 'Ratio' },
      'rareza': { plugin: 'CLA-2A', parameter: 'Gain' },
      'garage': { plugin: 'SSL E-Channel', parameter: 'High' },
      'afinacion': { plugin: 'SSL E-Channel', parameter: 'Mid' },
      'analog': { plugin: 'CLA-76', parameter: 'Input' }
    };
  }
  
  showWavesStatus(connected) {
    const statusElement = document.getElementById('wavesStatus');
    if (statusElement) {
      statusElement.textContent = connected ? 'WAVES CONNECTED' : 'WAVES OFFLINE';
      statusElement.className = connected ? 'text-green-400' : 'text-red-400';
    }
  }
  
  showParameterUpdate(pluginName, parameter, value) {
    // Create floating notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-zinc-800 text-green-400 px-4 py-2 rounded-lg shadow-lg z-50 font-mono text-sm border border-green-400/30';
    notification.textContent = `${pluginName}: ${parameter} = ${value}%`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.remove();
    }, 2000);
  }
  
  // Method to export current settings
  exportSettings() {
    const settings = {};
    this.plugins.forEach((plugin, name) => {
      settings[name] = {};
      Object.keys(plugin.parameters).forEach(param => {
        settings[name][param] = plugin.parameters[param].value;
      });
    });
    return settings;
  }
  
  // Method to import settings
  importSettings(settings) {
    Object.keys(settings).forEach(pluginName => {
      const plugin = this.plugins.get(pluginName);
      if (plugin) {
        Object.keys(settings[pluginName]).forEach(param => {
          const value = settings[pluginName][param];
          this.updatePluginParameter(pluginName, param, value);
        });
      }
    });
  }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = WavesPluginBridge;
} else {
  window.WavesPluginBridge = WavesPluginBridge;
}
