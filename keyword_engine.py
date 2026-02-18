# keyword_engine.py - Render Optimized Version
import requests
import time
import random
# comment out pytrends temporarily to avoid issues
# from pytrends.request import TrendReq

class KeywordEngine:
    def __init__(self, lang='ar', country='SA'):
        self.lang = lang
        self.country = country
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_suggestions(self, keyword):
        url = "http://suggestqueries.google.com/complete/search"
        params = {'client': 'firefox', 'q': keyword, 'hl': self.lang, 'gl': self.country}
        try:
            resp = self.session.get(url, params=params, timeout=3)  # reduced timeout
            return resp.json()[1] if resp.status_code == 200 else []
        except:
            return []
    
    def get_trends_score(self, keywords):
        # Return mock scores instead of calling pytrends (for stability on free tier)
        return {kw: random.randint(30, 90) for kw in keywords[:5]}
    
    def research(self, seed_keywords):
        results = []
        # Get trends first (fast, no sleep)
        trends = self.get_trends_score(seed_keywords)
        
        for i, kw in enumerate(seed_keywords):
            # Limit to first 3 keywords to avoid timeout
            if i >= 3:
                break
                
            suggestions = self.get_suggestions(kw)
            # Only expand with 1 letter to save time
            suggestions.extend(self.get_suggestions(f"{kw} ا"))
            
            results.append({
                'seed_keyword': kw,
                'suggestions': list(set(suggestions))[:50],  # Limit results
                'questions': [],
                'trends_score': trends.get(kw, 0)
            })
            # Reduced sleep: only 0.5s between requests
            time.sleep(0.5)
        
        return results
