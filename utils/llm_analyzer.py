#!/usr/bin/env python3
"""
LLM Analyzer Module
Deep insights using Gemini or OpenRouter (Claude/GPT)
Date: December 6, 2025
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMAnalyzer:
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.provider = 'gemini' if self.gemini_key else ('openrouter' if self.openrouter_key else None)
        # Use a more stable and commonly available free model for OpenRouter
        # Default Gemini provider to flash
        self.model = os.getenv('LLM_MODEL', 'google/gemini-pro-1.5' if self.provider == 'openrouter' else 'gemini-1.5-flash')

    def analyze_page_content(self, url, keyword, content_snippet=None):
        """Analyze a page for SEO optimization against a target keyword"""
        if not self.provider:
            return {"error": "No LLM API key found"}

        prompt = f"""
        You are an expert SEO auditor. Analyze the content below for the keyword: "{keyword}"
        URL: {url}
        
        --- PAGE CONTENT START ---
        {content_snippet[:3000] if content_snippet else "No content provided. Please infer based on URL patterns."}
        --- PAGE CONTENT END ---
        
        Provide 3 specific, actionable SEO recommendations.
        STRICTLY OUTPUT VALID JSON ONLY. No markdown, no conversational text.
        
        Expected Format:
        {{
            "recommendations": [
                "Action 1: ...",
                "Action 2: ...",
                "Action 3: ..."
            ],
            "score": 85
        }}
        """
        
        return self._call_llm(prompt)

    def generate_content_brief(self, keyword, competitors):
        """Generate a content brief to outrank competitors"""
        if not self.provider:
            return {"error": "No LLM API key found"}

        prompt = f"""
        You are a content strategist. Create an SEO brief for: "{keyword}"
        Competitors: {', '.join(competitors)}
        
        STRICTLY OUTPUT VALID JSON ONLY. No markdown.
        
        Expected Format:
        {{
            "title_ideas": ["Title 1...", "Title 2..."],
            "target_word_count": 1500,
            "headings_structure": ["H1: ...", "H2: ...", "H2: ..."],
            "unique_angle": "Focus on..."
        }}
        """
        
        return self._call_llm(prompt)

    def generate_holistic_strategy(self, context_data):
        """Generate a comprehensive SEO strategy based on aggregated data"""
        if not self.provider:
            return {"error": "No LLM API key found"}

        prompt = f"""
        You are a Chief SEO Strategist. Review this audit data for {context_data.get('domain', 'the website')} and create a high-impact strategy.
        
        DATA CONTEXT:
        1. Top Keyword Opportunities: {', '.join(context_data.get('top_keywords', []))}
        2. Declining Keywords (Risk): {', '.join(context_data.get('declining_keywords', []))}
        3. Technical Health: {context_data.get('technical_summary', 'No data')}
        4. Content Issues: {context_data.get('content_summary', 'No data')}
        
        TASK:
        Create a 3-part strategic roadmap. BE CONCISE.
        
        CONSTRAINTS:
        - Executive Summary: Max 50 words.
        - Action Items: Max 15 words each.
        
        STRICTLY OUTPUT VALID JSON ONLY.
        
        Expected Format:
        {{
            "executive_summary": "Concise summary of the biggest opportunity.",
            "pillars": {{
                "content": ["Action 1", "Action 2"],
                "technical": ["Action 1", "Action 2"],
                "authority": ["Action 1", "Action 2"]
            }},
            "quick_wins": ["Win 1", "Win 2"]
        }}
        """
        return self._call_llm(prompt)

    def _call_llm(self, prompt):
        """Internal method to call the configured LLM provider"""
        try:
            print(f"    → Sending request to {self.provider} (Model: {self.model})...")
            if self.provider == 'gemini':
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.gemini_key}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                response = requests.post(url, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    # Gemini safety filters might block content
                    if 'candidates' in result and result['candidates']:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        return self._clean_json(text)
                    else:
                        return {"error": "Gemini returned no candidates (Safety blocked?)"}
                else:
                    return {"error": f"Gemini API Error: {response.text}"}

            elif self.provider == 'openrouter':
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://seo-gap-analyzer.com", 
                }
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful SEO assistant. You output only valid JSON."},
                        {"role": "user", "content": prompt}
                    ]
                }
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    text = result['choices'][0]['message']['content']
                    return self._clean_json(text)
                else:
                    return {"error": f"OpenRouter API Error: {response.text}"}
                    
        except Exception as e:
            return {"error": str(e)}

    def _clean_json(self, text):
        """Robustly extract JSON from text"""
        try:
            # 1. Try direct parsing
            return json.loads(text)
        except:
            # 2. Try stripping markdown code blocks
            clean_text = text.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(clean_text)
            except:
                # 3. Find first '{' and last '}'
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1:
                    json_str = text[start:end+1]
                    try:
                        return json.loads(json_str)
                    except:
                        pass
                
                # Fallback
                return {"text_response": text, "error": "Failed to parse JSON"}

# Quick test
if __name__ == "__main__":
    llm = LLMAnalyzer()
    print(f"Provider: {llm.provider}")
    if llm.provider:
        res = llm.generate_content_brief("best dog supplements india", ["dogseechew.in", "furballstory.com"])
        print(json.dumps(res, indent=2))
