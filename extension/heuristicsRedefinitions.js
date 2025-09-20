// Heuristics and DOM Detection
console.log('🎯 Extension heuristics loaded');

// Heuristics for detecting and interacting with web elements
window.heuristics = {
    // Suno.com selectors
    suno: {
        promptInputs: [
            'textarea[placeholder*="Describe"]',
            'textarea[placeholder*="prompt"]',
            'textarea[placeholder*="Song description"]',
            '[data-testid="prompt-input"]',
            'input[placeholder*="Describe"]'
        ],
        
        lyricsInputs: [
            'textarea[placeholder*="lyrics"]',
            'textarea[placeholder*="Lyrics"]',
            'textarea[placeholder*="Custom lyrics"]',
            '[data-testid="lyrics-input"]'
        ],
        
        createButtons: [
            'button[type="submit"]',
            'button:contains("Create")',
            'button:contains("Generate")',
            '[data-testid="create-button"]'
        ],
        
        forms: [
            '[data-testid="create-form"]',
            '.create-form',
            'form',
            '.generation-form'
        ]
    },
    
    // Detection methods
    detectElement: (selectors) => {
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                console.log(`🎯 Found element: ${selector}`);
                return element;
            }
        }
        return null;
    },
    
    detectAllElements: (selectors) => {
        const found = [];
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                found.push(...elements);
                console.log(`🎯 Found ${elements.length} elements for: ${selector}`);
            }
        }
        return found;
    },
    
    // Wait for element to appear
    waitForElement: (selector, timeout = 10000) => {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            
            const checkForElement = () => {
                const element = document.querySelector(selector);
                if (element) {
                    resolve(element);
                    return;
                }
                
                if (Date.now() - startTime > timeout) {
                    reject(new Error(`Element ${selector} not found within ${timeout}ms`));
                    return;
                }
                
                setTimeout(checkForElement, 100);
            };
            
            checkForElement();
        });
    }
};