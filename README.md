# AI-Powered UI Testing with Playwright and Cucumber

An intelligent UI testing framework that uses AI to automatically identify and interact with web elements based on natural language descriptions in Cucumber feature files.

## Features

- **AI-Powered Element Detection**: Uses OpenAI GPT-4 or Anthropic Claude to identify elements
- **DOM-Only Analysis**: Fast performance without screenshots
- **Smart Caching**: Stores successful selectors for future use
- **Cucumber Integration**: Write tests in natural language
- **Smart XPath Helpers**: Built-in patterns for common elements
- **Multi-Browser Support**: Chrome, Firefox, Safari via Playwright

## Quick Start

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
playwright install
```

2. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env with your AI API keys
```

3. **Run Tests**:
```bash
python main.py examples/sample.feature
```

## Configuration

### Environment Variables

- `AI_PROVIDER`: `openai` or `anthropic`
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `BROWSER_TYPE`: `chromium`, `firefox`, or `webkit`
- `HEADLESS`: `true` or `false`

### Command Line Options

```bash
python main.py feature_file.feature [OPTIONS]

Options:
  --headless          Run browser in headless mode
  --browser TYPE      Browser type (chromium, firefox, webkit)
  --ai-provider TYPE  AI provider (openai, anthropic)
  --log-level LEVEL   Log level (DEBUG, INFO, WARNING, ERROR)
```

## Writing Tests

Create `.feature` files using natural language:

```gherkin
Feature: User Login
  Background:
    Given I navigate to "https://example.com/login"

  Scenario: Successful login
    When I type "user@example.com" into "email field"
    And I type "password123" into "password field"
    And I click "Login button"
    Then I should see "Welcome back!"
```

## How It Works

1. **Parse Cucumber**: Extract test steps and element descriptions
2. **Check Cache**: Look for previously successful selectors
3. **Try Smart Patterns**: Use built-in XPath patterns
4. **AI Analysis**: Send DOM + description to AI for element detection
5. **Cache Results**: Store successful selectors for future use
6. **Execute Actions**: Use Playwright to interact with elements

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│ Cucumber Parser │    │ Test Executor   │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ XPath Helpers   │    │ Element Cache   │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ AI Detector     │    │ Playwright      │
└─────────────────┘    └─────────────────┘
```

## Performance

- **DOM-Only**: No screenshots for faster analysis
- **Smart Caching**: Reuses successful selectors
- **Pattern Matching**: Tries common patterns first
- **Fallback AI**: Uses AI only when needed

## Example Output

```
2024-01-01 10:00:00 | INFO | Starting AI-powered UI testing
2024-01-01 10:00:01 | INFO | Cache hit for: Login button
2024-01-01 10:00:02 | INFO | Using AI analysis for: email field
2024-01-01 10:00:03 | INFO | Cached selector for: email field -> //input[@type='email']

TEST EXECUTION SUMMARY
======================
Total Scenarios: 3
Passed Scenarios: 2
Failed Scenarios: 1
Cache Hits: 15
AI Calls: 3
Total Execution Time: 45.2s
```