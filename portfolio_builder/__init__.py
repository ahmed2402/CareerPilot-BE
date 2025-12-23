"""
Portfolio Builder Package

A LangGraph-based multi-agent system for generating portfolio websites
from user prompts and resume data.
"""

from portfolio_builder.app import (
    generate_portfolio,
    generate_portfolio_from_file,
    generate_portfolio_from_text
)

__version__ = "1.0.0"

__all__ = [
    "generate_portfolio",
    "generate_portfolio_from_file",
    "generate_portfolio_from_text"
]
