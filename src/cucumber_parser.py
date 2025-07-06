"""
Cucumber/Gherkin parser to extract test steps and elements
"""
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from loguru import logger


@dataclass
class TestStep:
    """Represents a single test step"""
    step_type: str  # Given, When, Then, And, But
    step_text: str
    element_description: Optional[str] = None
    action: Optional[str] = None
    expected_text: Optional[str] = None


@dataclass
class TestScenario:
    """Represents a test scenario"""
    name: str
    steps: List[TestStep]
    tags: List[str] = None
    background_steps: List[TestStep] = None


class CucumberParser:
    """Parser for Cucumber/Gherkin feature files"""
    
    def __init__(self):
        self.action_patterns = {
            'click': r'click(?:\s+on)?(?:\s+the)?\s+(.+)',
            'type': r'(?:type|enter|input)\s+["\'](.+)["\'](?:\s+(?:in|into|on)(?:\s+the)?\s+(.+))?',
            'select': r'select\s+["\'](.+)["\'](?:\s+(?:from|in)(?:\s+the)?\s+(.+))?',
            'verify': r'(?:see|verify|check|should\s+see)\s+(.+)',
            'navigate': r'(?:go\s+to|navigate\s+to|visit)\s+(.+)',
            'wait': r'wait\s+(?:for\s+)?(.+)',
            'hover': r'hover\s+(?:over\s+)?(?:the\s+)?(.+)',
            'scroll': r'scroll\s+(?:to\s+)?(.+)',
            'clear': r'clear\s+(?:the\s+)?(.+)',
            'check': r'check\s+(?:the\s+)?(.+)',
            'uncheck': r'uncheck\s+(?:the\s+)?(.+)',
        }
    
    def parse_feature_file(self, file_path: str) -> List[TestScenario]:
        """Parse a Cucumber feature file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Feature file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_feature_content(content)
    
    def parse_feature_content(self, content: str) -> List[TestScenario]:
        """Parse Cucumber feature content"""
        scenarios = []
        lines = content.split('\n')
        
        current_scenario = None
        current_steps = []
        current_tags = []
        background_steps = []
        in_background = False
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Tags
            if line.startswith('@'):
                current_tags.extend(line.split())
                continue
            
            # Background
            if line.lower().startswith('background:'):
                in_background = True
                continue
            
            # Scenario
            if line.lower().startswith('scenario:') or line.lower().startswith('scenario outline:'):
                if current_scenario and current_steps:
                    current_scenario.steps = current_steps
                    scenarios.append(current_scenario)
                
                scenario_name = line.split(':', 1)[1].strip()
                current_scenario = TestScenario(
                    name=scenario_name,
                    steps=[],
                    tags=current_tags.copy(),
                    background_steps=background_steps.copy()
                )
                current_steps = []
                current_tags = []
                in_background = False
                continue
            
            # Steps
            if self._is_step_line(line):
                step = self._parse_step(line)
                if in_background:
                    background_steps.append(step)
                else:
                    current_steps.append(step)
        
        # Add the last scenario
        if current_scenario and current_steps:
            current_scenario.steps = current_steps
            scenarios.append(current_scenario)
        
        logger.info(f"Parsed {len(scenarios)} scenarios")
        return scenarios
    
    def _is_step_line(self, line: str) -> bool:
        """Check if line is a test step"""
        step_keywords = ['given', 'when', 'then', 'and', 'but']
        return any(line.lower().startswith(keyword) for keyword in step_keywords)
    
    def _parse_step(self, line: str) -> TestStep:
        """Parse a single test step"""
        parts = line.split(None, 1)
        if len(parts) < 2:
            return TestStep(step_type=parts[0], step_text=line)
        
        step_type = parts[0].lower()
        step_text = parts[1]
        
        # Extract action and element from step text
        action, element_description, expected_text = self._extract_action_and_element(step_text)
        
        return TestStep(
            step_type=step_type,
            step_text=step_text,
            element_description=element_description,
            action=action,
            expected_text=expected_text
        )
    
    def _extract_action_and_element(self, step_text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract action, element description, and expected text from step"""
        step_lower = step_text.lower()
        
        for action, pattern in self.action_patterns.items():
            match = re.search(pattern, step_lower)
            if match:
                groups = match.groups()
                
                if action == 'type':
                    # For type actions: type "text" into "element"
                    expected_text = groups[0] if groups[0] else None
                    element_description = groups[1] if len(groups) > 1 and groups[1] else None
                    return action, element_description, expected_text
                elif action == 'select':
                    # For select actions: select "option" from "dropdown"
                    expected_text = groups[0] if groups[0] else None
                    element_description = groups[1] if len(groups) > 1 and groups[1] else None
                    return action, element_description, expected_text
                else:
                    # For other actions: click "button", verify "text"
                    element_description = groups[0] if groups[0] else None
                    expected_text = groups[0] if action == 'verify' else None
                    return action, element_description, expected_text
        
        # If no pattern matches, try to extract quoted text as element
        quoted_matches = re.findall(r'["\']([^"\']+)["\']', step_text)
        if quoted_matches:
            return None, quoted_matches[0], None
        
        return None, None, None
    
    def get_all_elements(self, scenarios: List[TestScenario]) -> List[str]:
        """Get all unique element descriptions from scenarios"""
        elements = set()
        
        for scenario in scenarios:
            # Background steps
            if scenario.background_steps:
                for step in scenario.background_steps:
                    if step.element_description:
                        elements.add(step.element_description)
            
            # Scenario steps
            for step in scenario.steps:
                if step.element_description:
                    elements.add(step.element_description)
        
        return list(elements)
    
    def get_actions_summary(self, scenarios: List[TestScenario]) -> Dict[str, int]:
        """Get summary of all actions in scenarios"""
        actions = {}
        
        for scenario in scenarios:
            # Background steps
            if scenario.background_steps:
                for step in scenario.background_steps:
                    if step.action:
                        actions[step.action] = actions.get(step.action, 0) + 1
            
            # Scenario steps
            for step in scenario.steps:
                if step.action:
                    actions[step.action] = actions.get(step.action, 0) + 1
        
        return actions