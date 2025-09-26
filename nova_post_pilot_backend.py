#!/usr/bin/env python3
"""
Nova Post Pilot Backend
AI-Powered Content Creation & Social Media Management
"""

import asyncio
import json
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Nova Post Pilot API", version="1.0.0")

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

class CreatorProfile(BaseModel):
    content_type: str
    target_audience: str
    platforms: List[str]
    content_goals: str
    additional_info: Optional[str] = None

class MarketAnalysisRequest(BaseModel):
    profile: CreatorProfile
    analysis_depth: str = "advanced"

class ContentGenerationRequest(BaseModel):
    profile: CreatorProfile
    content_type: str
    platform: str
    hook_style: str = "viral"

class PublishingRequest(BaseModel):
    content: str
    platform: str
    scheduled_time: Optional[str] = None
    auto_publish: bool = False

class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate(self, prompt: str, model: str = OLLAMA_MODEL) -> str:
        """Generate content using Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    logger.error(f"Ollama API error: {response.status}")
                    return ""
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return ""

async def analyze_market_trends(profile: CreatorProfile) -> Dict:
    """Analyze market trends for the creator's niche"""
    prompt = f"""
    As a social media marketing expert, analyze the market trends for a {profile.content_type} creator targeting {profile.target_audience}.
    
    Provide analysis in JSON format with:
    - target_insights: age_range, interests, peak_hours, engagement_level
    - trending_topics: list of trending hashtags with growth percentages
    - best_posting_times: optimal times for each platform
    - competitor_analysis: key competitors and their strategies
    - content_gaps: opportunities in the market
    
    Focus on platforms: {', '.join(profile.platforms)}
    Content goals: {profile.content_goals}
    """
    
    async with OllamaClient() as client:
        response = await client.generate(prompt)
        
        try:
            # Try to parse JSON response
            analysis = json.loads(response)
        except json.JSONDecodeError:
            # Fallback to structured response
            analysis = {
                "target_insights": {
                    "age_range": "18-35",
                    "interests": "Music, Tech, AI",
                    "peak_hours": "7-9 PM",
                    "engagement_level": "High"
                },
                "trending_topics": [
                    {"name": "#AIMusic", "growth": "+45%"},
                    {"name": "#MusicTech", "growth": "+32%"},
                    {"name": "#ProducerLife", "growth": "+28%"},
                    {"name": "#StudioSetup", "growth": "+21%"}
                ],
                "best_posting_times": {
                    "instagram": "6-9 PM",
                    "tiktok": "6-10 PM",
                    "youtube": "2-4 PM",
                    "twitter": "12-3 PM"
                },
                "competitor_analysis": "Top creators in this niche focus on behind-the-scenes content",
                "content_gaps": "Educational content about AI tools in music production"
            }
        
        return analysis

async def generate_viral_hooks(profile: CreatorProfile, hook_style: str = "viral") -> List[str]:
    """Generate viral hook templates"""
    prompt = f"""
    Generate 3 viral hook templates for a {profile.content_type} creator targeting {profile.target_audience}.
    
    Style: {hook_style}
    Platforms: {', '.join(profile.platforms)}
    Goals: {profile.content_goals}
    
    Create hooks that:
    1. Grab attention immediately
    2. Create curiosity
    3. Are platform-appropriate
    4. Match the target audience
    
    Return as a JSON array of 3 hook strings.
    """
    
    async with OllamaClient() as client:
        response = await client.generate(prompt)
        
        try:
            hooks = json.loads(response)
        except json.JSONDecodeError:
            # Fallback hooks based on content type
            hooks = {
                "music": [
                    "This AI tool just changed everything about music production...",
                    "3 things every music producer needs to know in 2024...",
                    "I tried this controversial music technique and the results shocked me..."
                ],
                "gaming": [
                    "This game mechanic is breaking the internet...",
                    "5 secrets every gamer needs to know...",
                    "I played this game for 24 hours straight and here's what happened..."
                ],
                "tech": [
                    "This new technology will change everything...",
                    "3 tech trends that will dominate 2024...",
                    "I tested this controversial tech and the results were surprising..."
                ]
            }
            hooks = hooks.get(profile.content_type, hooks["music"])
        
        return hooks

async def generate_content_suggestions(profile: CreatorProfile) -> List[Dict]:
    """Generate content suggestions with engagement predictions"""
    prompt = f"""
    Generate 6 content suggestions for a {profile.content_type} creator targeting {profile.target_audience}.
    
    Platforms: {', '.join(profile.platforms)}
    Goals: {profile.content_goals}
    
    For each suggestion, provide:
    - title: engaging content title
    - description: brief description
    - expected_engagement: predicted likes/views
    - content_type: video, image, carousel, etc.
    - hashtags: relevant hashtags
    - best_platform: optimal platform for this content
    
    Return as JSON array of content suggestions.
    """
    
    async with OllamaClient() as client:
        response = await client.generate(prompt)
        
        try:
            suggestions = json.loads(response)
        except json.JSONDecodeError:
            # Fallback suggestions
            suggestions = [
                {
                    "title": "Behind the scenes: Creating a beat in 60 seconds",
                    "description": "Quick tutorial showing the creative process",
                    "expected_engagement": "15K+ likes",
                    "content_type": "video",
                    "hashtags": ["#MusicProduction", "#BehindTheScenes", "#QuickTutorial"],
                    "best_platform": "instagram"
                },
                {
                    "title": "AI vs Human: Can you tell the difference?",
                    "description": "Blind test comparing AI and human-created music",
                    "expected_engagement": "12K+ likes",
                    "content_type": "video",
                    "hashtags": ["#AIMusic", "#BlindTest", "#MusicTech"],
                    "best_platform": "tiktok"
                }
            ]
        
        return suggestions

