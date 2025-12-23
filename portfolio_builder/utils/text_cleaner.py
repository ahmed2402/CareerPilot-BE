"""
Text Cleaning Utilities for Portfolio Builder.

Functions for cleaning and preprocessing resume text and other content.
"""

import re
from typing import List, Optional, Tuple


def clean_resume_text(text: str) -> str:
    """
    Clean raw resume text by removing noise and normalizing formatting.
    
    Args:
        text: Raw resume text from PDF or other source
        
    Returns:
        Cleaned text ready for parsing
    """
    if not text:
        return ""
    
    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove excessive whitespace while preserving paragraph structure
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines to double newline
    
    # Remove common PDF artifacts
    text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', text)  # Remove extracted dates
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove leading/trailing whitespace from entire text
    text = text.strip()
    
    return text


def extract_urls(text: str) -> dict:
    """
    Extract various URLs from resume text.
    
    Args:
        text: Resume text to extract URLs from
        
    Returns:
        Dictionary with extracted URLs (email, linkedin, github, website)
    """
    urls = {
        'email': None,
        'linkedin': None,
        'github': None,
        'website': None,
        'twitter': None
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        urls['email'] = email_match.group(0).lower()
    
    # Extract LinkedIn
    linkedin_patterns = [
        r'(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9_-]+)/?',
        r'linkedin\.com/in/([A-Za-z0-9_-]+)'
    ]
    for pattern in linkedin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            username = match.group(1)
            urls['linkedin'] = f'https://linkedin.com/in/{username}'
            break
    
    # Extract GitHub
    github_patterns = [
        r'(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_-]+)/?(?!\S)',
        r'github\.com/([A-Za-z0-9_-]+)'
    ]
    for pattern in github_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            username = match.group(1)
            # Exclude common non-profile pages
            if username.lower() not in ['topics', 'trending', 'explore', 'settings']:
                urls['github'] = f'https://github.com/{username}'
                break
    
    # Extract Twitter/X
    twitter_patterns = [
        r'(?:https?://)?(?:www\.)?(?:twitter|x)\.com/([A-Za-z0-9_]+)/?',
        r'@([A-Za-z0-9_]+)'  # Twitter handle format
    ]
    for pattern in twitter_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            username = match.group(1)
            urls['twitter'] = f'https://twitter.com/{username}'
            break
    
    # Extract personal website (generic URL pattern)
    website_pattern = r'(?:https?://)?(?:www\.)?([A-Za-z0-9][A-Za-z0-9-]*\.)+[A-Za-z]{2,}(?:/[^\s]*)?'
    for match in re.finditer(website_pattern, text, re.IGNORECASE):
        url = match.group(0)
        url_lower = url.lower()
        
        # Skip known platforms
        skip_domains = ['linkedin', 'github', 'twitter', 'x.com', 'gmail', 'yahoo', 
                       'hotmail', 'outlook', 'coursera', 'udemy', 'credly', 'youtube']
        
        if not any(domain in url_lower for domain in skip_domains):
            if not url.startswith('http'):
                url = 'https://' + url
            urls['website'] = url
            break
    
    return urls


def extract_phone(text: str) -> Optional[str]:
    """
    Extract phone number from text.
    
    Args:
        text: Text to extract phone from
        
    Returns:
        Phone number string or None
    """
    # Common phone patterns (international and US formats)
    patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\+\d{1,3}[-.\s]?\d{10,12}'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group(0)
            # Basic validation - ensure it has enough digits
            digits = re.sub(r'\D', '', phone)
            if len(digits) >= 10:
                return phone
    
    return None


def normalize_skills(skills: List[str]) -> List[str]:
    """
    Normalize skill names for consistency.
    
    Args:
        skills: List of skill strings
        
    Returns:
        Normalized skill list
    """
    # Common skill name mappings
    skill_mappings = {
        'js': 'JavaScript',
        'javascript': 'JavaScript',
        'ts': 'TypeScript',
        'typescript': 'TypeScript',
        'py': 'Python',
        'python': 'Python',
        'node': 'Node.js',
        'nodejs': 'Node.js',
        'node.js': 'Node.js',
        'react': 'React',
        'reactjs': 'React',
        'react.js': 'React',
        'vue': 'Vue.js',
        'vuejs': 'Vue.js',
        'angular': 'Angular',
        'angularjs': 'Angular',
        'next': 'Next.js',
        'nextjs': 'Next.js',
        'next.js': 'Next.js',
        'aws': 'AWS',
        'gcp': 'Google Cloud',
        'azure': 'Azure',
        'ml': 'Machine Learning',
        'ai': 'Artificial Intelligence',
        'css': 'CSS',
        'html': 'HTML',
        'sql': 'SQL',
        'nosql': 'NoSQL',
        'mongodb': 'MongoDB',
        'postgres': 'PostgreSQL',
        'postgresql': 'PostgreSQL',
        'mysql': 'MySQL',
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'k8s': 'Kubernetes',
        'git': 'Git',
        'github': 'GitHub',
        'api': 'API Development',
        'rest': 'REST APIs',
        'graphql': 'GraphQL',
        'tailwind': 'Tailwind CSS',
        'tailwindcss': 'Tailwind CSS',
        'sass': 'Sass',
        'scss': 'Sass',
        'figma': 'Figma',
        'photoshop': 'Adobe Photoshop',
        'illustrator': 'Adobe Illustrator',
    }
    
    normalized = []
    seen = set()
    
    for skill in skills:
        # Clean up the skill
        skill_clean = skill.strip()
        if not skill_clean:
            continue
            
        # Check for mapping
        skill_lower = skill_clean.lower()
        mapped = skill_mappings.get(skill_lower, skill_clean)
        
        # Avoid duplicates (case-insensitive)
        if mapped.lower() not in seen:
            normalized.append(mapped)
            seen.add(mapped.lower())
    
    return normalized


def categorize_skills(skills: List[str]) -> dict:
    """
    Categorize skills into groups for better presentation.
    
    Args:
        skills: List of skill strings
        
    Returns:
        Dictionary with categorized skills
    """
    categories = {
        'Frontend': [],
        'Backend': [],
        'Database': [],
        'DevOps': [],
        'Languages': [],
        'Tools': [],
        'Soft Skills': [],
        'Other': []
    }
    
    # Keywords for each category
    category_keywords = {
        'Frontend': ['react', 'vue', 'angular', 'css', 'html', 'tailwind', 'sass', 
                    'bootstrap', 'next.js', 'nuxt', 'svelte', 'redux', 'webpack', 'vite'],
        'Backend': ['node', 'express', 'django', 'flask', 'spring', 'laravel', 'rails',
                   'fastapi', 'nest', 'graphql', 'rest', 'api', 'microservices'],
        'Database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                    'firebase', 'supabase', 'dynamodb', 'cassandra', 'neo4j'],
        'DevOps': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'ci/cd', 'jenkins',
                  'terraform', 'ansible', 'linux', 'nginx', 'apache'],
        'Languages': ['python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go',
                     'rust', 'kotlin', 'swift', 'ruby', 'php', 'scala'],
        'Tools': ['git', 'github', 'gitlab', 'jira', 'figma', 'photoshop', 'postman',
                 'vscode', 'intellij', 'slack', 'notion'],
        'Soft Skills': ['communication', 'leadership', 'teamwork', 'problem solving',
                       'time management', 'agile', 'scrum', 'collaboration']
    }
    
    for skill in skills:
        skill_lower = skill.lower()
        categorized = False
        
        for category, keywords in category_keywords.items():
            if any(keyword in skill_lower for keyword in keywords):
                categories[category].append(skill)
                categorized = True
                break
        
        if not categorized:
            categories['Other'].append(skill)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def extract_name(text: str) -> Optional[str]:
    """
    Attempt to extract a person's name from resume text.
    
    The name is typically at the very beginning of a resume.
    
    Args:
        text: Resume text
        
    Returns:
        Extracted name or None
    """
    lines = text.strip().split('\n')
    
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        
        # Skip empty lines and common headers
        if not line or len(line) < 3:
            continue
            
        skip_words = ['resume', 'curriculum', 'vitae', 'cv', 'portfolio', 
                     'contact', 'email', 'phone', 'address', 'objective',
                     'summary', 'experience', 'education', 'skills']
        
        if any(word in line.lower() for word in skip_words):
            continue
        
        # Check if line looks like a name (mostly letters and spaces)
        if re.match(r'^[A-Za-z\s\.\-\']+$', line):
            words = line.split()
            # Names typically have 2-4 words
            if 2 <= len(words) <= 4:
                # Each word should start with capital letter
                if all(w[0].isupper() for w in words if w):
                    return line
    
    return None
