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
        self.model = os.getenv('LLM_MODEL', 'google/gemini-pro' if self.provider == 'openrouter' else 'gemini-1.5-flash')

    def analyze_page_content(self, url, keyword, content_snippet=None):
        """Analyze a page for SEO optimization against a target keyword"""
        if not self.provider:
            return {"error": "No LLM API key found"}

        prompt = f"""
        Analyze this page for the target keyword: "{keyword}"
        URL: {url}
        
        Content Snippet:
        {content_snippet[:2000] if content_snippet else "Not provided"}
        
        Provide 3 specific, actionable SEO recommendations to improve ranking for this keyword.
        Focus on:
        1. Content gaps (what's missing?)
        2. User Intent alignment
        3. On-page optimization (title, headers)
        
        Format as JSON: {{ "recommendations": ["rec1", "rec2", "rec3"], "score": 0-100 }}
        """
        
        return self._call_llm(prompt)

    def generate_content_brief(self, keyword, competitors):
        """Generate a content brief to outrank competitors"""
        if not self.provider:
            return {"error": "No LLM API key found"}

        prompt = f"""
        Create an SEO content brief for the keyword: "{keyword}"
        
        Competitors Ranking:
        {', '.join(competitors)}
        
        Output JSON:
        {{
            "title_ideas": ["..."],
            "target_word_count": 1500,
            "headings_structure": ["H1...", "H2...", "H3..."],
            "unique_angle": "How to differentiate..."
        }}
        """
        
        return self._call_llm(prompt)

    def _call_llm(self, prompt):
        """Internal method to call the configured LLM provider"""
        try:
            if self.provider == 'gemini':
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.gemini_key}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    return self._clean_json(text)
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
                    "messages": [{"role": "user", "content": prompt}]
                }
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    text = result['choices'][0]['message']['content']
                    return self._clean_json(text)
                else:
                    return {"error": f"OpenRouter API Error: {response.text}"}
                    
        except Exception as e:
            return {"error": str(e)}

    def _clean_json(self, text):
        """Clean markdown formatting from JSON response"""
        try:
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except:
            return {"text_response": text}

# Quick test
if __name__ == "__main__":
    llm = LLMAnalyzer()
    print(f"Provider: {llm.provider}")
    if llm.provider:
        res = llm.generate_content_brief("best dog supplements india", ["dogseechew.in", "furballstory.com"])
        print(json.dumps(res, indent=2))
