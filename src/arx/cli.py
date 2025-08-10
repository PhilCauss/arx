"""
Command-line interface for arx
"""

import os
import sys
from .analyzer import ArxSecurityAnalyzer
from .wrapper import YayWrapper


def display_security_report(package_name: str, analysis):
    """Display security analysis report for a package"""
    print(f"\n{'='*60}")
    print(f"SECURITY ANALYSIS: {package_name}")
    print(f"{'='*60}")
    print(f"Security Score: {analysis.score}/100")
    print(f"Malicious Intent: {'⚠️  YES' if analysis.malicious_intent else '✅ NO'}")
    
    if analysis.suspicious_patterns:
        print(f"\nSuspicious Patterns:")
        for pattern in analysis.suspicious_patterns:
            print(f"  • {pattern}")
    
    if analysis.recommendations:
        print(f"\nRecommendations:")
        for rec in analysis.recommendations:
            print(f"  • {rec}")
    
    if analysis.package_name_analysis:
        print(f"\nPackage Name Analysis:")
        print(f"  {analysis.package_name_analysis}")
    
    print(f"{'='*60}")


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
        # Check for custom temp directory
        custom_temp_dir = os.getenv('ARX_TEMP_DIR')
        
        # Initialize components
        yay_wrapper = YayWrapper(temp_dir=custom_temp_dir)
        analyzer = ArxSecurityAnalyzer(temp_dir=custom_temp_dir)
        
        # Get packages to install
        packages = yay_wrapper.get_packages_to_install(yay_args)
        
        if not packages:
            # No packages to install, just run yay
            print("No packages to install detected. Running yay directly...")
            return yay_wrapper.run_yay(yay_args)
        
        print(f"Packages to install: {', '.join(packages)}")
        
        # Analyze each package
        all_analyses = []
        packages_not_found = []
        
        for package in packages:
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
            
            # Analyze PKGBUILD
            analysis = analyzer.analyze_pkgbuild(pkgbuild_content, package)
            
            # Analyze package name
            name_analysis = analyzer.analyze_package_name(package)
            analysis.package_name_analysis = name_analysis
            
            all_analyses.append((package, analysis))
            
            # Display report
            display_security_report(package, analysis)
        
        # Handle packages that were not found
        if packages_not_found:
            print(f"\n{'='*60}")
            print("PACKAGES NOT FOUND")
            print(f"{'='*60}")
            for package in packages_not_found:
                print(f"❌ {package}")
            print(f"{'='*60}")
            
            if not all_analyses:
                print("No valid packages to install. Exiting.")
                return 1
            
            # Ask if user wants to continue with only the found packages
            print(f"\nOnly {len(all_analyses)} out of {len(packages)} packages were found and analyzed.")
            if not prompt_continue():
                print("Installation cancelled by user.")
                return 1
        
        # Calculate overall security score
        if all_analyses:
            overall_score = sum(analysis.score for _, analysis in all_analyses) // len(all_analyses)
            overall_malicious = any(analysis.malicious_intent for _, analysis in all_analyses)
            
            print(f"\n{'='*60}")
            print(f"OVERALL SECURITY ASSESSMENT")
            print(f"{'='*60}")
            print(f"Overall Security Score: {overall_score}/100")
            if overall_malicious:
                print("⚠️  MALICIOUS INTENT DETECTED IN ONE OR MORE PACKAGES!")
            print(f"{'='*60}\n")
        
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
        print("Proceeding with installation...")
        return yay_wrapper.run_yay(yay_args)
        
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
