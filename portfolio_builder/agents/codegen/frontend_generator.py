"""
Frontend Code Generator Agent for Portfolio Builder.

Converts section content into actual React + Tailwind CSS code.
"""

import json
from typing import Dict, Any, List

from portfolio_builder.core.state import PortfolioBuilderState, GeneratedCode
from portfolio_builder.core.llm_config import get_code_llm
from portfolio_builder.core.prompts import (
    CODE_GENERATOR_SYSTEM_PROMPT,
    CODE_GENERATOR_COMPONENT_PROMPT,
    CODE_GENERATOR_APP_PROMPT
)
from portfolio_builder.utils.helpers import (
    safe_json_parse, 
    extract_code_from_response,
    format_component_name
)


def frontend_generator_node(state: PortfolioBuilderState) -> Dict[str, Any]:
    """
    Generate React + Tailwind code for all sections.
    """
    print("[FrontendGenerator] Starting code generation...")
    
    sections_content = state.get("sections_content", [])
    website_plan = state.get("website_plan", {})
    resume_data = state.get("resume_parsed", {})
    
    generated_files: List[GeneratedCode] = []
    
    # Get LLM for code generation
    try:
        llm = get_code_llm(temperature=0.2)
    except Exception as e:
        print(f"[FrontendGenerator] LLM not available: {e}")
        llm = None
    
    # Generate component for each section
    for section in sections_content:
        section_name = section.get("section_name", "")
        section_content = section.get("content", {})
        
        if not section_name:
            continue
        
        print(f"[FrontendGenerator] Generating {section_name} component...")
        
        component_code = _generate_section_component(
            llm, section_name, section_content, website_plan, resume_data
        )
        
        if component_code:
            component_name = format_component_name(section_name)
            generated_files.append(GeneratedCode(
                filename=f"{component_name}.jsx",
                filepath=f"src/components/{component_name}.jsx",
                content=component_code,
                component_type="component"
            ))
    
    # Generate App.jsx - use fallback to ensure correct imports
    print("[FrontendGenerator] Generating App.jsx...")
    app_code = _generate_fallback_app(sections_content, website_plan, resume_data)
    generated_files.append(GeneratedCode(
        filename="App.jsx",
        filepath="src/App.jsx",
        content=app_code,
        component_type="page"
    ))
    
    # Generate main.jsx entry point
    main_code = _generate_main_entry()
    generated_files.append(GeneratedCode(
        filename="main.jsx",
        filepath="src/main.jsx",
        content=main_code,
        component_type="page"
    ))
    
    # Generate index.css with Tailwind
    css_code = _generate_index_css(website_plan)
    generated_files.append(GeneratedCode(
        filename="index.css",
        filepath="src/index.css",
        content=css_code,
        component_type="style"
    ))
    
    # Generate configuration files
    config_files = _generate_config_files(website_plan, resume_data)
    generated_files.extend(config_files)
    
    print(f"[FrontendGenerator] Generated {len(generated_files)} files")
    
    return {
        "generated_files": generated_files,
        "current_node": "code_generator"
    }


def _generate_section_component(
    llm, 
    section_name: str, 
    section_content: Dict, 
    website_plan: Dict,
    resume_data: Dict
) -> str:
    """Generate a React component for a section."""
    # Always use template-based generation for reliability
    return _generate_template_component(section_name, section_content, website_plan, resume_data)


def _generate_template_component(
    section_name: str, 
    section_content: Dict, 
    website_plan: Dict,
    resume_data: Dict
) -> str:
    """Generate a proper component based on section type."""
    section_key = section_name.lower()
    
    # Route to specific template generators
    template_map = {
        "hero": _generate_hero_template,
        "about": _generate_about_template,
        "skills": _generate_skills_template,
        "projects": _generate_projects_template,
        "experience": _generate_experience_template,
        "contact": _generate_contact_template,
    }
    
    generator = template_map.get(section_key, _generate_generic_template)
    return generator(section_content, website_plan, resume_data)


