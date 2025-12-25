"""
Pydantic Models for Portfolio Builder API.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class PortfolioStyle(str, Enum):
    """Available portfolio styles."""
    MODERN = "modern"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    BOLD = "bold"
    PROFESSIONAL = "professional"


class ColorScheme(BaseModel):
    """Color scheme for the portfolio."""
    primary: str = Field(default="#6366f1", description="Primary accent color")
    secondary: str = Field(default="#818cf8", description="Secondary color")
    accent: str = Field(default="#22d3ee", description="Accent color")
    background: str = Field(default="#0f172a", description="Background color")
    text: str = Field(default="#f8fafc", description="Text color")


class PortfolioGenerateRequest(BaseModel):
    """Request model for generating a portfolio."""
    user_prompt: str = Field(
        ..., 
        description="User's preferences for the portfolio (colors, style, features)",
        example="Create a modern portfolio with dark theme and subtle animations"
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


class WebsitePlanResponse(BaseModel):
    """Response showing the website plan."""
    style: str
    color_scheme: ColorScheme
    sections: List[str]
    font_family: str
    use_animations: bool
    dark_mode: bool


class ResumeParseResponse(BaseModel):
    """Response from resume parsing."""
    name: str
    email: Optional[str]
    phone: Optional[str]
    github: Optional[str]
    linkedin: Optional[str]
    skills: List[str]
    projects_count: int
    experience_count: int
    data_source: str = Field(..., description="LLM or UTILITY")
