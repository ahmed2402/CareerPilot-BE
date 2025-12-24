"""
Logging configuration for Portfolio Builder.

Provides a simple, consistent logging interface for all modules.
"""

import logging
import sys

# Configure root logger for portfolio_builder
_logger = logging.getLogger("portfolio_builder")
_logger.setLevel(logging.INFO)

# Only add handler if not already added
if not _logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setLevel(logging.INFO)
    _formatter = logging.Formatter("[%(name)s] %(message)s")
    _handler.setFormatter(_formatter)
    _logger.addHandler(_handler)


def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        module_name: Name of the module (e.g., "resume_parser", "website_planner")
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"portfolio_builder.{module_name}")