def _generate_hero_template(content: Dict, plan: Dict, resume: Dict) -> str:
    """Generate Hero section component."""
    name = resume.get("name", "Developer")
    headline = content.get("headline", "Full Stack Developer")
    tagline = content.get("tagline", "Building amazing digital experiences")
    github = resume.get("github", "")
    linkedin = resume.get("linkedin", "")
    
    colors = plan.get("color_scheme", {})
    primary = colors.get("primary", "#6366f1")
    
    return f'''import React from 'react';
import {{ Github, Linkedin, Mail, ArrowDown }} from 'lucide-react';

const Hero = () => {{
  return (
    <section id="hero" className="min-h-screen flex items-center justify-center relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%239C92AC%22 fill-opacity=%220.05%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40"></div>
      
      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        <p className="text-lg md:text-xl text-gray-400 mb-4">Hi, I'm</p>
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-4">
          {name}
        </h1>
        <h2 className="text-2xl md:text-4xl font-semibold mb-6" style={{{{ color: '{primary}' }}}}>
          {headline}
        </h2>
        <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
          {tagline}
        </p>
        
        <div className="flex justify-center gap-4 mb-12">
          <a 
            href="#projects" 
            className="px-8 py-3 rounded-full font-semibold text-white transition-all hover:scale-105"
            style={{{{ backgroundColor: '{primary}' }}}}
          >
            View My Work
          </a>
          <a 
            href="#contact" 
            className="px-8 py-3 rounded-full font-semibold text-white border border-gray-600 hover:border-gray-400 transition-all"
          >
            Get In Touch
          </a>
        </div>
        
        <div className="flex justify-center gap-6">
          {github and f'<a href="{github}" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors"><Github size={{24}} /></a>' or ''}
          {linkedin and f'<a href="{linkedin}" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors"><Linkedin size={{24}} /></a>' or ''}
          <a href="#contact" className="text-gray-400 hover:text-white transition-colors">
            <Mail size={{24}} />
          </a>
        </div>
      </div>
      
      <a href="#about" className="absolute bottom-8 left-1/2 transform -translate-x-1/2 text-gray-400 animate-bounce">
        <ArrowDown size={{32}} />
      </a>
    </section>
  );
}};

export default Hero;
'''


def _generate_about_template(content: Dict, plan: Dict, resume: Dict) -> str:
    """Generate About section component."""
    name = resume.get("name", "Developer")
    bio = content.get("bio_paragraphs", [])
    bio_text = bio[0] if bio else f"Hi, I'm {name}. I'm passionate about creating amazing digital solutions."
    facts = content.get("key_facts", [])
    
    colors = plan.get("color_scheme", {})
    primary = colors.get("primary", "#6366f1")
    
    # Generate facts HTML
    facts_jsx = ""
    if facts:
        facts_items = []
        for fact in facts[:4]:
            facts_items.append(f'''
          <div className="text-center p-4">
            <p className="text-3xl font-bold" style={{{{ color: '{primary}' }}}}>{fact.get("value", "")}</p>
            <p className="text-gray-400">{fact.get("label", "")}</p>
          </div>''')
        facts_jsx = "\n".join(facts_items)
    
    return f'''import React from 'react';
import {{ User }} from 'lucide-react';

const About = () => {{
  return (
    <section id="about" className="py-20 px-4 bg-gray-800">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-white text-center mb-4">About Me</h2>
        <div className="w-24 h-1 mx-auto mb-12" style={{{{ backgroundColor: '{primary}' }}}}></div>
        
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="flex justify-center">
            <div className="w-64 h-64 rounded-full bg-gray-700 flex items-center justify-center border-4" style={{{{ borderColor: '{primary}' }}}}>
              <User size={{120}} className="text-gray-500" />
            </div>
          </div>
          
          <div>
            <p className="text-lg text-gray-300 leading-relaxed mb-6">
              {bio_text}
            </p>
            {len(bio) > 1 and f'<p className="text-lg text-gray-300 leading-relaxed">{bio[1]}</p>' or ''}
          </div>
        </div>
        
        {facts_jsx and f'''
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16">
          {facts_jsx}
        </div>
        ''' or ''}
      </div>
    </section>
  );
}};

export default About;
'''


def _generate_skills_template(content: Dict, plan: Dict, resume: Dict) -> str:
    """Generate Skills section component."""
    skills = resume.get("skills", [])
    categories = content.get("categories", [])
    
    colors = plan.get("color_scheme", {})
    primary = colors.get("primary", "#6366f1")
    
    # If no categories, create from skills list
    if not categories and skills:
        categories = [{"name": "Technologies", "skills": [{"name": s} for s in skills]}]
    
    # Generate skills cards
    skills_jsx = ""
    for cat in categories:
        cat_name = cat.get("name", "Skills")
        cat_skills = cat.get("skills", [])
        skill_tags = " ".join([f'<span key="{s.get("name", "")}" className="px-3 py-1 bg-gray-700 rounded-full text-sm text-gray-300">{s.get("name", s) if isinstance(s, dict) else s}</span>' for s in cat_skills])
        skills_jsx += f'''
        <div className="bg-gray-700/50 rounded-xl p-6">
          <h3 className="text-xl font-semibold text-white mb-4">{cat_name}</h3>
          <div className="flex flex-wrap gap-2">
            {skill_tags}
          </div>
        </div>'''
    
    return f'''import React from 'react';

const Skills = () => {{
  return (
    <section id="skills" className="py-20 px-4 bg-gray-900">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-white text-center mb-4">Skills & Technologies</h2>
        <div className="w-24 h-1 mx-auto mb-12" style={{{{ backgroundColor: '{primary}' }}}}></div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {skills_jsx or '<p className="text-gray-400 text-center col-span-full">Skills coming soon...</p>'}
        </div>
      </div>
    </section>
  );
}};

export default Skills;
'''


