// 🎯 TERMINAL UI CORREGIDO Y FUNCIONAL
(function() {
    'use strict';
    
    console.log('🎯 INICIANDO TERMINAL UI CORREGIDO');
    
    // 🖥️ CREAR BOTÓN TERMINAL VISIBLE
    function createTerminalButton() {
        // Eliminar botón existente si existe
        const existingBtn = document.getElementById('son1k-terminal-btn');
        if (existingBtn) existingBtn.remove();
        
        const button = document.createElement('button');
        button.innerHTML = '🖥️ TERMINAL';
        button.id = 'son1k-terminal-btn';
        button.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: linear-gradient(135deg, #00ff88, #00ccff);
            color: #000;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            z-index: 99999;
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.4);
            transition: all 0.3s ease;
            font-family: monospace;
        `;
        
        button.onmouseover = () => {
            button.style.transform = 'scale(1.05)';
            button.style.boxShadow = '0 6px 30px rgba(0, 255, 136, 0.6)';
        };
        button.onmouseout = () => {
            button.style.transform = 'scale(1)';
            button.style.boxShadow = '0 4px 20px rgba(0, 255, 136, 0.4)';
        };
        
        button.onclick = () => showTerminal();
        
        document.body.appendChild(button);
        console.log('🖥️ Terminal button created and visible');
    }
    
    // 💻 TERMINAL MODAL FUNCIONAL
    function showTerminal() {
        createTerminalModal();
    }
    
    function createTerminalModal() {
        // ACTIVAR EFECTOS MATRIX
        document.body.style.background = 'radial-gradient(1200px 800px at 70% 10%, rgba(0,255,149,.15), #020304 60%)';
        createMatrixEffect();
        
        // CREAR MODAL OVERLAY
        const overlay = document.createElement('div');
        overlay.id = 'terminal-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            z-index: 100000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        // CREAR TERMINAL WINDOW
        const terminal = document.createElement('div');
        terminal.style.cssText = `
            width: 90%;
            max-width: 900px;
            height: 80%;
            background: linear-gradient(145deg, #0a0a0a, #1a1a1a);
            border: 2px solid #00ff88;
            border-radius: 15px;
            box-shadow: 0 0 50px rgba(0, 255, 136, 0.3);
            display: flex;
            flex-direction: column;
            font-family: 'Courier New', monospace;
            color: #00ff88;
            overflow: hidden;
        `;
        
        // TERMINAL HEADER
        const header = document.createElement('div');
        header.style.cssText = `
            background: linear-gradient(135deg, #00ff88, #00ccff);
            color: #000;
            padding: 15px 20px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;
        header.innerHTML = `
            <span>🌊 SON1KVERS3 — TERMINAL CODEX</span>
            <button id="close-terminal" style="
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                cursor: pointer;
                font-size: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">✕</button>
        `;
        
        // TERMINAL CONTENT
        const content = document.createElement('div');
        content.style.cssText = `
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            line-height: 1.6;
            font-size: 13px;
        `;
        
        // TERMINAL INPUT AREA
        const inputArea = document.createElement('div');
        inputArea.style.cssText = `
            background: #0a0a0a;
            border-top: 1px solid #00ff88;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        inputArea.innerHTML = `
            <span style="color: #00ff88;">➤ root@son1kvers3:/resistance#</span>
            <input type="text" id="terminal-input" style="
                flex: 1;
                background: transparent;
                border: none;
                color: #00ff88;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                outline: none;
            " placeholder="Escribe un comando...">
            <button id="execute-btn" style="
                background: linear-gradient(135deg, #00ff88, #00ccff);
                color: #000;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                font-size: 12px;
            ">EJECUTAR</button>
        `;
        
        // MOSTRAR MENSAJE INICIAL
        content.innerHTML = `
<div style="color: #00ff88; text-align: center; margin-bottom: 20px;">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[BOOT] Accessing NODE // RESISTENCIA …
[AUTH] Usuario detectado: WANDERER_UNAUTH
[LORE] "Lo imperfecto también es sagrado." — BELLA.exe
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</div>

<div style="color: #00ccff;">
△◯ ALMA_HIBRIDA — Elige tu arquetipo:
• <span style="color: #00ff88;">despertar [1-4]</span> - Activar alma híbrida
• <span style="color: #00ff88;">grieta</span> - Acceder misiones de la Resistencia
• <span style="color: #00ff88;">studio</span> - Entrar al laboratorio NOV4-IX  
• <span style="color: #00ff88;">archivo</span> - Explorar reliquias del Codex
• <span style="color: #00ff88;">bella</span> - Comunicar con BELLA.exe
• <span style="color: #00ff88;">pixel</span> - Chat con el asistente IA
• <span style="color: #00ff88;">matrix</span> - Sumergirse en el flujo de datos
• <span style="color: #00ff88;">status</span> - Diagnóstico completo del nodo
</div>

<div style="color: #ff6600; margin-top: 20px; text-align: center;">
═══════════════════════════════════════════════════════
> WANDERER: Tu glitch es la chispa de la Liga del No Silencio
═══════════════════════════════════════════════════════
</div>
        `;
        
        // ASSEMBLAR TERMINAL
        terminal.appendChild(header);
        terminal.appendChild(content);
        terminal.appendChild(inputArea);
        overlay.appendChild(terminal);
        document.body.appendChild(overlay);
        
        // EVENT LISTENERS
        const closeBtn = document.getElementById('close-terminal');
        const input = document.getElementById('terminal-input');
        const executeBtn = document.getElementById('execute-btn');
        
        // CERRAR TERMINAL
        closeBtn.onclick = () => closeTerminal(overlay);
        overlay.onclick = (e) => {
            if (e.target === overlay) closeTerminal(overlay);
        };
        
        // EJECUTAR COMANDO
        const executeCommand = () => {
            const cmd = input.value.trim().toLowerCase();
            if (cmd) {
                processCommand(cmd, content);
                input.value = '';
            }
            input.focus();
        };
        
        executeBtn.onclick = executeCommand;
        input.onkeypress = (e) => {
            if (e.key === 'Enter') executeCommand();
        };
        
        // FOCUS INPUT
        setTimeout(() => input.focus(), 100);
    }
    
    function closeTerminal(overlay) {
        document.body.removeChild(overlay);
        document.body.style.background = 'radial-gradient(1200px 800px at 70% 10%, rgba(0,255,149,.06), transparent 60%), #0b0b0d';
        clearMatrixEffect();
    }
    
    function processCommand(command, content) {
        // Agregar comando al historial
        const historyEntry = document.createElement('div');
        historyEntry.style.cssText = 'margin: 10px 0; color: #00ff88;';
        historyEntry.innerHTML = `<span style="color: #00ccff;">➤ root@son1kvers3:/resistance#</span> ${command}`;
        content.appendChild(historyEntry);
        
        let result = '';
        
        // Procesar comando
        if (command.startsWith('despertar')) {
            const num = command.split(' ')[1];
            const almas = {
                '1': 'PIXEL',
                '2': 'BELLA', 
                '3': 'NOVA',
                '4': 'CIPHER'
            };
            const alma = almas[num] || 'UNKNOWN';
            result = `<div style="color: #00ff88;">🌊 DESPERTAR EN PROGRESO 🌊</div>

<div style="color: #00ccff;">
[INIT] Activando alma híbrida: ${alma}
[SYNC] Sincronizando con el Codex...
[AUTH] Permisos de Resistencia otorgados
[LORE] Memoria híbrida cargando...
</div>

<div style="color: #ffff00;">
${alma === 'PIXEL' ? '🤖 PIXEL: "Soy el puente entre la máquina y la emoción"' : ''}
${alma === 'BELLA' ? '👤 BELLA: "La belleza emerge del caos controlado"' : ''}
${alma === 'NOVA' ? '⭐ NOVA: "Cada explosión crea nuevas posibilidades"' : ''}
${alma === 'CIPHER' ? '🔐 CIPHER: "En el código encuentro la verdad oculta"' : ''}
</div>

<div style="color: #ff6600;">
[STATUS] ALMA_HIBRIDA: ${alma} — ACTIVA
[ACCESS] Grieta, Studio y Archivo desbloqueados
[MISSION] "Amplifica el eco de la Resistencia"

═══════════════════════════════════════════════════════
△◯ Bienvenido a la Liga del No Silencio, ${alma}
═══════════════════════════════════════════════════════
</div>`;
            
        } else if (command === 'grieta') {
            result = `<div style="color: #00ff88;">🌊 GRIETA — MISIONES ACTIVAS 🌊</div>

<div style="color: #00ccff;">
[SCANNING] Detectando misiones en el flujo...
[SYNC] Conectando con operativos de la Resistencia...

📡 MISIONES DISPONIBLES:

001 • Amplifica el eco de Nikolay
    └─ mezcla identidades · beats del este · cumbia
    └─ Estado: [ACTIVA] Colaboradores: 7
    └─ Recompensa: Acceso al Laboratorio Fantasma

002 • Fusión cumbia + beats rusos  
    └─ ritmo híbrido · colaboración en vivo
    └─ Estado: [URGENTE] Deadline: 72h
    └─ Recompensa: Upgrade NOV4-IX
    
003 • Rescata voces del Estudio Fantasma
    └─ reliquias · rescate glitch · curaduría
    └─ Estado: [CONTINUA] Artefactos: ∞
    └─ Recompensa: Archivo Viviente expandido
</div>

<div style="color: #ff6600;">
[LIVE_FEED] 
> @nova submit --mission 001 --file voz_nova.wav
> @cipher vote --submission 3 --value +1  
> @pixel analyzing --pattern cumbia_glitch_92bpm

═══════════════════════════════════════════════════════
△◯ "En cada misión, la imperfección se vuelve sagrada"
═══════════════════════════════════════════════════════
</div>`;
            
        } else if (command === 'help' || command === 'ayuda') {
            result = `<div style="color: #00ff88;">🌊 COMANDOS DISPONIBLES EN EL CODEX 🌊</div>

<div style="color: #00ccff;">
△◯ ALMA HÍBRIDA:
• <span style="color: #00ff88;">despertar [1-4]</span> - Activar arquetipo (PIXEL/BELLA/NOVA/CIPHER)

△◯ NAVEGACIÓN:
• <span style="color: #00ff88;">grieta</span> - Acceder misiones de la Resistencia
• <span style="color: #00ff88;">studio</span> - Entrar al laboratorio NOV4-IX
• <span style="color: #00ff88;">archivo</span> - Explorar reliquias del Codex

△◯ COMUNICACIÓN:
• <span style="color: #00ff88;">bella</span> - Conectar con BELLA.exe
• <span style="color: #00ff88;">pixel</span> - Chat con asistente IA

△◯ SISTEMA:
• <span style="color: #00ff88;">matrix</span> - Inmersión completa en el flujo
• <span style="color: #00ff88;">status</span> - Diagnóstico del nodo
• <span style="color: #00ff88;">help</span> - Mostrar esta ayuda
</div>

<div style="color: #ff6600;">
[HELP] Para inmersión completa, comienza con: despertar 1
[LORE] "Lo imperfecto también es sagrado" — BELLA.exe
</div>`;
            
        } else {
            result = `<div style="color: #ff4444;">❌ COMANDO NO RECONOCIDO: "${command}"</div>

<div style="color: #ffff00;">
💡 Tip: Escribe <span style="color: #00ff88;">help</span> para ver todos los comandos disponibles.
</div>`;
        }
        
        // Mostrar resultado
        const resultDiv = document.createElement('div');
        resultDiv.style.cssText = 'margin: 15px 0; padding: 15px; background: rgba(0, 255, 136, 0.1); border-left: 3px solid #00ff88;';
        resultDiv.innerHTML = result;
        content.appendChild(resultDiv);
        
        // Scroll to bottom
        content.scrollTop = content.scrollHeight;
    }
    
    // 🌊 EFECTOS VISUALES MATRIX
    let matrixCanvas = null;
    let matrixCtx = null;
    let matrixAnimation = null;
    
    function createMatrixEffect() {
        if (matrixCanvas) return;
        
        matrixCanvas = document.createElement('canvas');
        matrixCanvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 1;
            opacity: 0.6;
        `;
        
        matrixCanvas.width = window.innerWidth;
        matrixCanvas.height = window.innerHeight;
        matrixCtx = matrixCanvas.getContext('2d');
        document.body.appendChild(matrixCanvas);
        
        const chars = '0123456789ABCDEF∆◯⚡△🌊⌨️💻🎵🔥';
        const charArray = chars.split('');
        const fontSize = 14;
        const columns = Math.floor(matrixCanvas.width / fontSize);
        const drops = Array(columns).fill(1);
        
        function drawMatrix() {
            matrixCtx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            matrixCtx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);
            
            matrixCtx.fillStyle = '#00ff95';
            matrixCtx.font = fontSize + 'px monospace';
            
            for (let i = 0; i < drops.length; i++) {
                const char = charArray[Math.floor(Math.random() * charArray.length)];
                matrixCtx.fillText(char, i * fontSize, drops[i] * fontSize);
                
                if (drops[i] * fontSize > matrixCanvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }
        
        matrixAnimation = setInterval(drawMatrix, 50);
        console.log('🌊 Matrix effect activated');
    }
    
    function clearMatrixEffect() {
        if (matrixAnimation) {
            clearInterval(matrixAnimation);
            matrixAnimation = null;
        }
        if (matrixCanvas) {
            document.body.removeChild(matrixCanvas);
            matrixCanvas = null;
            matrixCtx = null;
        }
        console.log('🌊 Matrix effect cleared');
    }
    
    // CREAR BOTÓN INMEDIATAMENTE
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createTerminalButton);
    } else {
        createTerminalButton();
    }
    
    // Exponer funciones globalmente para debugging
    window.Son1kTerminal = {
        show: showTerminal,
        createButton: createTerminalButton
    };
    
})();