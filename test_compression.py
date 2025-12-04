#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for history compression functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from chotbot.core.history_compressor import HistoryCompressor
from chotbot.core.llm_client import LLMClient
from chotbot.mcp.context_manager import MCPContextManager
from chotbot.mcp.processor import MCPProcessor

def test_compression_strategies():
    """Test different compression strategies."""
    print("Testing history compression strategies...")
    
    # Initialize components
    llm_client = LLMClient()
    compressor = HistoryCompressor(llm_client)
    
    # Create test conversation history
    test_history = [
        {"role": "user", "content": "Hello, I want to learn about your products."},
        {"role": "assistant", "content": "Hello! We have various products including intelligent assistants, data analysis tools, and enterprise solutions. What interests you?"},
        {"role": "user", "content": "I'm interested in the intelligent assistant. What can it do?"},
        {"role": "assistant", "content": "Our intelligent assistant can handle customer inquiries, automatically respond to common questions, schedule meetings, provide data analysis, etc. It supports multiple languages and can be customized according to your business needs."},
        {"role": "user", "content": "How long does customization take?"},
        {"role": "assistant", "content": "Customization time depends on specific requirements, usually 2-4 weeks. We first conduct requirement analysis, then develop a prototype, and finally test and deploy."},
        {"role": "user", "content": "What about pricing?"},
        {"role": "assistant", "content": "Pricing depends on features and usage scale. We have Basic, Professional, and Enterprise versions, ranging from $99 to $999 per month."},
        {"role": "user", "content": "What features does Enterprise include?"},
        {"role": "assistant", "content": "Enterprise includes all basic features, plus advanced analytics, API integration, custom model training, 24/7 technical support, etc."},
        {"role": "user", "content": "Can I try it first?"},
        {"role": "assistant", "content": "Of course! We offer a 14-day free trial where you can experience all features. You can register an account on our website to start the trial."},
        {"role": "user", "content": "What information is needed for registration?"},
        {"role": "assistant", "content": "Registration only requires your email address and company name. We will send a confirmation email to your inbox, click the confirmation link to complete registration."},
        {"role": "user", "content": "Okay, I'll think about it. Also, do you provide API interfaces?"},
        {"role": "assistant", "content": "Yes, we provide complete RESTful API interfaces that support integration with your existing systems. API documentation can be found in our developer center."},
        {"role": "user", "content": "Are there usage limits for the API?"},
        {"role": "assistant", "content": "Different versions have different API call limits. Basic: 1,000 calls per month, Professional: 10,000 calls per month, Enterprise: unlimited."}
    ]
    
    print("\nOriginal history: {} messages".format(len(test_history)))
    
    # Test summary strategy
    print("\n=== Testing Summary Strategy ===")
    try:
        compressed_summary = compressor.compress(test_history, strategy="summary", keep_last_n=3)
        print("Compressed to: {} messages".format(len(compressed_summary)))
        for msg in compressed_summary:
            print("- {}: {}...".format(msg['role'], msg['content'][:100]))
    except Exception as e:
        print("Error: {}".format(e))
    
    # Test extract_key_info strategy
    print("\n=== Testing Extract Key Info Strategy ===")
    try:
        compressed_extract = compressor.compress(test_history, strategy="extract_key_info", keep_last_n=3)
        print("Compressed to: {} messages".format(len(compressed_extract)))
        for msg in compressed_extract:
            print("- {}: {}...".format(msg['role'], msg['content'][:100]))
    except Exception as e:
        print("Error: {}".format(e))
    
    # Test hybrid strategy
    print("\n=== Testing Hybrid Strategy ===")
    try:
        compressed_hybrid = compressor.compress(test_history, strategy="hybrid", keep_last_n=3)
        print("Compressed to: {} messages".format(len(compressed_hybrid)))
        for msg in compressed_hybrid:
            print("- {}: {}...".format(msg['role'], msg['content'][:100]))
    except Exception as e:
        print("Error: {}".format(e))

def test_incremental_compression():
    """Test incremental compression."""
    print("\n\nTesting incremental compression...")
    
    llm_client = LLMClient()
    compressor = HistoryCompressor(llm_client)
    
    # Create longer test history
    test_history = []
    for i in range(20):
        test_history.append({"role": "user", "content": "This is user message {}".format(i+1)})
        test_history.append({"role": "assistant", "content": "This is assistant reply {}, providing detailed information about question {}.".format(i+1, i+1)})
    
    print("Original history: {} messages".format(len(test_history)))
    
    try:
        compressed_incremental = compressor.incremental_compress(test_history, chunk_size=5)
        print("Incrementally compressed to: {} messages".format(len(compressed_incremental)))
        
        # Count compressed vs original messages
        compressed_count = sum(1 for msg in compressed_incremental if msg.get('compressed'))
        original_count = len(compressed_incremental) - compressed_count
        print("- Compressed chunks: {}".format(compressed_count))
        print("- Original messages: {}".format(original_count))
        
    except Exception as e:
        print("Error: {}".format(e))

def test_context_manager_integration():
    """Test integration with MCPContextManager."""
    print("\n\nTesting context manager integration...")
    
    llm_client = LLMClient()
    processor = MCPProcessor(llm_client)
    
    print("Adding multiple messages to trigger compression...")
    
    # Add enough messages to trigger compression
    for i in range(10):
        user_input = "Test question {}: inquiry about product features".format(i+1)
        print("\nUser: {}".format(user_input))
        
        try:
            response = processor.interact(user_input)
            print("Assistant: {}...".format(response[:100]))
            
            # Show context status
            context = processor.get_context()
            history_count = len(processor.context_manager.get_history())
            print("Context size: {} messages | History size: {} messages".format(len(context), history_count))
            
        except Exception as e:
            print("Error: {}".format(e))
            break
    
    # Show compression stats
    stats = processor.context_manager.get_compression_stats()
    print("\nCompression stats: {}".format(stats))

def test_compression_trigger():
    """Test when compression should be triggered."""
    print("\n\nTesting compression trigger logic...")
    
    llm_client = LLMClient()
    compressor = HistoryCompressor(llm_client)
    
    # Test different history lengths
    for size in [5, 10, 15, 20, 25]:
        history = [{"role": "user", "content": "Message {}".format(i)} for i in range(size)]
        should_compress = compressor.should_compress(history, threshold_messages=15)
        print("History size {}: should_compress = {}".format(size, should_compress))
    
    # Test with token threshold
    long_message = "x" * 1000  # ~250 tokens
    history = [{"role": "user", "content": long_message} for _ in range(10)]  # ~2500 tokens
    
    should_compress = compressor.should_compress(history, threshold_messages=15, threshold_tokens=2000)
    print("\nLong messages (10x1000 chars): should_compress = {}".format(should_compress))

if __name__ == "__main__":
    print("=" * 60)
    print("History Compression Test Suite")
    print("=" * 60)
    
    try:
        test_compression_strategies()
        test_incremental_compression()
        test_context_manager_integration()
        test_compression_trigger()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print("\n\nError during tests: {}".format(e))
        import traceback
        traceback.print_exc()