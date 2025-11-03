#!/usr/bin/env python
"""
Check if all requirements.txt packages are installed
"""

import sys
import importlib
import pkg_resources

def check_requirements():
    """Check if all packages from requirements.txt are installed."""
    
    print("=" * 60)
    print("📋 CHECKING REQUIREMENTS.TXT PACKAGES")
    print("=" * 60)
    
    with open('requirements.txt', 'r') as f:
        requirements = f.readlines()
    
    installed = []
    missing = []
    version_mismatch = []
    
    for req in requirements:
        req = req.strip()
        
        # Skip empty lines and comments
        if not req or req.startswith('#'):
            continue
        
        # Parse package name and version requirement
        if '>=' in req:
            pkg_name = req.split('>=')[0].strip()
            version_req = req.split('>=')[1].split(',')[0].strip()
        elif '==' in req:
            pkg_name = req.split('==')[0].strip()
            version_req = req.split('==')[1].strip()
        else:
            pkg_name = req
            version_req = None
        
        # Handle packages with extras like qrcode[pil]
        if '[' in pkg_name:
            pkg_name = pkg_name.split('[')[0].strip()
        
        # Special handling for package names that differ from import names
        import_name = pkg_name.replace('-', '_')
        
        # Special cases
        import_mapping = {
            'scikit_learn': 'sklearn',
            'pillow': 'PIL',
            'python_dotenv': 'dotenv',
        }
        
        if import_name.lower() in import_mapping:
            import_name = import_mapping[import_name.lower()]
        
        # Try to import the package
        try:
            # Try direct import
            try:
                mod = importlib.import_module(import_name)
                
                # Try to get version
                try:
                    installed_version = pkg_resources.get_distribution(pkg_name).version
                    installed.append((pkg_name, installed_version))
                    print(f"✅ {pkg_name:30s} v{installed_version}")
                except:
                    installed.append((pkg_name, "unknown"))
                    print(f"✅ {pkg_name:30s} (version unknown)")
                    
            except ImportError:
                # Try with original package name
                mod = importlib.import_module(pkg_name)
                installed.append((pkg_name, "unknown"))
                print(f"✅ {pkg_name:30s} (installed)")
                
        except ImportError:
            missing.append(pkg_name)
            print(f"❌ {pkg_name:30s} NOT INSTALLED")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Installed: {len(installed)}")
    print(f"❌ Missing: {len(missing)}")
    
    if missing:
        print("\n🔧 Missing packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        return False
    else:
        print("\n🎉 All requirements.txt packages are installed!")
        return True

if __name__ == "__main__":
    success = check_requirements()
    sys.exit(0 if success else 1)
