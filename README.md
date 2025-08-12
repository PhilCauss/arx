# Arx - Secure Yay Wrapper

Arx is a Python script that wraps around the `yay` package manager for Arch Linux, providing security analysis of packages before installation. It analyzes PKGBUILD files for malicious intent and checks package names for potential typosquatting.

## Features

- 🔍 **PKGBUILD Analysis**: Uses OpenAI to analyze PKGBUILD files for malicious intent
- 🛡️ **Package Name Analysis**: Detects potential typosquatting and suspicious naming patterns
- 📊 **Confidence Scoring**: Provides confidence levels for security analysis results
- ⚠️ **Malicious Intent Detection**: Identifies potentially harmful packages
- 🎯 **Yay Compatibility**: Accepts all yay arguments and passes them through
- 🔄 **Interactive Prompts**: Asks for confirmation before proceeding with installation
- ⚙️ **Configuration Management**: Easy configuration via config.ini file and arx-config command

## Installation

1. **Clone or download the script**:
   ```bash
   git clone <repository-url>
   cd arx
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

4. **Set up OpenAI API key** (required for PKGBUILD analysis):
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```
   
   Or add it to your shell configuration file (e.g., `~/.bashrc` or `~/.zshrc`):
   ```bash
   echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```
   
   **Note**: This script uses OpenAI API v1.0+ format. Make sure you have the latest version of the openai Python package.

## Usage

Arx works as a drop-in replacement for yay. All yay arguments are supported:

### Basic Usage

```bash
# Install a package
arx -S firefox

# Install multiple packages
arx -S firefox vlc gimp

# Update system
arx -Syu

# Search for packages
arx -Ss firefox

# Remove packages
arx -R firefox
```

### Examples

```bash
# Install a package with security analysis
arx -S spotify

# Update all packages
arx -Syu

# Install from AUR
arx -S yay-git

# Remove packages
arx -Rns firefox
```

## Security Analysis

Arx performs several types of security analysis:

### 1. PKGBUILD Analysis
- Analyzes PKGBUILD files for suspicious commands
- Checks for unusual network requests or downloads
- Identifies file system modifications outside package directory
- Detects execution of downloaded scripts
- Looks for hardcoded URLs or IP addresses

### 2. Package Name Analysis
- Detects potential typosquatting of popular packages
- Identifies suspicious naming patterns
- Checks for very short or very long package names
- Warns about packages with excessive numbers or characters

### 3. Confidence Levels
- **High Confidence (0.8-1.0)**: 🟢 Strong analysis results, package appears safe
- **Medium Confidence (0.6-0.79)**: 🟡 Moderate analysis results, review recommended
- **Low Confidence (0.0-0.59)**: 🔴 Limited analysis results, exercise caution

## Output Examples

### Verbose Output (default)

```
Packages to install: firefox

Analyzing firefox...

============================================================
SECURITY ANALYSIS: firefox
============================================================
📦 PACKAGE NAME ANALYSIS:
  ✅ Package name appears normal

🔍 PKGBUILD SECURITY ANALYSIS:
  Malicious Intent: ✅ NO
  Confidence: 0.85

  Suspicious Patterns:
    • None detected

  Recommendations:
    • Package appears safe for installation

  Analysis:
    This PKGBUILD follows standard packaging practices...
============================================================

============================================================
OVERALL SECURITY ASSESSMENT
============================================================
Average Confidence: 0.85
✅  No malicious intent detected in any packages
============================================================

Do you want to continue with the installation? (y/N): y
Proceeding with installation...
```

### Non-Verbose Output

```
Analyzing 1 packages...

========================================
CHECK: firefox
========================================
📦 NAME: ✅ Normal
🔍 PKGBUILD: ✅ SAFE (Confidence: 0.85)
========================================

========================================
OVERALL ASSESSMENT
========================================
✅  All packages appear safe
========================================

Do you want to continue with the installation? (y/N): y
```

## Configuration

### Configuration File

Arx uses a configuration file (`config.ini`) to control its behavior. The configuration file is automatically created in the following locations (in order of priority):

1. **Current working directory**: `./config.ini`
2. **User config directory**: `~/.config/arx/config.ini`
3. **System config directory**: `/etc/arx/config.ini`

#### Configuration Options

```ini
[arx]
# Control the verbosity of arx output
# If verbose=true: Display full detailed analysis output (default)
# If verbose=false: Display only check name and PKGBUILD analysis results
verbose = true
```

#### Managing Configuration

Use the `arx-config` command to manage your configuration:

```bash
# Show current configuration
arx-config show

# Enable verbose mode
arx-config verbose true

# Disable verbose mode
arx-config verbose false

# Show configuration file path
arx-config path
```

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for PKGBUILD analysis (required)
- `ARX_DEBUG`: Set to `1` for debug output

### Customization

You can modify the script to:
- Add more suspicious patterns for package names
- Customize the confidence scoring algorithm
- Add additional analysis methods
- Modify the prompt for OpenAI analysis

### Temporary Directory Handling

Arx automatically creates temporary directories in the system's temp location (`$TMPDIR` or `/tmp`) for PKGBUILD analysis. This approach ensures:

- **Automatic cleanup**: Temporary files are automatically removed after analysis
- **System integration**: Respects the `$TMPDIR` environment variable if set, otherwise defaults to `/tmp`
- **Isolation**: Creates `/tmp/arx/arx_<package_name>/` directories for each package analysis
- **Security**: No persistent temporary files that could accumulate over time

## Dependencies

- Python 3.8+
- `yay` package manager
- `openai>=1.0.0` Python package
- `requests>=2.25.0` Python package

## Troubleshooting

### Common Issues

1. **"yay not found" error**:
   - Make sure yay is installed: `sudo pacman -S yay`
   - Ensure yay is in your PATH

2. **OpenAI API errors**:
   - Check your API key is correct
   - Ensure you have sufficient API credits
   - Verify your OpenAI account is active

3. **Permission denied**:
   - Make sure the script is properly installed: `pip install -e .`
   - Run with proper permissions

4. **Package not found**:
   - The package might not exist in AUR or official repositories
   - Check the package name spelling

### Debug Mode

Enable debug mode by setting the environment variable:
```bash
export ARX_DEBUG=1
arx -S firefox
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

Arx is a security analysis tool and should not be considered a replacement for manual review. Always exercise caution when installing packages, especially from the AUR. The security analysis is provided as-is and should be used as one of many factors in your decision-making process.
