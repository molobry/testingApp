#!/usr/bin/env python3
"""
Main entry point for the AI-powered UI testing application
"""
import sys
import argparse
from pathlib import Path
from loguru import logger

from src.test_executor import TestExecutor
from config import settings


def setup_logging():
    """Configure logging"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level
    )
    logger.add(
        "logs/test_execution.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days"
    )


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI-powered UI testing with Playwright and Cucumber")
    parser.add_argument("feature_file", help="Path to the Cucumber feature file")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"], default="chromium", help="Browser type")
    parser.add_argument("--ai-provider", choices=["openai", "azure_openai", "anthropic"], help="AI provider to use")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    # Override settings with command line arguments
    if args.headless:
        settings.headless = True
    if args.browser:
        settings.browser_type = args.browser
    if args.ai_provider:
        settings.ai_provider = args.ai_provider
    if args.log_level:
        settings.log_level = args.log_level
    
    # Setup logging
    setup_logging()
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Validate feature file
    feature_file = Path(args.feature_file)
    if not feature_file.exists():
        logger.error(f"Feature file not found: {feature_file}")
        sys.exit(1)
    
    # Validate AI configuration
    if settings.ai_provider == "openai" and not settings.openai_api_key:
        logger.error("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
        sys.exit(1)
    elif settings.ai_provider == "azure_openai":
        if not settings.azure_openai_api_key:
            logger.error("Azure OpenAI API key not configured. Set AZURE_OPENAI_API_KEY environment variable.")
            sys.exit(1)
        if not settings.azure_openai_endpoint:
            logger.error("Azure OpenAI endpoint not configured. Set AZURE_OPENAI_ENDPOINT environment variable.")
            sys.exit(1)
        if not settings.azure_openai_deployment:
            logger.error("Azure OpenAI deployment not configured. Set AZURE_OPENAI_DEPLOYMENT environment variable.")
            sys.exit(1)
    elif settings.ai_provider == "anthropic" and not settings.anthropic_api_key:
        logger.error("Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)
    
    logger.info(f"Starting AI-powered UI testing")
    logger.info(f"Feature file: {feature_file}")
    logger.info(f"Browser: {settings.browser_type}")
    logger.info(f"Headless: {settings.headless}")
    logger.info(f"AI Provider: {settings.ai_provider}")
    
    try:
        # Execute tests
        executor = TestExecutor()
        results = executor.execute_feature_file(str(feature_file))
        
        # Exit with appropriate code
        failed_scenarios = sum(1 for result in results if not result.passed)
        if failed_scenarios > 0:
            logger.error(f"Tests failed: {failed_scenarios} scenarios failed")
            sys.exit(1)
        else:
            logger.info("All tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()