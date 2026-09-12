"""Configuration validation for HireLens backend."""

import os
from typing import Dict, List, Tuple


class ConfigValidator:
    """Validates required environment variables and provides helpful error messages."""
    
    REQUIRED_VARS = {
        "LLM_PROVIDER": ["openai", "gemini"],  # Must be one of these values
        "ENVIRONMENT": ["development", "production"],
    }
    
    CONDITIONAL_VARS = {
        "openai": ["OPENAI_API_KEY"],  # Required if LLM_PROVIDER=openai
        "gemini": ["GEMINI_API_KEY"],  # Required if LLM_PROVIDER=gemini
    }
    
    @staticmethod
    def validate() -> Tuple[bool, List[str]]:
        """
        Validates all required environment variables.
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required variables
        for var, allowed_values in ConfigValidator.REQUIRED_VARS.items():
            value = os.getenv(var)
            if not value:
                errors.append(f"Missing required env var: {var}")
            elif allowed_values and value not in allowed_values:
                errors.append(f"Invalid {var}='{value}'. Must be one of: {', '.join(allowed_values)}")
        
        # Check conditional variables
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if llm_provider in ConfigValidator.CONDITIONAL_VARS:
            for required_var in ConfigValidator.CONDITIONAL_VARS[llm_provider]:
                value = os.getenv(required_var)
                if not value or value.startswith("your_"):
                    errors.append(
                        f"Missing or invalid LLM credentials: {required_var}\n"
                        f"  Required for LLM_PROVIDER='{llm_provider}'\n"
                        f"  Please set {required_var} in your .env file"
                    )
        
        # Check database configuration
        db_type = os.getenv("DATABASE_TYPE", "sqlite").lower()
        if db_type == "postgresql":
            if not os.getenv("DATABASE_URL"):
                errors.append("DATABASE_URL required when DATABASE_TYPE=postgresql")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def print_validation_errors(errors: List[str]) -> None:
        """Pretty-prints validation errors."""
        if not errors:
            return
        
        print("\n" + "="*60)
        print("CONFIGURATION VALIDATION ERRORS")
        print("="*60)
        for i, error in enumerate(errors, 1):
            print(f"\n{i}. {error}")
        print("\n" + "="*60)
        print("Please check your .env file and try again.")
        print("Use .env.template as a reference.")
        print("="*60 + "\n")


if __name__ == "__main__":
    is_valid, errors = ConfigValidator.validate()
    if not is_valid:
        ConfigValidator.print_validation_errors(errors)
        exit(1)
    else:
        print("✓ Configuration validation passed!")
