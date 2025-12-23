"""
Preview Service for Portfolio Builder.

Handles generation of preview HTML and development server management.
"""

from pathlib import Path
from typing import List, Optional, Dict
import subprocess
import threading
import time

from portfolio_builder.core.state import GeneratedCode
from portfolio_builder.utils.file_utils import get_project_path


class PreviewService:
    """Service for generating previews of portfolio websites."""
    
    def __init__(self):
        self._running_servers: Dict[str, subprocess.Popen] = {}
        self._server_lock = threading.Lock()
    
    def generate_preview_html(self, files: List[GeneratedCode]) -> str:
        """
        Generate a standalone HTML preview of the portfolio.
        
        This creates a single HTML file that can be viewed without a dev server,
        useful for quick previews.
        
        Args:
            files: List of generated code files
            
        Returns:
            HTML string for preview
        """
        # Find key files
        app_content = ""
        css_content = ""
        components = {}
        
        for file in files:
            filename = file['filename'].lower()
            content = file['content']
            
            if 'app' in filename and filename.endswith('.jsx'):
                app_content = content
            elif filename.endswith('.css'):
                css_content = content
            elif file.get('component_type') == 'component':
                name = file['filename'].replace('.jsx', '')
                components[name] = content
        
        # Generate a simplified preview HTML
        preview_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Preview</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/lucide-react@0.263.1/dist/umd/lucide-react.min.js"></script>
    <style>
{css_content}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        // Lucide icons setup
        const {{ 
            Github, Linkedin, Mail, ExternalLink, Menu, X, 
            ChevronDown, ArrowRight, Code, Briefcase, GraduationCap,
            User, Phone, MapPin, Calendar, Star
        }} = lucideReact;
        
        // Components
{self._format_components_for_preview(components)}
        
        // App
{self._format_app_for_preview(app_content)}
        
        // Render
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
"""
        return preview_html
    
    def _format_components_for_preview(self, components: Dict[str, str]) -> str:
        """Format components for inline browser execution."""
        formatted = []
        
        for name, content in components.items():
            # Remove imports
            lines = content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Skip import statements
                if line.strip().startswith('import '):
                    continue
                # Skip export default
                if line.strip().startswith('export default'):
                    continue
                cleaned_lines.append(line)
            
            formatted.append('\n'.join(cleaned_lines))
        
        return '\n\n'.join(formatted)
    
    def _format_app_for_preview(self, app_content: str) -> str:
        """Format App component for inline browser execution."""
        if not app_content:
            return "const App = () => <div>Preview not available</div>;"
        
        lines = app_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip import statements
            if line.strip().startswith('import '):
                continue
            # Keep export default for App
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def start_dev_server(
        self, 
        project_id: str, 
        port: int = 3000
    ) -> Optional[str]:
        """
        Start a development server for a project.
        
        Note: This requires Node.js and npm to be installed.
        
        Args:
            project_id: Project identifier
            port: Port to run the server on
            
        Returns:
            Preview URL or None if failed
        """
        project_path = get_project_path(project_id)
        
        if not project_path.exists():
            print(f"Project not found: {project_id}")
            return None
        
        # Check if server is already running
        with self._server_lock:
            if project_id in self._running_servers:
                return f"http://localhost:{port}"
        
        try:
            # Install dependencies first
            subprocess.run(
                ['npm', 'install'],
                cwd=str(project_path),
                capture_output=True,
                timeout=120
            )
            
            # Start the dev server
            process = subprocess.Popen(
                ['npm', 'run', 'dev', '--', '--port', str(port)],
                cwd=str(project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                with self._server_lock:
                    self._running_servers[project_id] = process
                return f"http://localhost:{port}"
            else:
                print(f"Dev server failed to start for {project_id}")
                return None
            
        except Exception as e:
            print(f"Error starting dev server: {e}")
            return None
    
    def stop_dev_server(self, project_id: str) -> bool:
        """
        Stop a running development server.
        
        Args:
            project_id: Project identifier
            
        Returns:
            True if server was stopped
        """
        with self._server_lock:
            if project_id in self._running_servers:
                process = self._running_servers[project_id]
                process.terminate()
                
                # Wait for process to end
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                del self._running_servers[project_id]
                return True
        
        return False
    
    def stop_all_servers(self):
        """Stop all running development servers."""
        with self._server_lock:
            for project_id, process in list(self._running_servers.items()):
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
            
            self._running_servers.clear()
    
    def get_running_servers(self) -> List[str]:
        """Get list of project IDs with running servers."""
        with self._server_lock:
            return list(self._running_servers.keys())


# Singleton instance
_preview_service: Optional[PreviewService] = None


def get_preview_service() -> PreviewService:
    """Get the singleton PreviewService instance."""
    global _preview_service
    if _preview_service is None:
        _preview_service = PreviewService()
    return _preview_service
