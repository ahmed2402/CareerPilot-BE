"""
Pydantic Models for Portfolio Builder API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PortfolioGenerateRequest(BaseModel):
    """Request model for generating a portfolio from text."""
    user_prompt: str = Field(
        ..., 
        description="User's preferences for the portfolio (colors, style, features)",
        example="Create a modern portfolio with yellow background and black text"
    )
    resume_text: Optional[str] = Field(
        default=None,
        description="Raw resume text (alternative to file upload)"
    )


class PortfolioGenerateResponse(BaseModel):
    """Response model for portfolio generation."""
    success: bool = Field(..., description="Whether generation was successful")
    project_id: str = Field(..., description="Unique project identifier")
    message: str = Field(..., description="Status message")
    output_path: Optional[str] = Field(default=None, description="Path to generated files")
    zip_download_url: Optional[str] = Field(default=None, description="URL to download ZIP")
    preview_url: Optional[str] = Field(default=None, description="URL to preview the site")
    errors: List[str] = Field(default=[], description="List of errors if any")
    warnings: List[str] = Field(default=[], description="List of warnings if any")


class PortfolioStatusResponse(BaseModel):
    """Response model for checking portfolio status."""
    project_id: str
    status: str = Field(..., description="Status: pending, processing, completed, failed")
    progress: int = Field(default=0, description="Progress percentage 0-100")
    current_step: Optional[str] = Field(default=None, description="Current processing step")
    result: Optional[PortfolioGenerateResponse] = Field(default=None)
