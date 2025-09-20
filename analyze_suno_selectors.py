#!/usr/bin/env python3
"""
Analyze current Suno.com DOM structure to update selectors
"""
import time
import json
from backend.app.selenium_worker import SunoSeleniumWorker

def analyze_suno_dom():
    """Analyze Suno.com current DOM structure"""
    print("🔍 Analyzing Suno.com DOM structure...")
    
    worker = SunoSeleniumWorker(headless=True)
    
    try:
        # Setup driver
        if not worker.setup_driver():
            print("❌ Driver setup failed")
            return
        
        # Load Suno.com
        if not worker.load_suno_with_auth():
            print("❌ Failed to load Suno.com")
            return
        
        print("📸 Taking screenshot of main page...")
        worker.take_screenshot("main_page")
        
        # Try to navigate to create page
        print("🎵 Attempting to find create page elements...")
        
        # Check current URL
        current_url = worker.driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        # Try different create page URLs
        create_urls = [
            "https://suno.com/create",
            "https://app.suno.ai/create", 
            "https://suno.ai/create",
            "https://www.suno.com/create"
        ]
        
        for url in create_urls:
            print(f"🌐 Trying URL: {url}")
            try:
                worker.driver.get(url)
                time.sleep(3)
                
                current_url = worker.driver.current_url
                page_title = worker.driver.title
                print(f"  ✅ Loaded: {current_url}")
                print(f"  📄 Title: {page_title}")
                
                # Take screenshot
                worker.take_screenshot(f"create_page_{url.split('/')[-2]}")
                
                # Look for common input elements
                print("  🔍 Searching for input elements...")
                
                # Find all input elements
                inputs = worker.driver.find_elements("css selector", "input, textarea, button")
                print(f"  📝 Found {len(inputs)} input elements")
                
                # Analyze each input
                elements_found = []
                for i, element in enumerate(inputs[:20]):  # Limit to first 20
                    try:
                        tag = element.tag_name
                        elem_type = element.get_attribute('type') or 'undefined'
                        placeholder = element.get_attribute('placeholder') or ''
                        name = element.get_attribute('name') or ''
                        data_testid = element.get_attribute('data-testid') or ''
                        class_name = element.get_attribute('class') or ''
                        text = element.text[:50] if element.text else ''
                        
                        element_info = {
                            'index': i,
                            'tag': tag,
                            'type': elem_type,
                            'placeholder': placeholder,
                            'name': name,
                            'data-testid': data_testid,
                            'class': class_name,
                            'text': text
                        }
                        
                        elements_found.append(element_info)
                        
                        # Print relevant elements
                        if any(keyword in placeholder.lower() for keyword in ['prompt', 'style', 'lyrics', 'music']):
                            print(f"    🎯 {tag}[{elem_type}]: '{placeholder}' (testid: {data_testid})")
                        elif any(keyword in text.lower() for keyword in ['create', 'generate', 'submit']):
                            print(f"    🎯 {tag}: '{text}' (testid: {data_testid})")
                    
                    except Exception as e:
                        continue
                
                # Save elements to file for analysis
                with open(f'elements_{url.split("/")[-2]}.json', 'w') as f:
                    json.dump(elements_found, f, indent=2)
                
                print(f"  💾 Saved elements to elements_{url.split('/')[-2]}.json")
                
                # Look for specific patterns
                print("  🔎 Looking for key patterns...")
                
                # Check for text-based elements
                text_elements = worker.driver.find_elements("xpath", "//*[contains(text(), 'Create') or contains(text(), 'Generate') or contains(text(), 'Music')]")
                print(f"  📝 Found {len(text_elements)} text-based elements with key terms")
                
                if text_elements:
                    for elem in text_elements[:5]:
                        try:
                            print(f"    📌 {elem.tag_name}: '{elem.text}' (class: {elem.get_attribute('class')})")
                        except:
                            continue
                
                # If this looks like a valid create page, break
                if any(keyword in page_title.lower() for keyword in ['create', 'generate', 'studio']):
                    print("  ✅ This appears to be a valid create page!")
                    break
                
            except Exception as e:
                print(f"  ❌ Failed to load {url}: {e}")
                continue
        
        print("✅ DOM analysis completed")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        
    finally:
        worker.cleanup()

if __name__ == "__main__":
    analyze_suno_dom()