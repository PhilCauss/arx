"""
Configuration management for arx
"""

import configparser
import os
from pathlib import Path
from typing import Optional


class ArxConfig:
    """Configuration manager for arx"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = configparser.ConfigParser()
        self.config_path = config_path or self._find_config_file()
        self._load_config()
    
    def _find_config_file(self) -> str:
        """Find the configuration file in order of priority"""
        # Check current working directory first
        cwd_config = Path.cwd() / "config.ini"
        if cwd_config.exists():
            return str(cwd_config)
        
        # Check user's home directory
        home_config = Path.home() / ".config" / "arx" / "config.ini"
        if home_config.exists():
            return str(home_config)
        
        # Check system-wide config
        system_config = Path("/etc/arx/config.ini")
        if system_config.exists():
            return str(system_config)
        
        # Default to current working directory
        return str(cwd_config)
    
    def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path)
            except (configparser.Error, OSError) as e:
                print(f"Warning: Could not read config file {self.config_path}: {e}")
                # Set defaults
                self._set_defaults()
        else:
            # Create default config
            self._set_defaults()
            self._save_config()
    
    def _set_defaults(self):
        """Set default configuration values"""
        if 'arx' not in self.config:
            self.config['arx'] = {}
        
        if 'verbose' not in self.config['arx']:
            self.config['arx']['verbose'] = 'true'
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            # Ensure directory exists
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
        except (OSError, IOError) as e:
            print(f"Warning: Could not write config file {self.config_path}: {e}")
    
    @property
    def verbose(self) -> bool:
        """Get verbose setting"""
        try:
            return self.config.getboolean('arx', 'verbose', fallback=True)
        except (ValueError, configparser.Error):
            return True
    
    def set_verbose(self, value: bool):
        """Set verbose setting"""
        self.config['arx']['verbose'] = str(value).lower()
        self._save_config()


# Global configuration instance
config = ArxConfig()
