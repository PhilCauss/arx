"""
Configuration CLI utility for arx
"""

import argparse
import sys
from .config import ArxConfig


def main():
    """Configuration management CLI"""
    parser = argparse.ArgumentParser(
        description="Manage arx configuration",
        prog="arx-config"
    )
    
    parser.add_argument(
        "--config-path",
        help="Path to configuration file (default: auto-detect)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show current configuration")
    
    # Set verbose command
    verbose_parser = subparsers.add_parser("verbose", help="Set verbose mode")
    verbose_parser.add_argument(
        "value",
        choices=["true", "false", "on", "off", "1", "0"],
        help="Verbose mode value"
    )
    
    # Get config path command
    path_parser = subparsers.add_parser("path", help="Show configuration file path")
    
    args = parser.parse_args()
    
    # Initialize config
    config = ArxConfig(args.config_path)
    
    if args.command == "show":
        print(f"Configuration file: {config.config_path}")
        print(f"Verbose mode: {config.verbose}")
        
    elif args.command == "verbose":
        # Convert various input formats to boolean
        value = args.value.lower()
        if value in ["true", "on", "1"]:
            config.set_verbose(True)
            print("Verbose mode enabled")
        elif value in ["false", "off", "0"]:
            config.set_verbose(False)
            print("Verbose mode disabled")
        else:
            print(f"Invalid value: {args.value}")
            sys.exit(1)
            
    elif args.command == "path":
        print(config.config_path)
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
