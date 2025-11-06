import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.ai_providers.local_provider import LocalProvider
import asyncio

async def test_local_provider():
    print("Testing LocalProvider...")
    
    # Test initialization
    provider = LocalProvider()
    print(f"Provider name: {provider.get_provider_name()}")
    
    # Test basic analysis
    result = await provider.analyze("Test question", "")
    print(f"Analysis successful: {'svar' in result}")
    print(f"Response: {result['svar'][:100]}...")
    print(f"Tokens used: {result['tokens_used']}")
    print(f"Model: {result['modell']}")
    print(f"Provider: {result['provider']}")
    
    # Test with context
    context = "OMX Stockholm data shows financial trends"
    result2 = await provider.analyze("What's the stock market doing?", context)
    print(f"\nContext analysis successful: {'svar' in result2}")
    print(f"Response with context: {result2['svar'][:100]}...")
    
    # Test streaming
    print("\nTesting streaming...")
    chunks = []
    async for chunk in provider.analyze_stream("Stream test", ""):
        chunks.append(chunk)
    print(f"Streaming successful: {len(chunks) == 1}")
    print(f"Stream chunk length: {len(chunks[0])}")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_local_provider())