def _generate_projects_template(content: Dict, plan: Dict, resume: Dict) -> str:
    """Generate Projects section component."""
    projects = content.get("projects", resume.get("projects", []))
    
    colors = plan.get("color_scheme", {})
    primary = colors.get("primary", "#6366f1")
    
    # Generate project cards
    projects_jsx = ""
    for i, proj in enumerate(projects[:6]):
        title = proj.get("title", f"Project {i+1}")
        desc = proj.get("description", "An amazing project")
        techs = proj.get("technologies", [])
        link = proj.get("links", {}).get("live") or proj.get("link", "")
        github = proj.get("links", {}).get("github") or proj.get("github_link", "")
        
        tech_tags = " ".join([f'<span className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">{t}</span>' for t in techs[:4]])
        
        projects_jsx += f'''
          <div className="bg-gray-800 rounded-xl overflow-hidden hover:transform hover:scale-105 transition-transform duration-300">
            <div className="h-48 bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
              <span className="text-6xl">🚀</span>
            </div>
            <div className="p-6">
              <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
              <p className="text-gray-400 text-sm mb-4">{desc[:150]}</p>
              <div className="flex flex-wrap gap-2 mb-4">
                {tech_tags}
              </div>
              <div className="flex gap-4">
                {link and f'<a href="{link}" target="_blank" rel="noopener noreferrer" className="text-sm font-medium hover:underline" style={{{{ color: "{primary}" }}}}>Live Demo →</a>' or ''}
                {github and f'<a href="{github}" target="_blank" rel="noopener noreferrer" className="text-sm text-gray-400 hover:text-white">GitHub</a>' or ''}
              </div>
            </div>
          </div>'''
    
    return f'''import React from 'react';

const Projects = () => {{
  return (
    <section id="projects" className="py-20 px-4 bg-gray-800">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-white text-center mb-4">Featured Projects</h2>
        <div className="w-24 h-1 mx-auto mb-12" style={{{{ backgroundColor: '{primary}' }}}}></div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {projects_jsx or '<p className="text-gray-400 text-center col-span-full">Projects coming soon...</p>'}
        </div>
      </div>
    </section>
  );
}};

export default Projects;
'''


def _generate_experience_template(content: Dict, plan: Dict, resume: Dict) -> str:
    """Generate Experience section component."""
    experiences = content.get("experiences", resume.get("experience", []))
    
    colors = plan.get("color_scheme", {})
    primary = colors.get("primary", "#6366f1")
    
    # Generate experience items
    exp_jsx = ""
    for exp in experiences[:5]:
        company = exp.get("company", "Company")
        role = exp.get("role", "Position")
        duration = exp.get("duration", "")
        desc = exp.get("description", "")
        highlights = exp.get("highlights", [])
        
        highlights_li = " ".join([f'<li className="text-gray-400">{h}</li>' for h in highlights[:3]])
        
        exp_jsx += f'''
          <div className="relative pl-8 pb-12 border-l-2 border-gray-700 last:pb-0">
            <div className="absolute left-[-9px] top-0 w-4 h-4 rounded-full" style={{{{ backgroundColor: '{primary}' }}}}></div>
            <div className="bg-gray-800 rounded-xl p-6">
              <p className="text-sm text-gray-400 mb-1">{duration}</p>
              <h3 className="text-xl font-semibold text-white">{role}</h3>
              <p className="font-medium mb-3" style={{{{ color: '{primary}' }}}}>{company}</p>
              {desc and f'<p className="text-gray-400 mb-3">{desc}</p>' or ''}
              {highlights_li and f'<ul className="list-disc list-inside space-y-1">{highlights_li}</ul>' or ''}
            </div>
          </div>'''
    
    return f'''import React from 'react';

const Experience = () => {{
  return (
    <section id="experience" className="py-20 px-4 bg-gray-900">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-4xl font-bold text-white text-center mb-4">Experience</h2>
        <div className="w-24 h-1 mx-auto mb-12" style={{{{ backgroundColor: '{primary}' }}}}></div>
        
        <div className="space-y-0">
          {exp_jsx or '<p className="text-gray-400 text-center">Experience details coming soon...</p>'}
        </div>
      </div>
    </section>
  );
}};

export default Experience;
'''


