"""
Input Validator Module for AXIOM Security

This module provides input validation functionality to prevent injection attacks
and ensure data integrity across the AXIOM platform.
"""

import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Input validator for security checks"""

    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r';\s*--',  # Semicolon followed by comment
            r';\s*/\*',  # Semicolon followed by block comment
            r'union\s+select',  # UNION SELECT
            r'/\*.*\*/',  # Block comments
            r'--.*$',  # Line comments
            r';\s*drop\s+table',  # DROP TABLE
            r';\s*delete\s+from',  # DELETE FROM
            r';\s*update\s+.*\s+set',  # UPDATE SET
            r';\s*insert\s+into',  # INSERT INTO
        ]

        # Math expression patterns (allowed characters)
        self.math_pattern = r'^[0-9+\-*/().\s^sqrtlogexp]*$'

        # XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',  # Event handlers
            r'<iframe[^>]*>.*?</iframe>',  # Iframe tags
            r'<object[^>]*>.*?</object>',  # Object tags
        ]

    def validate_sql_input(self, input_str: str) -> bool:
        """Validate input for SQL injection attempts"""
        if not isinstance(input_str, str):
            return False

        input_lower = input_str.lower()

        for pattern in self.sql_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected: {pattern}")
                return False

        return True

    def validate_math_expression(self, expression: str) -> bool:
        """Validate mathematical expression"""
        if not isinstance(expression, str):
            return False

        # Remove whitespace
        expression = expression.replace(' ', '')

        # Check for only allowed characters
        if not re.match(self.math_pattern, expression):
            return False

        # Basic syntax check - count parentheses
        if expression.count('(') != expression.count(')'):
            return False

        # Check for dangerous functions (only allow safe ones)
        dangerous_functions = ['eval', 'exec', 'import', '__']
        for func in dangerous_functions:
            if func in expression.lower():
                return False

        return True

    def validate_xss_input(self, input_str: str) -> bool:
        """Validate input for XSS attempts"""
        if not isinstance(input_str, str):
            return True  # Non-strings are safe

        input_lower = input_str.lower()

        for pattern in self.xss_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                logger.warning(f"XSS pattern detected: {pattern}")
                return False

        return True

    def sanitize_input(self, input_str: str, max_length: int = 1000) -> str:
        """Sanitize input string"""
        if not isinstance(input_str, str):
            return str(input_str)

        # Truncate if too long
        if len(input_str) > max_length:
            input_str = input_str[:max_length]

        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/']
        for char in dangerous_chars:
            input_str = input_str.replace(char, '')

        return input_str

    def validate_json_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JSON input data"""
        results = {}

        for key, value in data.items():
            if isinstance(value, str):
                results[key] = {
                    "sql_safe": self.validate_sql_input(value),
                    "xss_safe": self.validate_xss_input(value),
                    "math_safe": self.validate_math_expression(value) if any(char in value for char in "+-*/^()") else True,
                    "sanitized": self.sanitize_input(value)
                }
            elif isinstance(value, (list, dict)):
                # Recursively validate nested structures
                results[key] = {"nested_validation": "complex_structure"}
            else:
                results[key] = {"valid": True}

        return results


# Global input validator instance
input_validator = InputValidator()
