"""
Final Assembler Agent for Portfolio Builder.

Combines all generated files into a complete, deployable portfolio.
"""

from typing import Dict, Any
from pathlib import Path

from portfolio_builder.core.state import PortfolioBuilderState, GeneratedCode
from portfolio_builder.core.prompts import README_TEMPLATE
from portfolio_builder.services.file_service import get_file_service
from portfolio_builder.services.preview_service import get_preview_service
from portfolio_builder.utils.file_utils import create_zip, get_project_path


def final_assembler_node(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Assemble all generated files into a complete portfolio project.
    
    This node:
    1. Creates the project folder structure
    2. Writes all generated files to disk
    3. Generates a README
    4. Creates a downloadable ZIP
    5. Optionally generates a preview
    
    Args:
        state: Current workflow state with generated_files
        
    Returns:
        Dict with output_path, zip_path, and preview_url
    """
    print("[Assembler] Starting final assembly...")
    
    project_id = state.get("project_id", "portfolio")
    generated_files = state.get("generated_files", [])
    website_plan = state.get("website_plan", {})
    resume_data = state.get("resume_parsed", {})
    validation_result = state.get("validation_result", {})
    
    # Add README to generated files
    readme_content = _generate_readme(resume_data, website_plan)
    generated_files.append(GeneratedCode(
        filename="README.md",
        filepath="README.md",
        content=readme_content,
        component_type="other"
    ))
    
    # Add .gitignore
    gitignore_content = _generate_gitignore()
    generated_files.append(GeneratedCode(
        filename=".gitignore",
        filepath=".gitignore",
        content=gitignore_content,
        component_type="config"
    ))
    
    # Get services
    file_service = get_file_service()
    preview_service = get_preview_service()
    
    # Save all files to disk
    print(f"[Assembler] Saving {len(generated_files)} files to disk...")
    output_path = file_service.save_generated_site(project_id, generated_files)
    
    # Create ZIP for download
    print("[Assembler] Creating ZIP archive...")
    zip_path = file_service.create_download_zip(project_id)
    
    # Generate preview HTML
    print("[Assembler] Generating preview...")
    try:
        preview_html = preview_service.generate_preview_html(generated_files)
        preview_path = Path(output_path) / "preview.html"
        with open(preview_path, 'w', encoding='utf-8') as f:
            f.write(preview_html)
        preview_url = str(preview_path)
    except Exception as e:
        print(f"[Assembler] Warning: Could not generate preview: {e}")
        preview_url = None
    
    # Log summary
    errors = validation_result.get("errors", [])
    warnings = validation_result.get("warnings", [])
    
    print("[Assembler] ===== ASSEMBLY COMPLETE =====")
    print(f"[Assembler] Project ID: {project_id}")
    print(f"[Assembler] Output path: {output_path}")
    print(f"[Assembler] ZIP path: {zip_path}")
    print(f"[Assembler] Files generated: {len(generated_files)}")
    print(f"[Assembler] Validation errors: {len(errors)}")
    print(f"[Assembler] Validation warnings: {len(warnings)}")
    
    # Determine workflow status
    workflow_status = "completed"
    if errors:
        workflow_status = "completed_with_errors"
    
    return {
        "output_path": output_path,
        "zip_path": zip_path,
        "preview_url": preview_url,
        "workflow_status": workflow_status,
        "current_node": "assembler"
    }


def _generate_readme(resume_data: Dict, website_plan: Dict) -> str:
    """Generate a README for the portfolio project."""
    name = resume_data.get("name", "Developer")
    
    # Build tech stack list
    tech_stack = website_plan.get("tech_stack", ["react", "tailwind"])
    tech_list = "\n".join([f"- {tech.title()}" for tech in tech_stack])
    
    return README_TEMPLATE.format(
        name=name,
        tech_stack=tech_list
    )


def _generate_gitignore() -> str:
    """Generate a .gitignore file."""
    return '''# Dependencies
node_modules/
.pnp
.pnp.js

# Build outputs
dist/
build/
.next/
out/

# Testing
coverage/

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Misc
*.pem
.vercel
'''