def _generate_contact_template(content: Dict, plan: Dict, resume: Dict) -> str:
    """Generate Contact section component."""
    email = resume.get("email", "")
    github = resume.get("github", "")
    linkedin = resume.get("linkedin", "")
    
    colors = plan.get("color_scheme", {})
    primary = colors.get("primary", "#6366f1")
    
    return f'''import React from 'react';
import {{ Mail, Github, Linkedin, Send }} from 'lucide-react';

const Contact = () => {{
  return (
    <section id="contact" className="py-20 px-4 bg-gray-800">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl font-bold text-white mb-4">Get In Touch</h2>
        <div className="w-24 h-1 mx-auto mb-8" style={{{{ backgroundColor: '{primary}' }}}}></div>
        
        <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
          I'm always open to new opportunities and collaborations. 
          Feel free to reach out if you'd like to connect!
        </p>
        
        <div className="flex justify-center gap-8 mb-12">
          {email and f'''
          <a 
            href="mailto:{email}" 
            className="flex items-center gap-2 px-6 py-3 rounded-full text-white font-semibold hover:scale-105 transition-transform"
            style={{{{ backgroundColor: '{primary}' }}}}
          >
            <Mail size={{20}} />
            Email Me
          </a>''' or ''}
          {linkedin and f'''
          <a 
            href="{linkedin}" 
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-6 py-3 rounded-full text-white font-semibold border border-gray-600 hover:border-gray-400 transition-colors"
          >
            <Linkedin size={{20}} />
            LinkedIn
          </a>''' or ''}
        </div>
        
        <div className="flex justify-center gap-6">
          {github and f'<a href="{github}" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors"><Github size={{28}} /></a>' or ''}
          {linkedin and f'<a href="{linkedin}" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors"><Linkedin size={{28}} /></a>' or ''}
          {email and f'<a href="mailto:{email}" className="text-gray-400 hover:text-white transition-colors"><Mail size={{28}} /></a>' or ''}
        </div>
        
        <p className="mt-16 text-gray-500 text-sm">
          © 2024 {resume.get("name", "Portfolio")}. All rights reserved.
        </p>
      </div>
    </section>
  );
}};

export default Contact;
'''


def _generate_generic_template(content: Dict, plan: Dict, resume: Dict) -> str:
    """Generate a generic section component."""
    section_name = content.get("section_name", "Section")
    component_name = format_component_name(section_name)
    title = content.get("title", section_name.title())
    subtitle = content.get("subtitle", "")
    
    colors = plan.get("color_scheme", {})
    primary = colors.get("primary", "#6366f1")
    
    return f'''import React from 'react';

const {component_name} = () => {{
  return (
    <section id="{section_name.lower()}" className="py-20 px-4 bg-gray-900">
      <div className="max-w-6xl mx-auto text-center">
        <h2 className="text-4xl font-bold text-white mb-4">{title}</h2>
        <div className="w-24 h-1 mx-auto mb-8" style={{{{ backgroundColor: '{primary}' }}}}></div>
        <p className="text-xl text-gray-300">{subtitle}</p>
      </div>
    </section>
  );
}};

export default {component_name};
'''