async def optimize_posting_schedule(profile: CreatorProfile) -> Dict:
    """Optimize posting schedule based on audience analysis"""
    prompt = f"""
    Create an optimal posting schedule for a {profile.content_type} creator targeting {profile.target_audience}.
    
    Platforms: {', '.join(profile.platforms)}
    Goals: {profile.content_goals}
    
    Provide:
    - daily_schedule: best times for each day of the week
    - platform_specific: optimal times for each platform
    - content_frequency: how often to post on each platform
    - engagement_tips: platform-specific engagement strategies
    
    Return as JSON object.
    """
    
    async with OllamaClient() as client:
        response = await client.generate(prompt)
        
        try:
            schedule = json.loads(response)
        except json.JSONDecodeError:
            # Fallback schedule
            schedule = {
                "daily_schedule": {
                    "monday": {"instagram": "6:00 PM", "tiktok": "6:30 PM"},
                    "tuesday": {"instagram": "7:30 PM", "tiktok": "7:00 PM"},
                    "wednesday": {"youtube": "2:00 PM", "instagram": "8:00 PM"},
                    "thursday": {"tiktok": "7:00 PM", "twitter": "12:00 PM"},
                    "friday": {"instagram": "8:00 PM", "tiktok": "9:00 PM"},
                    "saturday": {"tiktok": "9:00 PM", "youtube": "3:00 PM"},
                    "sunday": {"youtube": "3:00 PM", "twitter": "6:00 PM"}
                },
                "platform_specific": {
                    "instagram": "6-9 PM",
                    "tiktok": "6-10 PM",
                    "youtube": "2-4 PM",
                    "twitter": "12-3 PM"
                },
                "content_frequency": {
                    "instagram": "3-4 posts per week",
                    "tiktok": "1-2 posts per day",
                    "youtube": "1-2 videos per week",
                    "twitter": "2-3 posts per day"
                },
                "engagement_tips": {
                    "instagram": "Use Stories for behind-the-scenes content",
                    "tiktok": "Jump on trending sounds and challenges",
                    "youtube": "Create longer-form educational content",
                    "twitter": "Engage in conversations and share quick thoughts"
                }
            }
        
        return schedule

@app.post("/api/npp/analyze-profile")
async def analyze_profile(request: MarketAnalysisRequest):
    """Analyze creator profile and generate market insights"""
    try:
        analysis = await analyze_market_trends(request.profile)
        return {"success": True, "analysis": analysis}
    except Exception as e:
        logger.error(f"Profile analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/api/npp/generate-hooks")
async def generate_hooks(request: ContentGenerationRequest):
    """Generate viral hook templates"""
    try:
        hooks = await generate_viral_hooks(request.profile, request.hook_style)
        return {"success": True, "hooks": hooks}
    except Exception as e:
        logger.error(f"Hook generation error: {e}")
        raise HTTPException(status_code=500, detail="Hook generation failed")

@app.post("/api/npp/generate-content")
async def generate_content(request: ContentGenerationRequest):
    """Generate content suggestions"""
    try:
        suggestions = await generate_content_suggestions(request.profile)
        return {"success": True, "suggestions": suggestions}
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        raise HTTPException(status_code=500, detail="Content generation failed")

@app.post("/api/npp/optimize-schedule")
async def optimize_schedule(request: MarketAnalysisRequest):
    """Optimize posting schedule"""
    try:
        schedule = await optimize_posting_schedule(request.profile)
        return {"success": True, "schedule": schedule}
    except Exception as e:
        logger.error(f"Schedule optimization error: {e}")
        raise HTTPException(status_code=500, detail="Schedule optimization failed")

@app.post("/api/npp/publish-content")
async def publish_content(request: PublishingRequest):
    """Publish or schedule content"""
    try:
        # Here you would integrate with actual social media APIs
        # For now, we'll simulate the publishing process
        
        if request.auto_publish:
            # Simulate immediate publishing
            return {
                "success": True,
                "message": "Content published successfully",
                "platform": request.platform,
                "published_at": "now"
            }
        else:
            # Simulate scheduling
            return {
                "success": True,
                "message": "Content scheduled successfully",
                "platform": request.platform,
                "scheduled_for": request.scheduled_time
            }
    except Exception as e:
        logger.error(f"Publishing error: {e}")
        raise HTTPException(status_code=500, detail="Publishing failed")

@app.get("/api/npp/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Nova Post Pilot"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
