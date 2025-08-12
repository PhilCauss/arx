#!/bin/bash

# Arx Installation Script
# This script installs arx and its dependencies

set -e

echo "🚀 Installing Arx - Secure Yay Wrapper"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 first:"
    echo "  sudo pacman -S python"
    exit 1
fi

# Check if yay is installed
if ! command -v yay &> /dev/null; then
    echo "❌ yay is required but not installed."
    echo "Please install yay first:"
    echo "  sudo pacman -S yay"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Python package in user space
echo "📦 Installing Arx Python package..."
python3 -m pip install --user -e .

# Test if the package can be imported
echo "🧪 Testing arx package..."
if ! python3 -c "import arx; print('✅ arx package imported successfully')" 2>/dev/null; then
    echo "❌ Failed to import arx package. Please check the installation."
    exit 1
fi

# Test if the CLI works
echo "🧪 Testing arx CLI..."
if ! python3 -m cli --help &> /dev/null; then
    echo "❌ Failed to test arx CLI. Please check the installation."
    exit 1
fi
echo "✅ arx CLI test passed"

# Create a symlink in /usr/local/bin (optional)
read -p "🤔 Would you like to create a symlink in /usr/local/bin? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -w /usr/local/bin ]; then
        # Remove existing symlink if it exists
        if [ -L /usr/local/bin/arx ]; then
            echo "🔄 Removing existing symlink..."
            rm /usr/local/bin/arx
        fi
        
        # Create new symlink to the installed package
        sudo ln -sf "$(python3 -m site --user-base)/bin/arx" /usr/local/bin/arx
        echo "✅ Symlink created: /usr/local/bin/arx"
        
        # Test the symlink
        if command -v arx &> /dev/null; then
            echo "✅ Symlink test passed - 'arx' command is now available"
        else
            echo "⚠️  Symlink created but 'arx' command not found in PATH"
            echo "   You may need to restart your shell or add /usr/local/bin to PATH"
        fi
    else
        echo "❌ Cannot write to /usr/local/bin. Skipping symlink creation."
        echo "💡 Alternative: You can run arx with: python3 -m cli"
    fi
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  OpenAI API key not found in environment variables."
    echo "To enable PKGBUILD analysis, set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "Or add it to your shell configuration file:"
    echo "  echo 'export OPENAI_API_KEY=\"your-api-key-here\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    echo ""
fi

# Note about temporary directory handling
echo ""
echo "💡 Note: Arx automatically uses system temporary directories for PKGBUILD analysis."
echo "   Temporary files are created in /tmp/arx/ and automatically cleaned up after use."
echo ""

echo ""
echo "🎉 Arx installation completed!"
echo ""
echo "Usage examples:"
if command -v arx &> /dev/null; then
    echo "  arx -S firefox          # Using symlink"
    echo "  arx -Syu               # Using symlink"
    echo "  arx -Ss package-name   # Using symlink"
else
      echo "  python3 -m cli -S firefox    # Direct execution"
  echo "  python3 -m cli -Syu         # Direct execution"
  echo "  python3 -m cli -Ss package-name # Direct execution"
fi
echo ""
echo "For more information, see README.md"
