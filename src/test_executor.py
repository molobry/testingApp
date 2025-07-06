"""
Test execution engine that coordinates all components
"""
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cucumber_parser import CucumberParser, TestScenario, TestStep
from ai_client import AIElementDetector
from playwright_controller import PlaywrightController
from element_cache import ElementCache
from xpath_helpers import XPathHelper


@dataclass
class TestResult:
    """Result of test execution"""
    scenario_name: str
    passed: bool
    steps_executed: int
    steps_passed: int
    steps_failed: int
    error_message: Optional[str] = None
    execution_time: float = 0.0
    failed_steps: List[str] = None


class TestExecutor:
    """Main test execution engine"""
    
    def __init__(self):
        self.cucumber_parser = CucumberParser()
        self.ai_detector = AIElementDetector()
        self.playwright_controller = PlaywrightController()
        self.element_cache = ElementCache()
        self.xpath_helper = XPathHelper()
        
        # Statistics
        self.total_scenarios = 0
        self.passed_scenarios = 0
        self.failed_scenarios = 0
        self.cache_hits = 0
        self.ai_calls = 0
    
    def execute_feature_file(self, feature_file_path: str) -> List[TestResult]:
        """Execute all scenarios in a feature file"""
        logger.info(f"Starting execution of feature file: {feature_file_path}")
        
        try:
            # Parse feature file
            scenarios = self.cucumber_parser.parse_feature_file(feature_file_path)
            self.total_scenarios = len(scenarios)
            
            # Execute each scenario
            results = []
            for scenario in scenarios:
                result = self.execute_scenario(scenario)
                results.append(result)
                
                if result.passed:
                    self.passed_scenarios += 1
                else:
                    self.failed_scenarios += 1
            
            # Print summary
            self._print_execution_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute feature file: {e}")
            return []
        finally:
            self.playwright_controller.close_browser()
    
    def execute_scenario(self, scenario: TestScenario) -> TestResult:
        """Execute a single test scenario"""
        logger.info(f"Executing scenario: {scenario.name}")
        
        start_time = time.time()
        steps_executed = 0
        steps_passed = 0
        steps_failed = 0
        failed_steps = []
        error_message = None
        
        try:
            # Execute background steps first
            if scenario.background_steps:
                for step in scenario.background_steps:
                    success = self._execute_step(step)
                    steps_executed += 1
                    if success:
                        steps_passed += 1
                    else:
                        steps_failed += 1
                        failed_steps.append(f"Background: {step.step_text}")
            
            # Execute scenario steps
            for step in scenario.steps:
                success = self._execute_step(step)
                steps_executed += 1
                if success:
                    steps_passed += 1
                else:
                    steps_failed += 1
                    failed_steps.append(step.step_text)
                    
                    # Stop on first failure (optional - could be configurable)
                    if not success:
                        break
        
        except Exception as e:
            error_message = str(e)
            logger.error(f"Scenario execution failed: {e}")
        
        execution_time = time.time() - start_time
        passed = steps_failed == 0 and error_message is None
        
        return TestResult(
            scenario_name=scenario.name,
            passed=passed,
            steps_executed=steps_executed,
            steps_passed=steps_passed,
            steps_failed=steps_failed,
            error_message=error_message,
            execution_time=execution_time,
            failed_steps=failed_steps
        )
    
    def _execute_step(self, step: TestStep) -> bool:
        """Execute a single test step"""
        logger.info(f"Executing step: {step.step_text}")
        
        try:
            # Handle different step types
            if step.action == "navigate":
                return self._handle_navigate_step(step)
            elif step.action == "click":
                return self._handle_click_step(step)
            elif step.action == "type":
                return self._handle_type_step(step)
            elif step.action == "select":
                return self._handle_select_step(step)
            elif step.action == "verify":
                return self._handle_verify_step(step)
            elif step.action == "wait":
                return self._handle_wait_step(step)
            else:
                # Try to infer action from step text
                return self._handle_generic_step(step)
                
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return False
    
    def _handle_navigate_step(self, step: TestStep) -> bool:
        """Handle navigation steps"""
        url = step.element_description
        if not url:
            # Extract URL from step text
            import re
            url_match = re.search(r'["\']([^"\']+)["\']', step.step_text)
            if url_match:
                url = url_match.group(1)
        
        if url:
            return self.playwright_controller.navigate_to(url)
        return False
    
    def _handle_click_step(self, step: TestStep) -> bool:
        """Handle click steps"""
        if not step.element_description:
            return False
        
        selector = self._get_element_selector(step.element_description)
        if selector:
            return self.playwright_controller.click_element(selector["selector"], selector["type"])
        return False
    
    def _handle_type_step(self, step: TestStep) -> bool:
        """Handle type/input steps"""
        if not step.element_description or not step.expected_text:
            return False
        
        selector = self._get_element_selector(step.element_description)
        if selector:
            return self.playwright_controller.type_text(
                selector["selector"], 
                step.expected_text, 
                selector["type"]
            )
        return False
    
    def _handle_select_step(self, step: TestStep) -> bool:
        """Handle select steps"""
        if not step.element_description or not step.expected_text:
            return False
        
        selector = self._get_element_selector(step.element_description)
        if selector:
            return self.playwright_controller.select_option(
                selector["selector"], 
                step.expected_text, 
                selector["type"]
            )
        return False
    
    def _handle_verify_step(self, step: TestStep) -> bool:
        """Handle verification steps"""
        if not step.expected_text:
            return False
        
        # Try to find element containing the expected text
        selector = f"//*[contains(text(),'{step.expected_text}')]"
        return self.playwright_controller.find_element(selector, "xpath")
    
    def _handle_wait_step(self, step: TestStep) -> bool:
        """Handle wait steps"""
        if step.element_description:
            selector = self._get_element_selector(step.element_description)
            if selector:
                return self.playwright_controller.wait_for_element(
                    selector["selector"], 
                    selector["type"]
                )
        else:
            # Default wait
            time.sleep(2)
            return True
        return False
    
    def _handle_generic_step(self, step: TestStep) -> bool:
        """Handle generic steps by trying to infer action"""
        step_lower = step.step_text.lower()
        
        # Try to infer action from step text
        if "click" in step_lower and step.element_description:
            return self._handle_click_step(step)
        elif any(word in step_lower for word in ["type", "enter", "input"]) and step.element_description:
            return self._handle_type_step(step)
        elif "select" in step_lower and step.element_description:
            return self._handle_select_step(step)
        elif any(word in step_lower for word in ["see", "verify", "check"]):
            return self._handle_verify_step(step)
        elif "navigate" in step_lower or "go to" in step_lower:
            return self._handle_navigate_step(step)
        else:
            logger.warning(f"Unknown step type: {step.step_text}")
            return True  # Assume success for unknown steps
    
    def _get_element_selector(self, element_description: str) -> Optional[Dict[str, str]]:
        """Get element selector using cache or AI analysis"""
        current_url = self.playwright_controller.get_page_url()
        
        # Check cache first
        cached_result = self.element_cache.get(current_url, element_description)
        if cached_result:
            self.cache_hits += 1
            logger.info(f"Using cached selector for: {element_description}")
            return {
                "selector": cached_result["selector"],
                "type": cached_result["selector_type"]
            }
        
        # Try smart XPath patterns first
        xpath_variations = self.xpath_helper.generate_xpath_variations(element_description)
        for xpath in xpath_variations:
            if self.playwright_controller.find_element(xpath, "xpath"):
                logger.info(f"Found element with pattern: {xpath}")
                # Cache the successful selector
                self.element_cache.set(current_url, element_description, xpath, "xpath")
                return {"selector": xpath, "type": "xpath"}
        
        # Use AI analysis as fallback
        logger.info(f"Using AI analysis for: {element_description}")
        self.ai_calls += 1
        
        html_content = self.playwright_controller.get_page_html()
        ai_result = self.ai_detector.find_element_selector(html_content, element_description, current_url)
        
        if ai_result["success"] and ai_result["best_selector"]:
            selector = ai_result["best_selector"]
            selector_type = "xpath" if selector.startswith("//") or selector.startswith("xpath=") else "css"
            
            # Test the selector
            if self.playwright_controller.find_element(selector, selector_type):
                # Cache the successful selector
                self.element_cache.set(current_url, element_description, selector, selector_type)
                return {"selector": selector, "type": selector_type}
        
        logger.error(f"Could not find selector for: {element_description}")
        return None
    
    def _print_execution_summary(self, results: List[TestResult]) -> None:
        """Print execution summary"""
        logger.info("=" * 60)
        logger.info("TEST EXECUTION SUMMARY")
        logger.info("=" * 60)
        
        total_time = sum(result.execution_time for result in results)
        total_steps = sum(result.steps_executed for result in results)
        total_passed_steps = sum(result.steps_passed for result in results)
        total_failed_steps = sum(result.steps_failed for result in results)
        
        logger.info(f"Total Scenarios: {self.total_scenarios}")
        logger.info(f"Passed Scenarios: {self.passed_scenarios}")
        logger.info(f"Failed Scenarios: {self.failed_scenarios}")
        logger.info(f"Total Steps: {total_steps}")
        logger.info(f"Passed Steps: {total_passed_steps}")
        logger.info(f"Failed Steps: {total_failed_steps}")
        logger.info(f"Total Execution Time: {total_time:.2f}s")
        logger.info(f"Cache Hits: {self.cache_hits}")
        logger.info(f"AI Calls: {self.ai_calls}")
        
        if self.failed_scenarios > 0:
            logger.info("\nFAILED SCENARIOS:")
            for result in results:
                if not result.passed:
                    logger.info(f"  - {result.scenario_name}")
                    if result.failed_steps:
                        for failed_step in result.failed_steps:
                            logger.info(f"    * {failed_step}")
        
        logger.info("=" * 60)