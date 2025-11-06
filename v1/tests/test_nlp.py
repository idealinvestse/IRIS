"""
IRIS v6.0 - NLP Tests
Testar svensk språkbehandling
"""

import pytest
from src.utils.nlp_swedish import SwedishNLP

class TestSwedishNLP:
    """Test Swedish NLP utilities"""
    
    def test_nlp_initialization(self):
        """Test NLP initialisering"""
        nlp = SwedishNLP()
        assert nlp is not None
        assert len(nlp.stopwords) > 0
    
    def test_keyword_extraction(self):
        """Test nyckelords-extraktion"""
        nlp = SwedishNLP()
        text = "Stockholm är Sveriges huvudstad och största stad med över en miljon invånare"
        
        keywords = nlp.extract_keywords(text, max_keywords=5)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "stockholm" in keywords or "huvudstad" in keywords
        # Stoppord ska filtreras bort
        assert "och" not in keywords
        assert "är" not in keywords
    
    def test_intent_detection_weather(self):
        """Test intent-detektion för väder"""
        nlp = SwedishNLP()
        query = "Hur är vädret i Stockholm idag?"
        
        intent = nlp.detect_intent(query)
        
        assert intent["primary_intent"] == "väder"
        assert intent["confidence"] > 0
    
    def test_intent_detection_finance(self):
        """Test intent-detektion för finans"""
        nlp = SwedishNLP()
        query = "Vad är OMX kursen just nu?"
        
        intent = nlp.detect_intent(query)
        
        assert intent["primary_intent"] == "finans"
    
    def test_intent_detection_news(self):
        """Test intent-detektion för nyheter"""
        nlp = SwedishNLP()
        query = "Senaste nyheterna från Sverige"
        
        intent = nlp.detect_intent(query)
        
        assert intent["primary_intent"] == "nyheter"
    
    def test_intent_detection_statistics(self):
        """Test intent-detektion för statistik"""
        nlp = SwedishNLP()
        query = "SCB statistik om befolkningen"
        
        intent = nlp.detect_intent(query)
        
        assert intent["primary_intent"] == "statistik"
    
    def test_question_detection(self):
        """Test fråge-detektion"""
        nlp = SwedishNLP()
        
        assert nlp.is_question("Hur mår du?")
        assert nlp.is_question("Vad är klockan")
        assert nlp.is_question("Vem är statsminister?")
        assert not nlp.is_question("Jag mår bra")
        assert not nlp.is_question("Stockholm är huvudstaden")
    
    def test_text_summarization(self):
        """Test text-sammanfattning"""
        nlp = SwedishNLP()
        long_text = """
        Stockholm är Sveriges huvudstad. Det är också landets största stad.
        Staden har över en miljon invånare. Stockholm grundades på 1200-talet.
        Idag är det ett viktigt ekonomiskt och kulturellt centrum.
        """
        
        summary = nlp.summarize_text(long_text, max_sentences=2)
        
        assert len(summary) < len(long_text)
        assert "Stockholm" in summary
    
    def test_sentiment_analysis_positive(self):
        """Test sentimentanalys - positiv"""
        nlp = SwedishNLP()
        text = "Detta är fantastiskt bra och excellent!"
        
        sentiment = nlp.sentiment_analysis(text)
        
        assert sentiment["sentiment"] == "positive"
        assert sentiment["positive_indicators"] > 0
    
    def test_sentiment_analysis_negative(self):
        """Test sentimentanalys - negativ"""
        nlp = SwedishNLP()
        text = "Detta är dåligt och hemsk kvalitet"
        
        sentiment = nlp.sentiment_analysis(text)
        
        assert sentiment["sentiment"] == "negative"
        assert sentiment["negative_indicators"] > 0
    
    def test_sentiment_analysis_neutral(self):
        """Test sentimentanalys - neutral"""
        nlp = SwedishNLP()
        text = "Detta är en beskrivning av Stockholm"
        
        sentiment = nlp.sentiment_analysis(text)
        
        assert sentiment["sentiment"] == "neutral"
