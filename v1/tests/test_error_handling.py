"""
IRIS v6.0 - Error Handling Tests
Testar circuit breakers och felhantering
"""

import pytest
import asyncio
from src.utils.error_handling import (
    CircuitBreaker, CircuitBreakerConfig, CircuitBreakerState,
    CircuitBreakerOpenException, GracefulDegradation,
    retry_with_backoff, get_circuit_breaker
)

@pytest.mark.asyncio
class TestCircuitBreaker:
    """Test circuit breaker functionality"""
    
    async def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialisering"""
        breaker = CircuitBreaker("test_service")
        assert breaker.name == "test_service"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
    
    async def test_circuit_breaker_success(self):
        """Test framgångsrikt anrop genom circuit breaker"""
        breaker = CircuitBreaker("test_success")
        
        async def successful_function():
            return "success"
        
        result = await breaker.call(successful_function)
        assert result == "success"
        assert breaker.success_count == 1
        assert breaker.state == CircuitBreakerState.CLOSED
    
    async def test_circuit_breaker_opens_on_failures(self):
        """Test att circuit breaker öppnas vid fel"""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test_failure", config)
        
        async def failing_function():
            raise Exception("Test error")
        
        # Försök tills circuit breaker öppnas
        for i in range(3):
            try:
                await breaker.call(failing_function)
            except Exception:
                pass
        
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count >= 3
    
    async def test_circuit_breaker_blocks_when_open(self):
        """Test att circuit breaker blockerar när öppen"""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker("test_block", config)
        
        async def failing_function():
            raise Exception("Test error")
        
        # Öppna circuit breaker
        for i in range(2):
            try:
                await breaker.call(failing_function)
            except Exception:
                pass
        
        # Nästa anrop ska blockeras
        with pytest.raises(CircuitBreakerOpenException):
            await breaker.call(failing_function)
    
    async def test_circuit_breaker_statistics(self):
        """Test hämtning av statistik"""
        breaker = CircuitBreaker("test_stats")
        
        async def test_func():
            return "ok"
        
        await breaker.call(test_func)
        
        stats = breaker.get_statistics()
        assert stats["name"] == "test_stats"
        assert stats["success_count"] == 1
        assert stats["state"] == "closed"
    
    async def test_get_circuit_breaker(self):
        """Test global circuit breaker retrieval"""
        breaker = get_circuit_breaker("scb")
        assert breaker is not None
        assert breaker.name == "SCB"

class TestGracefulDegradation:
    """Test graceful degradation"""
    
    def test_fallback_response_generation(self):
        """Test generering av fallback-svar"""
        query = "Hur är vädret idag?"
        error = Exception("Service unavailable")
        
        fallback = GracefulDegradation.provide_fallback_response(query, error)
        
        assert fallback["typ"] == "fallback"
        assert fallback["original_fråga"] == query
        assert "fallback_svar" in fallback
        assert "väder" in fallback["fallback_svar"].lower()
    
    def test_fallback_intent_detection(self):
        """Test intent-detektion för fallback"""
        test_cases = [
            ("OMX kurs", "finans"),
            ("väder stockholm", "väder"),
            ("senaste nyheterna", "nyheter"),
            ("SCB statistik", "statistik")
        ]
        
        for query, expected_intent in test_cases:
            fallback = GracefulDegradation.provide_fallback_response(
                query, Exception("test")
            )
            assert expected_intent in fallback["fallback_svar"].lower() or \
                   expected_intent.upper() in fallback["fallback_svar"]

@pytest.mark.asyncio
class TestRetryWithBackoff:
    """Test retry with exponential backoff"""
    
    async def test_retry_success_after_failure(self):
        """Test att retry lyckas efter initial misslyckande"""
        attempts = []
        
        @retry_with_backoff(max_retries=3, base_delay=0.1)
        async def flaky_function():
            attempts.append(1)
            if len(attempts) < 2:
                raise Exception("Temporary error")
            return "success"
        
        result = await flaky_function()
        assert result == "success"
        assert len(attempts) == 2  # Misslyckas en gång, lyckas andra
    
    async def test_retry_exhaustion(self):
        """Test att retry ger upp efter max försök"""
        attempts = []
        
        @retry_with_backoff(max_retries=2, base_delay=0.1)
        async def always_failing():
            attempts.append(1)
            raise Exception("Persistent error")
        
        with pytest.raises(Exception):
            await always_failing()
        
        assert len(attempts) == 3  # Ursprungligt + 2 retry
