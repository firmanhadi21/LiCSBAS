# Fix LiCSBAS Module Import Issues in Google Colab

import os
import sys
import subprocess

def fix_licsbas_imports():
    """Fix LiCSBAS import issues in Google Colab"""
    
    print("Fixing LiCSBAS import issues...")
    
    # 1. Set up proper paths
    licsbas_path = '/content/LiCSBAS'
    licsbas_lib_path = '/content/LiCSBAS/LiCSBAS_lib'
    licsbas_bin_path = '/content/LiCSBAS/bin'
    
    # Add all necessary paths to Python path
    paths_to_add = [
        licsbas_path,
        licsbas_lib_path,
        licsbas_bin_path,
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # 2. Set environment variables
    os.environ['LiCSBAS'] = licsbas_path
    os.environ['LiCSBAS_lib'] = licsbas_lib_path
    os.environ['PYTHONPATH'] = ':'.join(paths_to_add + [os.environ.get('PYTHONPATH', '')])
    os.environ['PATH'] = f"{licsbas_bin_path}:{os.environ['PATH']}"
    
    # 3. Check if LiCSBAS_meta.py exists and create symlinks if needed
    meta_file = os.path.join(licsbas_lib_path, 'LiCSBAS_meta.py')
    
    if not os.path.exists(meta_file):
        print(f"LiCSBAS_meta.py not found at {meta_file}")
        # List available files to debug
        print("Available files in LiCSBAS_lib:")
        if os.path.exists(licsbas_lib_path):
            subprocess.run(['ls', '-la', licsbas_lib_path])
        
        # Try to find the meta file
        for root, dirs, files in os.walk(licsbas_path):
            if 'LiCSBAS_meta.py' in files:
                found_meta = os.path.join(root, 'LiCSBAS_meta.py')
                print(f"Found LiCSBAS_meta.py at: {found_meta}")
                # Create symlink
                try:
                    os.symlink(found_meta, meta_file)
                    print(f"Created symlink: {meta_file} -> {found_meta}")
                except:
                    # If symlink fails, copy the file
                    subprocess.run(['cp', found_meta, meta_file])
                    print(f"Copied file: {found_meta} -> {meta_file}")
                break
    
    # 4. Create __init__.py files if missing
    init_files = [
        os.path.join(licsbas_path, '__init__.py'),
        os.path.join(licsbas_lib_path, '__init__.py'),
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# LiCSBAS module init file\n')
            print(f"Created {init_file}")
    
    print("LiCSBAS paths fixed!")
    print(f"Python path includes: {[p for p in sys.path if 'LiCSBAS' in p]}")
    
    return True

def test_licsbas_imports():
    """Test if LiCSBAS modules can be imported"""
    try:
        # Test basic imports
        import LiCSBAS_meta
        print("✓ LiCSBAS_meta imported successfully")
        
        from LiCSBAS_lib import LiCSBAS_tools_lib
        print("✓ LiCSBAS_tools_lib imported successfully")
        
        from LiCSBAS_lib import LiCSBAS_io_lib
        print("✓ LiCSBAS_io_lib imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def reinstall_licsbas():
    """Reinstall LiCSBAS with proper setup"""
    print("Reinstalling LiCSBAS...")
    
    # Remove existing installation
    subprocess.run(['rm', '-rf', '/content/LiCSBAS'])
    
    # Clone fresh copy
    os.chdir('/content')
    result = subprocess.run(['git', 'clone', 'https://github.com/yumorishita/LiCSBAS.git'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error cloning LiCSBAS: {result.stderr}")
        return False
    
    print("LiCSBAS cloned successfully")
    
    # Fix permissions
    subprocess.run(['chmod', '+x', '/content/LiCSBAS/bin/*.py'])
    
    # Apply fixes
    fix_licsbas_imports()
    
    return True

# Main execution
if __name__ == "__main__":
    print("=== LiCSBAS Import Fix ===")
    
    # First try to fix existing installation
    if os.path.exists('/content/LiCSBAS'):
        fix_licsbas_imports()
        
        if test_licsbas_imports():
            print("✓ LiCSBAS is now working correctly!")
        else:
            print("⚠ Fixes didn't work, reinstalling...")
            reinstall_licsbas()
            test_licsbas_imports()
    else:
        print("LiCSBAS not found, installing...")
        reinstall_licsbas()
        test_licsbas_imports()
    
    print("\n=== Testing LiCSBAS01_get_geotiff.py ===")
    try:
        # Test the specific script that was failing
        os.chdir('/content/LiCSBAS')
        result = subprocess.run(['python', 'bin/LiCSBAS01_get_geotiff.py', '-h'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ LiCSBAS01_get_geotiff.py is working!")
            print("Help output:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print(f"✗ Error running LiCSBAS01_get_geotiff.py: {result.stderr}")
    except Exception as e:
        print(f"✗ Exception testing script: {e}")
