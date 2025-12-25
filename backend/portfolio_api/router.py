"""
FastAPI Router for Portfolio Builder.

Features:
- Progress tracking during generation
- Live preview of built React app (npm build + serve dist)
- ZIP download
"""

import os
import sys
import shutil
import uuid
import subprocess
from pathlib import Path
from typing import Optional

# Add parent directory (CareerPilot-BE) to path for portfolio_builder imports
BACKEND_DIR = Path(__file__).parent.parent  # backend/
PROJECT_ROOT = BACKEND_DIR.parent  # CareerPilot-BE/
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse

from .models import (
    PortfolioGenerateRequest,
    PortfolioGenerateResponse,
    PortfolioStatusResponse,
)

router = APIRouter()

# Storage paths
STORAGE_DIR = Path(__file__).parent / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
ZIP_CODE_DIR = STORAGE_DIR / "zip_code"
PREVIEW_DIR = STORAGE_DIR / "preview"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
ZIP_CODE_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

# In-memory job status tracking (use Redis in production)
job_status = {}


def build_preview(project_id: str, source_path: str) -> Optional[str]:
    """
    Build the React app for preview using npm.
    
    Runs: npm install && npm run build
    Returns path to dist folder if successful.
    """
    try:
        preview_dest = PREVIEW_DIR / project_id
        
        # Copy source to preview directory
        if preview_dest.exists():
            shutil.rmtree(preview_dest)
        shutil.copytree(source_path, preview_dest)
        
        print(f"[Preview] Building project at: {preview_dest}")
        
        # Run npm install (shell=True for Windows compatibility)
        print("[Preview] Running npm install...")
        install_result = subprocess.run(
            "npm install",
            cwd=str(preview_dest),
            shell=True,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if install_result.returncode != 0:
            print(f"[Preview] npm install failed: {install_result.stderr}")
            return None
        
        print("[Preview] npm install completed")
        
        # Run npm run build
        print("[Preview] Running npm run build...")
        build_result = subprocess.run(
            "npm run build",
            cwd=str(preview_dest),
            shell=True,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if build_result.returncode != 0:
            print(f"[Preview] npm build failed: {build_result.stderr}")
            return None
        
        print("[Preview] npm build completed")
        
        # Check if dist folder was created
        dist_path = preview_dest / "dist"
        if dist_path.exists():
            print(f"[Preview] Build successful! Dist at: {dist_path}")
            return str(dist_path)
        
        print("[Preview] Warning: dist folder not found after build")
        return None
        
    except subprocess.TimeoutExpired:
        print("[Preview] Build timed out")
        return None
    except Exception as e:
        print(f"[Preview] Build error: {e}")
        return None


def run_portfolio_generation(project_id: str, resume_path: str, user_prompt: str):
    """Background task to run portfolio generation."""
    try:
        job_status[project_id] = {
            "status": "processing",
            "progress": 10,
            "current_step": "Starting portfolio generation..."
        }
        
        # Add path for portfolio_builder imports (needed in background thread)
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Update progress - Parsing resume
        job_status[project_id]["progress"] = 20
        job_status[project_id]["current_step"] = "Parsing resume with LLM..."
        
        # Import the complete pipeline from app.py
        from portfolio_builder.app import generate_portfolio
        
        # Update progress - Running workflow
        job_status[project_id]["progress"] = 30
        job_status[project_id]["current_step"] = "Running portfolio generation workflow..."
        
        # Run the complete pipeline (this takes ~2-3 mins)
        result = generate_portfolio(
            user_prompt=user_prompt,
            resume_file_path=resume_path,
            project_id=project_id
        )
        
        output_path = result.get("output_path")
        
        # Copy ZIP to our storage
        job_status[project_id]["progress"] = 80
        job_status[project_id]["current_step"] = "Copying ZIP file..."
        
        if result.get("zip_path") and os.path.exists(result["zip_path"]):
            dest_zip = ZIP_CODE_DIR / f"{project_id}.zip"
            shutil.copy2(result["zip_path"], dest_zip)
        
        # Build the React app for preview
        job_status[project_id]["progress"] = 85
        job_status[project_id]["current_step"] = "Building preview (npm install & build)..."
        
        preview_path = None
        if output_path and os.path.exists(output_path):
            preview_path = build_preview(project_id, output_path)
        
        job_status[project_id] = {
            "status": "completed",
            "progress": 100,
            "current_step": "Done! Portfolio ready.",
            "result": {
                "success": result.get("success", False),
                "project_id": project_id,
                "message": "Portfolio generated successfully!" if result.get("success") else "Generation completed with issues",
                "output_path": output_path,
                "zip_download_url": f"/portfolio-builder/download/{project_id}",
                "preview_url": f"/portfolio-builder/preview/{project_id}" if preview_path else None,
                "errors": result.get("errors", []),
                "warnings": result.get("warnings", [])
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        job_status[project_id] = {
            "status": "failed",
            "progress": 0,
            "current_step": f"Error: {str(e)[:100]}",
            "result": {
                "success": False,
                "project_id": project_id,
                "message": f"Generation failed: {str(e)}",
                "errors": [str(e)],
                "warnings": []
            }
        }


@router.post("/generate", response_model=PortfolioGenerateResponse)
async def generate_portfolio_from_file(
    background_tasks: BackgroundTasks,
    resume_file: UploadFile = File(..., description="Resume file (PDF, DOCX, TXT)"),
    user_prompt: str = Form(
        default="Create a modern, professional portfolio website",
        description="Your preferences for the portfolio style, colors, features"
    )
):
    """
    Generate a portfolio website from an uploaded resume file.
    
    **Workflow:**
    1. Upload resume -> Saved to storage/uploads
    2. Background generation starts -> Track with /status/{project_id}
    3. React app is built -> Preview at /preview/{project_id}
    4. Download ZIP -> GET /download/{project_id}
    """
    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".doc", ".txt"}
    file_ext = os.path.splitext(resume_file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate project ID
    project_id = str(uuid.uuid4())[:8]
    
    # Save uploaded file
    upload_path = UPLOADS_DIR / f"{project_id}{file_ext}"
    
    try:
        content = await resume_file.read()
        with open(upload_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Initialize job status
    job_status[project_id] = {
        "status": "pending",
        "progress": 0,
        "current_step": "Queued for processing"
    }
    
    # Start background generation
    background_tasks.add_task(
        run_portfolio_generation,
        project_id,
        str(upload_path),
        user_prompt
    )
    
    return PortfolioGenerateResponse(
        success=True,
        project_id=project_id,
        message="Portfolio generation started. Use /status/{project_id} to track progress.",
        errors=[],
        warnings=[]
    )


@router.post("/generate-text", response_model=PortfolioGenerateResponse)
async def generate_portfolio_from_text(
    background_tasks: BackgroundTasks,
    request: PortfolioGenerateRequest
):
    """
    Generate a portfolio website from resume text (no file upload).
    """
    if not request.resume_text:
        raise HTTPException(status_code=400, detail="resume_text is required")
    
    project_id = str(uuid.uuid4())[:8]
    upload_path = UPLOADS_DIR / f"{project_id}.txt"
    
    try:
        with open(upload_path, "w", encoding="utf-8") as f:
            f.write(request.resume_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save text: {str(e)}")
    
    job_status[project_id] = {
        "status": "pending",
        "progress": 0,
        "current_step": "Queued for processing"
    }
    
    background_tasks.add_task(
        run_portfolio_generation,
        project_id,
        str(upload_path),
        request.user_prompt
    )
    
    return PortfolioGenerateResponse(
        success=True,
        project_id=project_id,
        message="Portfolio generation started. Use /status/{project_id} to track progress.",
        errors=[],
        warnings=[]
    )


@router.get("/status/{project_id}", response_model=PortfolioStatusResponse)
async def get_generation_status(project_id: str):
    """
    Check the status of a portfolio generation job.
    
    Poll this endpoint to track progress:
    - 0%: Queued
    - 10-30%: Starting, parsing resume
    - 30-80%: Generating portfolio (takes 2-3 mins)
    - 80-85%: Copying files
    - 85-100%: Building preview
    - 100%: Done (check result field)
    """
    if project_id not in job_status:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    status_data = job_status[project_id]
    
    return PortfolioStatusResponse(
        project_id=project_id,
        status=status_data.get("status", "unknown"),
        progress=status_data.get("progress", 0),
        current_step=status_data.get("current_step"),
        result=status_data.get("result")
    )


@router.get("/preview/{project_id}")
async def preview_portfolio(project_id: str):
    """
    Get live preview of the generated portfolio.
    
    This serves the built React app (from dist folder).
    
    **Usage in frontend:**
    ```html
    <iframe src="http://localhost:8000/portfolio-builder/preview/{project_id}" />
    ```
    """
    # Check for built dist/index.html in preview storage
    dist_index = PREVIEW_DIR / project_id / "dist" / "index.html"
    if dist_index.exists():
        return FileResponse(str(dist_index), media_type="text/html")
    
    # Check original output path from job status
    if project_id in job_status:
        result = job_status[project_id].get("result", {})
        if result:
            output_path = result.get("output_path")
            if output_path:
                dist_path = Path(output_path) / "dist" / "index.html"
                if dist_path.exists():
                    return FileResponse(str(dist_path), media_type="text/html")
    
    raise HTTPException(
        status_code=404, 
        detail=f"Preview not available for project {project_id}. Build may have failed or generation still in progress."
    )


@router.get("/preview/{project_id}/{path:path}")
async def serve_preview_files(project_id: str, path: str):
    """
    Serve all files from the dist folder (assets, JS, CSS, etc).
    
    With base: './' in vite.config.js, the built HTML requests:
    - ./assets/index-xxxx.js
    - ./assets/index-xxxx.css
    
    Which the browser resolves to /portfolio-builder/preview/{id}/assets/...
    """
    # If path is empty (trailing slash case), serve index.html
    if not path or path == "":
        path = "index.html"
    
    # Try PREVIEW_DIR first (where we copy and build)
    dist_path = PREVIEW_DIR / project_id / "dist" / path
    if dist_path.exists() and dist_path.is_file():
        # Determine content type based on extension
        content_type = "application/octet-stream"
        if path.endswith(".html"):
            content_type = "text/html"
        elif path.endswith(".css"):
            content_type = "text/css"
        elif path.endswith(".js"):
            content_type = "application/javascript"
        elif path.endswith(".json"):
            content_type = "application/json"
        elif path.endswith(".png"):
            content_type = "image/png"
        elif path.endswith(".jpg") or path.endswith(".jpeg"):
            content_type = "image/jpeg"
        elif path.endswith(".svg"):
            content_type = "image/svg+xml"
        elif path.endswith(".ico"):
            content_type = "image/x-icon"
        elif path.endswith(".woff2"):
            content_type = "font/woff2"
        elif path.endswith(".woff"):
            content_type = "font/woff"
        
        return FileResponse(str(dist_path), media_type=content_type)
    
    # Fallback: try original output path from job status
    if project_id in job_status:
        result = job_status[project_id].get("result", {})
        if result:
            output_path = result.get("output_path")
            if output_path:
                fallback_path = Path(output_path) / "dist" / path
                if fallback_path.exists() and fallback_path.is_file():
                    return FileResponse(str(fallback_path))
    
    raise HTTPException(status_code=404, detail=f"File not found: {path}")


@router.get("/download/{project_id}")
async def download_portfolio_zip(project_id: str):
    """
    Download the generated portfolio as a ZIP file.
    """
    zip_path = ZIP_CODE_DIR / f"{project_id}.zip"
    
    if not zip_path.exists():
        if project_id in job_status:
            status = job_status[project_id].get("status")
            if status == "processing":
                raise HTTPException(status_code=202, detail="Generation still in progress")
            elif status == "failed":
                raise HTTPException(status_code=500, detail="Generation failed")
        
        raise HTTPException(status_code=404, detail=f"ZIP file not found for project {project_id}")
    
    return FileResponse(
        path=str(zip_path),
        filename=f"portfolio_{project_id}.zip",
        media_type="application/zip"
    )


@router.delete("/cleanup/{project_id}")
async def cleanup_project(project_id: str):
    """Clean up all files for a project."""
    cleaned = []
    
    # Clean uploads
    for ext in [".pdf", ".docx", ".doc", ".txt"]:
        upload_file = UPLOADS_DIR / f"{project_id}{ext}"
        if upload_file.exists():
            upload_file.unlink()
            cleaned.append(str(upload_file))
    
    # Clean ZIP
    zip_file = ZIP_CODE_DIR / f"{project_id}.zip"
    if zip_file.exists():
        zip_file.unlink()
        cleaned.append(str(zip_file))
    
    # Clean preview
    preview_dir = PREVIEW_DIR / project_id
    if preview_dir.exists():
        shutil.rmtree(preview_dir)
        cleaned.append(str(preview_dir))
    
    # Remove from job status
    if project_id in job_status:
        del job_status[project_id]
    
    return {"message": f"Cleaned up {len(cleaned)} items", "items": cleaned}
