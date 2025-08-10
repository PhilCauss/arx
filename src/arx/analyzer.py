"""
Security analysis functionality for arx
"""

import json
import os
import re
from typing import Optional
import openai
from .models import SecurityAnalysis


class ArxSecurityAnalyzer:
    """Handles security analysis of packages"""
    
    def __init__(self, openai_api_key: Optional[str] = None, temp_dir: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.temp_dir = temp_dir or os.getenv('ARX_TEMP_DIR')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def analyze_pkgbuild(self, pkgbuild_content: str, package_name: str) -> SecurityAnalysis:
        """Analyze PKGBUILD for malicious intent using OpenAI"""
        if not self.openai_api_key:
            return SecurityAnalysis(
                score=50,
                malicious_intent=False,
                suspicious_patterns=["No OpenAI API key provided"],
                recommendations=["Set OPENAI_API_KEY environment variable for detailed analysis"],
                package_name_analysis="Analysis not available"
            )
        
        try:
            prompt = f"""
Analyze this PKGBUILD for potential malicious intent. Look for:
1. Suspicious commands in prepare(), build(), or install() functions
2. Unusual network requests or downloads
3. File system modifications outside of package directory
4. Execution of downloaded scripts
5. Hardcoded URLs or IP addresses
6. Unusual permissions or file operations

Package name: {package_name}

PKGBUILD content:
{pkgbuild_content}

Provide a JSON response with:
{{
    "score": <0-100>,
    "malicious_intent": <true/false>,
    "suspicious_patterns": ["pattern1", "pattern2"],
    "recommendations": ["rec1", "rec2"],
    "analysis": "detailed explanation"
}}
"""
            
            # Create OpenAI client
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are a security expert analyzing PKGBUILD files for malicious intent."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            analysis_text = response.choices[0].message.content
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                return SecurityAnalysis(
                    score=analysis_data.get('score', 50),
                    malicious_intent=analysis_data.get('malicious_intent', False),
                    suspicious_patterns=analysis_data.get('suspicious_patterns', []),
                    recommendations=analysis_data.get('recommendations', []),
                    package_name_analysis=analysis_data.get('analysis', '')
                )
            else:
                return SecurityAnalysis(
                    score=50,
                    malicious_intent=False,
                    suspicious_patterns=["Could not parse AI analysis"],
                    recommendations=["Manual review recommended"],
                    package_name_analysis=analysis_text
                )
                
        except Exception as e:
            return SecurityAnalysis(
                score=50,
                malicious_intent=False,
                suspicious_patterns=[f"Analysis failed: {str(e)}"],
                recommendations=["Manual review recommended"],
                package_name_analysis="Analysis failed"
            )
    
    def analyze_package_name(self, package_name: str) -> str:
        """Analyze package name for potential typosquatting or malicious naming"""
        suspicious_patterns = [
            r'^[0-9]+$',  # Pure numbers
            r'^[a-z0-9]{1,3}$',  # Very short names
            r'[0-9]{4,}',  # Many consecutive numbers
            r'[a-z]{10,}',  # Very long lowercase strings
        ]
        
        # Check for common typosquatting patterns
        common_packages = [
            # Web browsers
            'firefox', 'chrome', 'chromium', 'brave', 'edge', 'safari', 'opera',
            
            # Development tools
            'vscode', 'code', 'sublime', 'atom', 'vim', 'emacs', 'nano',
            'git', 'github', 'gitlab', 'bitbucket', 'svn',
            'node', 'npm', 'yarn', 'pnpm',
            'python', 'pip', 'conda', 'poetry',
            'java', 'maven', 'gradle', 'ant',
            'rust', 'cargo', 'rustc',
            'golang', 'go',
            'cpp', 'gcc', 'clang', 'make', 'cmake',
            'docker', 'podman', 'kubernetes', 'k8s', 'helm',
            'jenkins', 'travis', 'circleci', 'github-actions',
            
            # Media applications
            'vlc', 'mpv', 'mplayer', 'ffmpeg', 'gstreamer',
            'gimp', 'photoshop', 'inkscape', 'krita', 'blender',
            'audacity', 'audition', 'garageband', 'pro-tools',
            'obs', 'streamlabs', 'xsplit',
            'spotify', 'apple-music', 'youtube-music', 'tidal',
            'steam', 'epic', 'origin', 'uplay', 'gog',
            
            # Communication
            'discord', 'slack', 'teams', 'zoom', 'skype', 'telegram',
            'whatsapp', 'signal', 'threema', 'matrix',
            
            # Office & Productivity
            'libreoffice', 'openoffice', 'microsoft-office', 'word', 'excel',
            'powerpoint', 'outlook', 'onenote',
            'notion', 'evernote', 'onenote', 'trello', 'asana',
            
            # System tools
            'htop', 'top', 'iotop', 'nethogs', 'glances',
            'wget', 'curl', 'aria2', 'youtube-dl', 'yt-dlp',
            'rsync', 'scp', 'sftp', 'ssh', 'telnet',
            'nmap', 'wireshark', 'tcpdump', 'netstat',
            
            # Package managers
            'pacman', 'yay', 'paru', 'aurman', 'pamac',
            'apt', 'yum', 'dnf', 'zypper', 'brew',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite',
            'mariadb', 'oracle', 'sql-server',
            
            # Web servers
            'apache', 'nginx', 'lighttpd', 'caddy',
            'nodejs', 'php', 'ruby', 'django', 'flask',
            
            # Security tools
            'nmap', 'wireshark', 'metasploit', 'burp-suite',
            'john', 'hashcat', 'aircrack-ng', 'kali',
            
            # Virtualization
            'virtualbox', 'vmware', 'qemu', 'kvm', 'xen',
            'vagrant', 'ansible', 'terraform', 'puppet',
            
            # Cloud & DevOps
            'aws-cli', 'azure-cli', 'gcloud', 'kubectl',
            'terraform', 'ansible', 'chef', 'puppet',
            'jenkins', 'gitlab-ci', 'github-actions',
            
            # Gaming
            'steam', 'epic', 'origin', 'uplay', 'gog',
            'minecraft', 'roblox', 'unity', 'unreal-engine',
            
            # Social media
            'facebook', 'twitter', 'instagram', 'linkedin',
            'reddit', 'tiktok', 'snapchat', 'pinterest',
            
            # File sharing
            'dropbox', 'google-drive', 'onedrive', 'mega',
            'box', 'icloud', 'nextcloud', 'owncloud'
        ]
        
        analysis = []
        
        # Check for suspicious patterns
        for pattern in suspicious_patterns:
            if re.search(pattern, package_name):
                analysis.append(f"Suspicious pattern detected: {pattern}")
        
        # Check for typosquatting
        for common_pkg in common_packages:
            if package_name.lower() in common_pkg or common_pkg in package_name.lower():
                if package_name.lower() != common_pkg:
                    analysis.append(f"Potential typosquatting of '{common_pkg}'")
        
        if not analysis:
            return "Package name appears normal"
        else:
            return "; ".join(analysis)
