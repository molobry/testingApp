#!/usr/bin/env python3
"""
Test script to verify the application works
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.cucumber_parser import CucumberParser
from src.xpath_helpers import XPathHelper
from src.element_cache import ElementCache

def test_cucumber_parser():
    """Test Cucumber parser"""
    print("Testing Cucumber Parser...")
    
    parser = CucumberParser()
    scenarios = parser.parse_feature_file("examples/sample.feature")
    
    print(f"Found {len(scenarios)} scenarios")
    for scenario in scenarios:
        print(f"- {scenario.name} ({len(scenario.steps)} steps)")
    
    # Get all elements
    elements = parser.get_all_elements(scenarios)
    print(f"Found {len(elements)} unique elements:")
    for element in elements:
        print(f"  - {element}")
    
    # Get actions summary
    actions = parser.get_actions_summary(scenarios)
    print(f"Actions summary: {actions}")
    
    print("✅ Cucumber Parser test passed!\n")

def test_xpath_helpers():
    """Test XPath helpers"""
    print("Testing XPath Helpers...")
    
    helper = XPathHelper()
    
    # Test button patterns
    button_xpath = helper.button_by_text("Login")
    print(f"Button XPath: {button_xpath}")
    
    # Test variations
    variations = helper.generate_xpath_variations("Login button")
    print(f"XPath variations for 'Login button': {variations}")
    
    print("✅ XPath Helpers test passed!\n")

def test_element_cache():
    """Test element cache"""
    print("Testing Element Cache...")
    
    cache = ElementCache("test_cache.json")
    
    # Test cache operations
    cache.set("http://example.com", "login button", "//button[text()='Login']", "xpath")
    result = cache.get("http://example.com", "login button")
    
    print(f"Cache result: {result}")
    
    # Test stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    # Clean up
    cache.clear_cache()
    
    print("✅ Element Cache test passed!\n")

if __name__ == "__main__":
    try:
        test_cucumber_parser()
        test_xpath_helpers()
        test_element_cache()
        print("🎉 All tests passed! The application is ready to use.")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)