"""
Smart XPath helpers for common UI patterns
"""
from typing import List, Dict, Optional


class XPathHelper:
    """Common XPath patterns for UI elements"""
    
    @staticmethod
    def button_by_text(text: str) -> str:
        """Find button by exact text"""
        return f"//button[text()='{text}']"
    
    @staticmethod
    def button_by_partial_text(text: str) -> str:
        """Find button by partial text"""
        return f"//button[contains(text(),'{text}')]"
    
    @staticmethod
    def link_by_text(text: str) -> str:
        """Find link by exact text"""
        return f"//a[text()='{text}']"
    
    @staticmethod
    def link_by_partial_text(text: str) -> str:
        """Find link by partial text"""
        return f"//a[contains(text(),'{text}')]"
    
    @staticmethod
    def input_by_placeholder(placeholder: str) -> str:
        """Find input by placeholder"""
        return f"//input[@placeholder='{placeholder}']"
    
    @staticmethod
    def input_by_label(label: str) -> str:
        """Find input by associated label"""
        return f"//input[@id=//label[text()='{label}']/@for]"
    
    @staticmethod
    def select_by_label(label: str) -> str:
        """Find select by associated label"""
        return f"//select[@id=//label[text()='{label}']/@for]"
    
    @staticmethod
    def element_by_text(text: str) -> str:
        """Find any element containing text"""
        return f"//*[contains(text(),'{text}')]"
    
    @staticmethod
    def element_by_attribute(tag: str, attr: str, value: str) -> str:
        """Find element by attribute"""
        return f"//{tag}[@{attr}='{value}']"
    
    @staticmethod
    def get_common_patterns() -> Dict[str, str]:
        """Get dictionary of common patterns"""
        return {
            "button_text": "//button[text()='{}']",
            "button_contains": "//button[contains(text(),'{}')]",
            "link_text": "//a[text()='{}']",
            "link_contains": "//a[contains(text(),'{}')]",
            "input_placeholder": "//input[@placeholder='{}']",
            "input_name": "//input[@name='{}']",
            "input_id": "//input[@id='{}']",
            "element_text": "//*[contains(text(),'{}')]",
            "element_class": "//*[@class='{}']",
            "element_id": "//*[@id='{}']"
        }
    
    @staticmethod
    def generate_xpath_variations(element_description: str) -> List[str]:
        """Generate multiple XPath variations for an element description"""
        variations = []
        text = element_description.strip()
        
        # Button variations
        if "button" in text.lower():
            button_text = text.replace("button", "").strip()
            variations.extend([
                f"//button[text()='{button_text}']",
                f"//button[contains(text(),'{button_text}')]",
                f"//input[@type='button' and @value='{button_text}']",
                f"//input[@type='submit' and @value='{button_text}']"
            ])
        
        # Link variations
        if "link" in text.lower():
            link_text = text.replace("link", "").strip()
            variations.extend([
                f"//a[text()='{link_text}']",
                f"//a[contains(text(),'{link_text}')]"
            ])
        
        # Input variations
        if "input" in text.lower() or "field" in text.lower():
            field_name = text.replace("input", "").replace("field", "").strip()
            variations.extend([
                f"//input[@placeholder='{field_name}']",
                f"//input[@name='{field_name}']",
                f"//input[@id='{field_name}']",
                f"//input[@id=//label[text()='{field_name}']/@for]"
            ])
        
        # Generic text search
        variations.append(f"//*[contains(text(),'{text}')]")
        
        return variations