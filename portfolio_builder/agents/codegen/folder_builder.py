"""
Folder Builder - 100% Hardcoded filesystem and config generation.

❌ NOT LLM-based (IMPORTANT)
Folder structures must be deterministic.
LLMs should never create filesystem logic.
"""

import json
from typing import Dict, Any, List

from portfolio_builder.core.state import GeneratedCode
from portfolio_builder.core.logger import get_logger

logger = get_logger("folder_builder")


def generate_project_structure(
    website_plan: Dict,
    resume_data: Dict
) -> List[GeneratedCode]:
    """
    Generate all project configuration and structure files.
    
    This is 100% HARDCODED - no LLM involvement.
    
    Files generated:
    - package.json
    - vite.config.js
    - index.html
    - README.md
    - .gitignore
    
    Args:
        website_plan: Website plan (for metadata only)
        resume_data: Resume data (for name/title only)
        
    Returns:
        List of GeneratedCode for config files
    """
    logger.info("="*60)
    logger.info("PROJECT STRUCTURE GENERATION (100% HARDCODED)")
    logger.info("="*60)
    logger.info("  ❌ No LLM involvement - deterministic output")
    
    generated_files = []
    
    # package.json
    package_json = _generate_package_json(website_plan)
    generated_files.append(GeneratedCode(
        filename="package.json",
        filepath="package.json",
        content=package_json,
        component_type="config"
    ))
    logger.info("  ✓ package.json [HARDCODED]")
    
    # vite.config.js
    vite_config = _generate_vite_config()
    generated_files.append(GeneratedCode(
        filename="vite.config.js",
        filepath="vite.config.js",
        content=vite_config,
        component_type="config"
    ))
    logger.info("  ✓ vite.config.js [HARDCODED]")
    
    # index.html
    index_html = _generate_index_html(resume_data)
    generated_files.append(GeneratedCode(
        filename="index.html",
        filepath="index.html",
        content=index_html,
        component_type="page"
    ))
    logger.info("  ✓ index.html [HARDCODED]")
    
    # README.md
    readme = _generate_readme(resume_data)
    generated_files.append(GeneratedCode(
        filename="README.md",
        filepath="README.md",
        content=readme,
        component_type="doc"
    ))
    logger.info("  ✓ README.md [HARDCODED]")
    
    # .gitignore
    gitignore = _generate_gitignore()
    generated_files.append(GeneratedCode(
        filename=".gitignore",
        filepath=".gitignore",
        content=gitignore,
        component_type="config"
    ))
    logger.info("  ✓ .gitignore [HARDCODED]")
    
    logger.info(f"\n--- Generated {len(generated_files)} config files ---")
    
    return generated_files


def _generate_package_json(website_plan: Dict) -> str:
    """Generate package.json with fixed dependencies."""
    use_animations = website_plan.get("use_animations", True)
    
    dependencies = {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "lucide-react": "^0.263.1"
    }
    
    if use_animations:
        dependencies["framer-motion"] = "^10.16.0"
    
    package = {
        "name": "portfolio",
        "private": True,
        "version": "1.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": dependencies,
        "devDependencies": {
            "@vitejs/plugin-react": "^4.0.0",
            "autoprefixer": "^10.4.14",
            "postcss": "^8.4.24",
            "tailwindcss": "^3.3.2",
            "vite": "^4.4.0"
        }
    }
    
    return json.dumps(package, indent=2)


def _generate_vite_config() -> str:
    """Generate vite.config.js - always the same structure."""
    return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',
})
"""


def _generate_index_html(resume_data: Dict) -> str:
    """Generate index.html with dynamic title."""
    name = resume_data.get("name", "Portfolio")
    
    return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{name}'s Portfolio - Showcasing skills and projects" />
    <title>{name} | Portfolio</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
'''


def _generate_readme(resume_data: Dict) -> str:
    """Generate README.md with project info."""
    name = resume_data.get("name", "Developer")
    
    return f'''# {name}'s Portfolio Website

A modern, responsive portfolio website built with React and Tailwind CSS.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## 📁 Project Structure

```
├── src/
│   ├── components/     # React components
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
└── package.json        # Dependencies
```

## 🛠️ Built With

- React
- Tailwind CSS
- Vite
- Lucide Icons

## 📝 Customization

- Update content in component files under `src/components/`
- Modify colors in `tailwind.config.js` and `src/index.css`
- Add images to `public/` folder

## 📄 License

MIT License - feel free to use this for your own portfolio!

---
Generated with ❤️ by Auto Portfolio Builder
'''


def _generate_gitignore() -> str:
    """Generate .gitignore for React/Vite project."""
    return """# Dependencies
node_modules/

# Build output
dist/
build/

# Local env files
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Cache
.cache/
"""


# ============================================================
# Folder structure constants (never changes)
# ============================================================
PROJECT_FOLDERS = [
    "src",
    "src/components",
    "public",
]

REQUIRED_FILES = [
    "package.json",
    "vite.config.js",
    "tailwind.config.js",
    "postcss.config.js",
    "index.html",
    "src/main.jsx",
    "src/App.jsx",
    "src/index.css",
    ".gitignore",
    "README.md",
]
