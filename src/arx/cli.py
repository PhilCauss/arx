"""
Command-line interface for arx
"""

import os
import sys
import tempfile
from .analyzer import ArxSecurityAnalyzer
from .wrapper import YayWrapper
from .config import config


def display_security_report(package_name: str, analysis, analyzer, verbose: bool = True):
    """Display security analysis report for a package"""
    if verbose:
        # Full verbose output (current behavior)
        print(f"\n{'='*60}")
        print(f"SECURITY ANALYSIS: {package_name}")
        print(f"{'='*60}")
        
        # Start with package name analysis
        print("📦 PACKAGE NAME ANALYSIS:")
        name_analysis = analyzer.analyze_package_name(package_name)
        if name_analysis and name_analysis != "Package name appears normal":
            print(f"  ⚠️  {name_analysis}")
        else:
            print(f"  ✅ Package name appears normal")
        
        # Then show PKGBUILD analysis results
        print(f"\n🔍 PKGBUILD SECURITY ANALYSIS:")
        print(f"  Malicious Intent: {'⚠️  YES' if analysis.malicious_intent else '✅ NO'}")
        print(f"  Confidence: {analysis.confidence:.2f}")

        
        if analysis.suspicious_patterns:
            print(f"\n  Suspicious Patterns:")
            for pattern in analysis.suspicious_patterns:
                print(f"    • {pattern}")
        
        if analysis.recommendations:
            print(f"\n  Recommendations:")
            for rec in analysis.recommendations:
                print(f"    • {rec}")
        
        if analysis.analysis:
            print(f"\n  Analysis:")
            print(f"    {analysis.analysis}")
        
        print(f"{'='*60}")
    else:
        # Minimal output - just check name and PKGBUILD analysis results
        print(f"\n{'='*40}")
        print(f"CHECK: {package_name}")
        print(f"{'='*40}")
        
        # Package name analysis
        name_analysis = analyzer.analyze_package_name(package_name)
        if name_analysis and name_analysis != "Package name appears normal":
            print(f"📦 NAME: ⚠️  {name_analysis}")
        else:
            print(f"📦 NAME: ✅ Normal")
        
        # PKGBUILD analysis results
        print(f"🔍 PKGBUILD: {'⚠️  MALICIOUS' if analysis.malicious_intent else '✅ SAFE'} (Confidence: {analysis.confidence:.2f})")
        
        print(f"{'='*40}")