def _generate_fallback_app(
    sections_content: List, 
    website_plan: Dict,
    resume_data: Dict
) -> str:
    """Generate the main App.jsx component with proper imports."""
    
    # Sort sections by order
    sections = sorted(sections_content, key=lambda x: x.get("order", 0))
    
    # Generate imports - CORRECT path to ./components/
    imports = []
    components = []
    nav_items = []
    
    for section in sections:
        name = section.get("section_name", "")
        if name:
            component_name = format_component_name(name)
            imports.append(f"import {component_name} from './components/{component_name}';")
            components.append(f"      <{component_name} />")
            nav_items.append(f'{{ id: "{name.lower()}", label: "{name.title()}" }}')
    
    imports_str = "\n".join(imports)
    components_str = "\n".join(components)
    nav_items_str = ", ".join(nav_items)
    
    colors = website_plan.get("color_scheme", {})
    primary = colors.get("primary", "#6366f1")
    
    return f'''import React from 'react';
import {{ Menu, X }} from 'lucide-react';
{imports_str}

const navItems = [{nav_items_str}];

function App() {{
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
  
  const scrollToSection = (id) => {{
    document.getElementById(id)?.scrollIntoView({{ behavior: 'smooth' }});
    setMobileMenuOpen(false);
  }};

  return (
    <div className="min-h-screen bg-gray-900">
      {{/* Navigation */}}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-900/90 backdrop-blur-sm border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <a href="#hero" className="text-xl font-bold text-white">Portfolio</a>
          
          {{/* Desktop Nav */}}
          <ul className="hidden md:flex items-center gap-8">
            {{navItems.map((item) => (
              <li key={{item.id}}>
                <button 
                  onClick={{() => scrollToSection(item.id)}}
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  {{item.label}}
                </button>
              </li>
            ))}}
          </ul>
          
          {{/* Mobile Menu Button */}}
          <button 
            className="md:hidden text-white"
            onClick={{() => setMobileMenuOpen(!mobileMenuOpen)}}
          >
            {{mobileMenuOpen ? <X size={{24}} /> : <Menu size={{24}} />}}
          </button>
        </div>
        
        {{/* Mobile Nav */}}
        {{mobileMenuOpen && (
          <div className="md:hidden bg-gray-800 border-t border-gray-700">
            <ul className="px-4 py-4 space-y-4">
              {{navItems.map((item) => (
                <li key={{item.id}}>
                  <button 
                    onClick={{() => scrollToSection(item.id)}}
                    className="text-gray-300 hover:text-white transition-colors block w-full text-left"
                  >
                    {{item.label}}
                  </button>
                </li>
              ))}}
            </ul>
          </div>
        )}}
      </nav>

      {{/* Sections */}}
      <main className="pt-16">
{components_str}
      </main>
    </div>
  );
}}

export default App;
'''


def _generate_main_entry() -> str:
    """Generate main.jsx entry point."""
    return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''


def _generate_index_css(website_plan: Dict) -> str:
    """Generate index.css with Tailwind directives."""
    colors = website_plan.get("color_scheme", {})
    font = website_plan.get("font_family", "Inter")
    
    return f'''@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family={font}:wght@300;400;500;600;700&display=swap');

:root {{
  --color-primary: {colors.get("primary", "#6366f1")};
  --color-secondary: {colors.get("secondary", "#818cf8")};
  --color-accent: {colors.get("accent", "#22d3ee")};
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

html {{
  scroll-behavior: smooth;
}}

body {{
  font-family: '{font}', sans-serif;
  background-color: #111827;
  color: #f9fafb;
  line-height: 1.6;
}}

/* Smooth scrolling offset for fixed nav */
section {{
  scroll-margin-top: 64px;
}}
'''


def _generate_config_files(website_plan: Dict, resume_data: Dict) -> List[GeneratedCode]:
    """Generate configuration files."""
    files = []
    
    # package.json
    dependencies = {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "lucide-react": "^0.263.1"
    }
    
    package_json = {
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
    
    files.append(GeneratedCode(
        filename="package.json",
        filepath="package.json",
        content=json.dumps(package_json, indent=2),
        component_type="config"
    ))
    
    # tailwind.config.js
    colors = website_plan.get("color_scheme", {})
    tailwind_config = f'''/** @type {{import('tailwindcss').Config}} */
export default {{
  content: [
    "./index.html",
    "./src/**/*.{{js,ts,jsx,tsx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: '{colors.get("primary", "#6366f1")}',
        secondary: '{colors.get("secondary", "#818cf8")}',
        accent: '{colors.get("accent", "#22d3ee")}',
      }},
      fontFamily: {{
        sans: ['{website_plan.get("font_family", "Inter")}', 'sans-serif'],
      }},
    }},
  }},
  plugins: [],
}}
'''
    files.append(GeneratedCode(
        filename="tailwind.config.js",
        filepath="tailwind.config.js",
        content=tailwind_config,
        component_type="config"
    ))
    
    # postcss.config.js
    postcss_config = '''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
    files.append(GeneratedCode(
        filename="postcss.config.js",
        filepath="postcss.config.js",
        content=postcss_config,
        component_type="config"
    ))
    
    # vite.config.js
    vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
'''
    files.append(GeneratedCode(
        filename="vite.config.js",
        filepath="vite.config.js",
        content=vite_config,
        component_type="config"
    ))
    
    # index.html
    name = resume_data.get("name", "Portfolio")
    index_html = f'''<!DOCTYPE html>
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
    files.append(GeneratedCode(
        filename="index.html",
        filepath="index.html",
        content=index_html,
        component_type="page"
    ))
    
    return files
