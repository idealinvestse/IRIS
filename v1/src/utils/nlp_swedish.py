"""
IRIS v6.0 - Swedish NLP Utilities
Svensk språkbehandling och textanalys
"""

import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SwedishNLP:
    """
    Svensk språkbehandling och NLP-verktyg
    """
    
    def __init__(self):
        self.stopwords = self._load_swedish_stopwords()
        logger.info("🇸🇪 SwedishNLP initialiserad")
    
    def _load_swedish_stopwords(self) -> set:
        """Ladda svenska stoppord"""
        return {
            "och", "i", "att", "det", "som", "på", "är", "av", "för", "den",
            "till", "en", "ett", "om", "har", "de", "med", "kan", "var",
            "än", "så", "men", "från", "vid", "eller", "alla", "denna",
            "ingen", "något", "någon", "där", "här", "när", "hur", "vad",
            "varför", "ska", "skulle", "vara", "varit", "blir", "blev"
        }
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extrahera nyckelord från svensk text
        """
        # Tokenisera och rensa
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filtrera bort stoppord och korta ord
        keywords = [
            word for word in words 
            if word not in self.stopwords and len(word) > 3
        ]
        
        # Räkna frekvens
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sortera efter frekvens
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_keywords[:max_keywords]]
    
    def detect_intent(self, query: str) -> Dict[str, Any]:
        """
        Detektera intent från svensk fråga
        """
        query_lower = query.lower()
        
        intents = {
            "väder": ["väder", "temperatur", "regn", "sol", "moln", "smhi"],
            "finans": ["aktie", "omx", "börs", "kurs", "ekonomi", "finans"],
            "statistik": ["statistik", "scb", "befolkning", "siffror", "data"],
            "nyheter": ["nyheter", "nyhet", "aktuellt", "senaste", "händer"]
        }
        
        detected = {}
        for intent, keywords in intents.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                detected[intent] = score
        
        # Returnera dominant intent
        if detected:
            dominant = max(detected.items(), key=lambda x: x[1])
            return {
                "primary_intent": dominant[0],
                "confidence": dominant[1] / len(query.split()),
                "all_intents": detected
            }
        
        return {
            "primary_intent": "general",
            "confidence": 0.0,
            "all_intents": {}
        }
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """
        Enkel sammanfattning av svensk text
        """
        # Dela upp i meningar
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Ta första N meningar
        summary_sentences = sentences[:max_sentences]
        
        return '. '.join(summary_sentences) + '.'
    
    def is_question(self, text: str) -> bool:
        """
        Kontrollera om text är en fråga
        """
        question_words = ["vad", "hur", "när", "var", "vem", "varför", "vilken"]
        text_lower = text.lower()
        
        return (
            text.strip().endswith('?') or
            any(text_lower.startswith(word) for word in question_words)
        )
    
    def sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Enkel sentimentanalys för svensk text
        """
        positive_words = ["bra", "bäst", "fantastisk", "underbar", "excellent", "topp", "positiv"]
        negative_words = ["dålig", "värst", "hemsk", "usel", "negativ", "problem", "fel"]
        
        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = pos_count / (pos_count + neg_count) if (pos_count + neg_count) > 0 else 0
        elif neg_count > pos_count:
            sentiment = "negative"
            score = neg_count / (pos_count + neg_count) if (pos_count + neg_count) > 0 else 0
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_indicators": pos_count,
            "negative_indicators": neg_count
        }