def prompt_continue() -> bool:
    """Prompt user to continue with installation"""
    while True:
        response = input("\nDo you want to continue with the installation? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def main():
    """Main CLI entry point"""
    # Get all arguments after the script name
    yay_args = sys.argv[1:]
    
    # Show help if no arguments or help requested
    if not yay_args or '-h' in yay_args or '--help' in yay_args:
        print("arx - A secure wrapper around yay package manager")
        print("Analyzes packages for malicious intent before installation")
        print()
        print("Usage: arx [yay-arguments]")
        print()
        print("Examples:")
        print("  arx -S firefox")
        print("  arx -Syu")
        print("  arx --sync --refresh")
        print("  arx -Ss package-name")
        print("  arx -R package-name")
        print()
        print("All yay arguments are supported. See 'yay --help' for more options.")
        return 0
    
    try:
        # Create temporary directory for analysis
        new_temp_dir = tempfile.mkdtemp()
        try:
            openai_api_key = os.getenv('OPENAI_API_KEY')
            
            # Initialize components
            yay_wrapper = YayWrapper(temp_dir=new_temp_dir)
            analyzer = ArxSecurityAnalyzer(temp_dir=new_temp_dir)
            
            # Get packages to install
            packages = yay_wrapper.get_packages_to_install(yay_args)
            
            if not packages:
                # No packages to install, just run yay
                print("No packages to install detected. Running yay directly...")
                return yay_wrapper.run_yay(yay_args)
            
            if not openai_api_key:
                print("Error: OPENAI_API_KEY environment variable is not set")
                return 1

            if config.verbose:
                print(f"Packages to install: {', '.join(packages)}")
            else:
                print(f"Analyzing {len(packages)} packages...")
            
            # Analyze each package
            all_analyses = []
            packages_not_found = []
            
            for package in packages:
                if config.verbose:
                    print(f"\nAnalyzing {package}...")
                
                # First check if package exists
                if not yay_wrapper.check_package_exists(package):
                    print(f"❌ Package '{package}' not found in AUR or official repositories")
                    packages_not_found.append(package)
                    continue
                
                # Get PKGBUILD content
                pkgbuild_content = yay_wrapper.get_pkgbuild_content(package)
                
                if pkgbuild_content is None:
                    print(f"⚠️  Could not retrieve PKGBUILD for '{package}' - skipping analysis")
                    packages_not_found.append(package)
                    continue
                
                # First, analyze package name for typosquatting and suspicious naming
                name_analysis = analyzer.analyze_package_name(package)
                
                # Then analyze PKGBUILD content
                analysis = analyzer.analyze_pkgbuild(pkgbuild_content, package)
                
                all_analyses.append((package, analysis))
                
                # Display report
                display_security_report(package, analysis, analyzer, config.verbose)
            
            # Handle packages that were not found
            if packages_not_found:
                if config.verbose:
                    print(f"\n{'='*60}")
                    print("PACKAGES NOT FOUND")
                    print(f"{'='*60}")
                    for package in packages_not_found:
                        print(f"❌ {package}")
                    print(f"{'='*60}")
                else:
                    print(f"\n{'='*40}")
                    print("NOT FOUND")
                    print(f"{'='*40}")
                    for package in packages_not_found:
                        print(f"❌ {package}")
                    print(f"{'='*40}")
                
                if not all_analyses:
                    print("No valid packages to install. Exiting.")
                    return 1
                
                # Ask if user wants to continue with only the found packages
                if config.verbose:
                    print(f"\nOnly {len(all_analyses)} out of {len(packages)} packages were found and analyzed.")
                else:
                    print(f"\n{len(all_analyses)}/{len(packages)} packages analyzed.")
                if not prompt_continue():
                    print("Installation cancelled by user.")
                    return 1
            
            # Calculate overall security assessment
            if all_analyses:
                overall_malicious = any(analysis.malicious_intent for _, analysis in all_analyses)
                overall_confidence = sum(analysis.confidence for _, analysis in all_analyses) / len(all_analyses)
                
                if config.verbose:
                    print(f"\n{'='*60}")
                    print(f"OVERALL SECURITY ASSESSMENT")
                    print(f"{'='*60}")
                    print(f"Average Confidence: {overall_confidence:.2f}")
                    if overall_malicious:
                        print("⚠️  MALICIOUS INTENT DETECTED IN ONE OR MORE PACKAGES!")
                    else:
                        print("✅  No malicious intent detected in any packages")
                    print(f"{'='*60}\n")
                else:
                    # Minimal overall assessment
                    print(f"\n{'='*40}")
                    print("OVERALL ASSESSMENT")
                    print(f"{'='*40}")
                    if overall_malicious:
                        print("⚠️  MALICIOUS INTENT DETECTED!")
                    else:
                        print("✅  All packages appear safe")
                    print(f"{'='*40}\n")
            
            # Prompt for continuation
            if not prompt_continue():
                print("Installation cancelled by user.")
                return 1
            
            # Filter out not-found packages from yay arguments
            if packages_not_found:
                filtered_args = []
                i = 0
                while i < len(yay_args):
                    arg = yay_args[i]
                    if arg in ['-S', '--sync'] and i + 1 < len(yay_args):
                        # Handle -S flag
                        filtered_args.append(arg)
                        i += 1
                        while i < len(yay_args) and not yay_args[i].startswith('-'):
                            if yay_args[i] not in packages_not_found:
                                filtered_args.append(arg)
                            i += 1
                    elif not arg.startswith('-') and arg not in ['install', 'remove', 'update']:
                        # Direct package names
                        if arg not in packages_not_found:
                            filtered_args.append(arg)
                    else:
                        # Other arguments (flags, etc.)
                        filtered_args.append(arg)
                    i += 1
                yay_args = filtered_args
            
            # Run yay
            if config.verbose:
                print("Proceeding with installation...")
            return yay_wrapper.run_yay(yay_args)
            
        finally:
            # Always clean up the temporary directory
            import shutil
            try:
                shutil.rmtree(new_temp_dir)
            except OSError:
                # Ignore errors during cleanup (e.g., directory already removed)
                pass
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
