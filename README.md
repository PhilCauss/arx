# Arx - Secure Yay Wrapper

Arx is a Python script that wraps around the `yay` package manager for Arch Linux, providing security analysis of packages before installation. It analyzes PKGBUILD files for malicious intent and checks package names for potential typosquatting.

## Features

- 🔍 **PKGBUILD Analysis**: Uses OpenAI to analyze PKGBUILD files for malicious intent
- 🛡️ **Package Name Analysis**: Detects potential typosquatting and suspicious naming patterns
- 📊 **Security Scoring**: Provides a 0-100 security score for each package
- ⚠️ **Malicious Intent Detection**: Identifies potentially harmful packages
- 🎯 **Yay Compatibility**: Accepts all yay arguments and passes them through
- 🔄 **Interactive Prompts**: Asks for confirmation before proceeding with installation

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

3. **Make the script executable**:
   ```bash
   chmod +x arx.py
   ```

4. **Set up OpenAI API key** (optional but recommended):
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
./arx.py -S firefox

# Install multiple packages
./arx.py -S firefox vlc gimp

# Update system
./arx.py -Syu

# Search for packages
./arx.py -Ss firefox

# Remove packages
./arx.py -R firefox
```

### Examples

```bash
# Install a package with security analysis
./arx.py -S spotify

# Update all packages
./arx.py -Syu

# Install from AUR
./arx.py -S yay-git

# Remove packages
./arx.py -Rns firefox
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

### 3. Security Scoring
- **0-39**: 🔴 High risk - Exercise extreme caution
- **40-69**: 🟡 Medium risk - Review carefully
- **70-100**: 🟢 Low risk - Generally safe

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

- `OPENAI_API_KEY`: Your OpenAI API key for PKGBUILD analysis
- `ARX_TEMP_DIR`: Custom temporary directory for PKGBUILD analysis (optional)
- `ARX_DEBUG`: Set to `1` for debug output

### Customization

You can modify the script to:
- Add more suspicious patterns for package names
- Customize the security scoring algorithm
- Add additional analysis methods
- Modify the prompt for OpenAI analysis

### Temporary Directory Configuration

By default, arx creates temporary directories in the system's temp location (`$TMPDIR` or `/tmp`) for PKGBUILD analysis. You can customize this behavior:

```bash
# Use a custom temp directory (files will be preserved for inspection)
export ARX_TEMP_DIR="/home/user/arx_temp"

# Use system temp directory (files will be automatically cleaned up)
unset ARX_TEMP_DIR
```

**Note**: 
- **System temp**: Creates `/tmp/arx/arx_<package_name>/` directories and cleans them up after analysis
- **Custom temp**: Creates `/your/path/arx_<package_name>/` directories and cleans them up after analysis
- The `$TMPDIR` environment variable is respected if set, otherwise defaults to `/tmp`

## Dependencies

- Python 3.7+
- `yay` package manager
- `openai` Python package
- `requests` Python package

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
   - Make the script executable: `chmod +x arx.py`
   - Run with proper permissions

4. **Package not found**:
   - The package might not exist in AUR or official repositories
   - Check the package name spelling

### Debug Mode

Enable debug mode by setting the environment variable:
```bash
export ARX_DEBUG=1
./arx.py -S firefox
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

Arx is a security analysis tool and should not be considered a replacement for manual review. Always exercise caution when installing packages, especially from the AUR. The security analysis is provided as-is and should be used as one of many factors in your decision-making process.
