import requests
from bs4 import BeautifulSoup
import time
import random
from pytrends.request import TrendReq

class KeywordEngine:
    def __init__(self, lang='ar', country='SA'):
        self.lang = lang
        self.country = country
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
    
    def get_suggestions(self, keyword):
        url = "http://suggestqueries.google.com/complete/search"
        params = {'client': 'firefox', 'q': keyword, 'hl': self.lang, 'gl': self.country}
        try:
            resp = self.session.get(url, params=params, timeout=5)
            return resp.json()[1] if resp.status_code == 200 else []
        except:
            return []
    
    def get_trends_score(self, keywords):
        try:
            pytrends = TrendReq(hl=f'{self.lang}-{self.country}', tz=360)
            sample = keywords[:5]
            pytrends.build_payload(sample, timeframe='today 12-m', geo=self.country)
            data = pytrends.interest_over_time()
            scores = {}
            for kw in sample:
                if kw in data.columns:
                    scores[kw] = round(data[kw].mean(), 2)
            return scores
        except:
            return {}
    
    def research(self, seed_keywords):
        results = []
        trends = self.get_trends_score(seed_keywords)
        
        for kw in seed_keywords:
            suggestions = self.get_suggestions(kw)
            # توسيع البحث بحرفين فقط لتسريع الأداء على الويب
            for letter in ['ا', 'ب']:
                suggestions.extend(self.get_suggestions(f"{kw} {letter}"))
                time.sleep(1)
            
            results.append({
                'seed_keyword': kw,
                'suggestions': list(set(suggestions)),
                'questions': [],
                'trends_score': trends.get(kw, 0)
            })
            time.sleep(2)
        
        return results
