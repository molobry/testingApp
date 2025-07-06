"""
AI client for element detection and selector generation
"""
import json
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import openai
import anthropic
from loguru import logger
from config import settings


class AIClient(ABC):
    """Abstract base class for AI clients"""
    
    @abstractmethod
    def analyze_dom(self, html_content: str, element_description: str, url: str) -> Dict[str, Any]:
        """Analyze DOM and return element selector"""
        pass


class OpenAIClient(AIClient):
    """OpenAI client for element detection"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model


class AzureOpenAIClient(AIClient):
    """Azure OpenAI client for element detection"""
    
    def __init__(self, api_key: str, endpoint: str, deployment: str, api_version: str = "2024-02-01"):
        self.client = openai.AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version
        )
        self.deployment = deployment
    
    def analyze_dom(self, html_content: str, element_description: str, url: str) -> Dict[str, Any]:
        """Analyze DOM using Azure OpenAI to find element selector"""
        
        system_prompt = """You are an expert at analyzing HTML DOM and finding element selectors.
Given HTML content and an element description, find the best XPath or CSS selector for that element.

Rules:
1. Prefer XPath selectors over CSS selectors
2. Use text-based selectors when possible (e.g., //button[text()='Submit'])
3. Avoid fragile selectors like absolute paths or index-based selectors
4. Return multiple selector options ranked by reliability
5. Include confidence score (0-1) for each selector

Return JSON format:
{
    "selectors": [
        {
            "selector": "//button[text()='Submit']",
            "type": "xpath",
            "confidence": 0.9,
            "reasoning": "Direct text match for button"
        }
    ],
    "best_selector": "//button[text()='Submit']",
    "success": true,
    "error": null
}"""

        user_prompt = f"""
HTML Content:
{html_content[:8000]}  # Limit HTML to avoid token limits

Element to find: "{element_description}"
URL: {url}

Find the best selector for this element. Focus on the most reliable approach.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            logger.info(f"Azure OpenAI analysis completed for: {element_description}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Azure OpenAI response: {e}")
            return {
                "selectors": [],
                "best_selector": None,
                "success": False,
                "error": f"JSON parse error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            return {
                "selectors": [],
                "best_selector": None,
                "success": False,
                "error": str(e)
            }
    
    def analyze_dom(self, html_content: str, element_description: str, url: str) -> Dict[str, Any]:
        """Analyze DOM using OpenAI to find element selector"""
        
        system_prompt = """You are an expert at analyzing HTML DOM and finding element selectors.
Given HTML content and an element description, find the best XPath or CSS selector for that element.

Rules:
1. Prefer XPath selectors over CSS selectors
2. Use text-based selectors when possible (e.g., //button[text()='Submit'])
3. Avoid fragile selectors like absolute paths or index-based selectors
4. Return multiple selector options ranked by reliability
5. Include confidence score (0-1) for each selector

Return JSON format:
{
    "selectors": [
        {
            "selector": "//button[text()='Submit']",
            "type": "xpath",
            "confidence": 0.9,
            "reasoning": "Direct text match for button"
        }
    ],
    "best_selector": "//button[text()='Submit']",
    "success": true,
    "error": null
}"""

        user_prompt = f"""
HTML Content:
{html_content[:8000]}  # Limit HTML to avoid token limits

Element to find: "{element_description}"
URL: {url}

Find the best selector for this element. Focus on the most reliable approach.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            logger.info(f"OpenAI analysis completed for: {element_description}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return {
                "selectors": [],
                "best_selector": None,
                "success": False,
                "error": f"JSON parse error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "selectors": [],
                "best_selector": None,
                "success": False,
                "error": str(e)
            }


class AnthropicClient(AIClient):
    """Anthropic client for element detection"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def analyze_dom(self, html_content: str, element_description: str, url: str) -> Dict[str, Any]:
        """Analyze DOM using Anthropic to find element selector"""
        
        system_prompt = """You are an expert at analyzing HTML DOM and finding element selectors.
Given HTML content and an element description, find the best XPath or CSS selector for that element.

Rules:
1. Prefer XPath selectors over CSS selectors
2. Use text-based selectors when possible (e.g., //button[text()='Submit'])
3. Avoid fragile selectors like absolute paths or index-based selectors
4. Return multiple selector options ranked by reliability
5. Include confidence score (0-1) for each selector

Return JSON format:
{
    "selectors": [
        {
            "selector": "//button[text()='Submit']",
            "type": "xpath",
            "confidence": 0.9,
            "reasoning": "Direct text match for button"
        }
    ],
    "best_selector": "//button[text()='Submit']",
    "success": true,
    "error": null
}"""

        user_prompt = f"""
HTML Content:
{html_content[:8000]}  # Limit HTML to avoid token limits

Element to find: "{element_description}"
URL: {url}

Find the best selector for this element. Focus on the most reliable approach.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            content = response.content[0].text
            result = json.loads(content)
            
            logger.info(f"Anthropic analysis completed for: {element_description}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Anthropic response: {e}")
            return {
                "selectors": [],
                "best_selector": None,
                "success": False,
                "error": f"JSON parse error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return {
                "selectors": [],
                "best_selector": None,
                "success": False,
                "error": str(e)
            }


class AIElementDetector:
    """Main AI element detector that coordinates different AI clients"""
    
    def __init__(self):
        self.client = self._initialize_client()
    
    def _initialize_client(self) -> AIClient:
        """Initialize AI client based on configuration"""
        if settings.ai_provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return OpenAIClient(settings.openai_api_key, settings.openai_model)
        elif settings.ai_provider == "azure_openai":
            if not settings.azure_openai_api_key or not settings.azure_openai_endpoint or not settings.azure_openai_deployment:
                raise ValueError("Azure OpenAI configuration incomplete. Need: api_key, endpoint, deployment")
            return AzureOpenAIClient(
                settings.azure_openai_api_key,
                settings.azure_openai_endpoint,
                settings.azure_openai_deployment,
                settings.azure_openai_api_version
            )
        elif settings.ai_provider == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            return AnthropicClient(settings.anthropic_api_key, settings.anthropic_model)
        else:
            raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
    
    def find_element_selector(self, html_content: str, element_description: str, url: str) -> Dict[str, Any]:
        """Find element selector using AI analysis"""
        logger.info(f"Analyzing element: {element_description}")
        
        # Clean HTML content
        cleaned_html = self._clean_html(html_content)
        
        # Get AI analysis
        result = self.client.analyze_dom(cleaned_html, element_description, url)
        
        # Enhance with fallback selectors if AI failed
        if not result["success"] or not result["best_selector"]:
            result = self._add_fallback_selectors(result, element_description)
        
        return result
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content to focus on interactive elements"""
        # Remove script and style tags
        import re
        
        # Remove script tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove style tags  
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove comments
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        
        # Keep only interactive elements and their context
        # This is a simplified approach - in production, you might want more sophisticated HTML parsing
        
        return html_content
    
    def _add_fallback_selectors(self, result: Dict[str, Any], element_description: str) -> Dict[str, Any]:
        """Add fallback selectors when AI analysis fails"""
        from xpath_helpers import XPathHelper
        
        fallback_selectors = XPathHelper.generate_xpath_variations(element_description)
        
        fallback_list = []
        for selector in fallback_selectors:
            fallback_list.append({
                "selector": selector,
                "type": "xpath",
                "confidence": 0.5,
                "reasoning": "Fallback pattern-based selector"
            })
        
        result["selectors"].extend(fallback_list)
        
        # Set best selector to first fallback if none exists
        if not result["best_selector"] and fallback_list:
            result["best_selector"] = fallback_list[0]["selector"]
            result["success"] = True
        
        return result