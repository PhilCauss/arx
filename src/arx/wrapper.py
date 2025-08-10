"""
Yay wrapper functionality for arx
"""

import os
import subprocess
import tempfile
import shutil
from typing import List, Optional


class YayWrapper:
    """Wraps yay functionality"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.yay_path = self._find_yay()
        self.temp_dir = temp_dir or os.getenv('ARX_TEMP_DIR')
    
    def _find_yay(self) -> str:
        """Find yay executable"""
        # Check common locations
        possible_paths = ['yay', '/usr/bin/yay', '/usr/local/bin/yay']
        for path in possible_paths:
            if os.path.exists(path) or self._is_executable(path):
                return path
        raise FileNotFoundError("yay not found. Please install yay first.")
    
    def _is_executable(self, path: str) -> bool:
        """Check if a command is executable"""
        try:
            result = subprocess.run(['which', path], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_packages_to_install(self, args: List[str]) -> List[str]:
        """Extract package names from yay arguments"""
        packages = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ['-S', '--sync'] and i + 1 < len(args):
                # Handle -S flag
                i += 1
                while i < len(args) and not args[i].startswith('-'):
                    packages.append(args[i])
                    i += 1
            elif not arg.startswith('-') and arg not in ['install', 'remove', 'update']:
                # Direct package names
                packages.append(arg)
            i += 1
        return packages
    
    def get_pkgbuild_content(self, package_name: str) -> Optional[str]:
        """Get PKGBUILD content for a package"""
        temp_dir = None
        try:
            # Create temporary directory for arx
            if self.temp_dir:
                # Use custom temp directory
                temp_dir = os.path.join(self.temp_dir, f"arx_{package_name}")
                os.makedirs(temp_dir, exist_ok=True)
            else:
                # Use system temp directory with arx subfolder
                system_temp = os.environ.get('TMPDIR', '/tmp')
                arx_temp_base = os.path.join(system_temp, 'arx')
                os.makedirs(arx_temp_base, exist_ok=True)
                temp_dir = os.path.join(arx_temp_base, f"arx_{package_name}")
                os.makedirs(temp_dir, exist_ok=True)
            
            # Change to temp directory and run yay --getpkgbuild
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                result = subprocess.run(
                    [self.yay_path, '--getpkgbuild', package_name],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            finally:
                os.chdir(original_cwd)
            
            if result.returncode != 0:
                # Check if package was not found
                if any(msg in result.stderr.lower() for msg in ['not found', 'no results', 'no packages']):
                    return None
                print(f"Warning: yay --getpkgbuild failed: {result.stderr}")
                return None
            
            # Look for PKGBUILD file
            pkgbuild_path = os.path.join(temp_dir, package_name, 'PKGBUILD')
            if os.path.exists(pkgbuild_path):
                with open(pkgbuild_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print(f"Warning: PKGBUILD not found at {pkgbuild_path}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"Timeout getting PKGBUILD for {package_name}")
            return None
        except Exception as e:
            print(f"Error getting PKGBUILD for {package_name}: {e}")
            return None
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                if self.temp_dir:
                    # For custom temp dir, just clean up the package subdirectory
                    try:
                        shutil.rmtree(temp_dir)
                        print(f"Cleaned up temporary directory: {temp_dir}")
                    except Exception as e:
                        print(f"Warning: Could not clean up temporary directory {temp_dir}: {e}")
                else:
                    # For system temp dir, clean up the package subdirectory
                    try:
                        shutil.rmtree(temp_dir)
                        # Also clean up the arx base directory if it's empty
                        arx_base = os.path.dirname(temp_dir)
                        if os.path.exists(arx_base) and not os.listdir(arx_base):
                            os.rmdir(arx_base)
                    except Exception as e:
                        print(f"Warning: Could not clean up temporary directory {temp_dir}: {e}")
    
    def check_package_exists(self, package_name: str) -> bool:
        """Check if a package exists in AUR or official repositories"""
        try:
            result = subprocess.run(
                [self.yay_path, '-Ss', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return False
            
            # Check if any results were found
            lines = result.stdout.strip().split('\n')
            return len(lines) > 0 and not all(line.strip() == '' for line in lines)
            
        except subprocess.TimeoutExpired:
            print(f"Timeout checking if package {package_name} exists")
            return False
        except Exception as e:
            print(f"Error checking if package {package_name} exists: {e}")
            return False
    
    def run_yay(self, args: List[str]) -> int:
        """Run yay with the given arguments"""
        try:
            result = subprocess.run([self.yay_path] + args)
            return result.returncode
        except Exception as e:
            print(f"Error running yay: {e}")
            return 1
