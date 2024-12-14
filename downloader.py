import sys
import os
import subprocess
import time
import logging
from filelock import FileLock
from plyer import notification
from tkinter import Tk, messagebox
from packaging import version as packaging_version
import sysconfig
import importlib
import importlib.util
import re
import builtins
import tempfile

# Set up logging to a file
logging.basicConfig(filename='library_installation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

imported_packages = set()  # To keep track of already imported packages

# Function to extract version requirements from comments
def extract_version_from_comments(script_content):
    version_pattern = re.compile(r'#\s*Required:\s*(\S+)([<>=!]+)(\S+)')
    version_requirements = re.findall(version_pattern, script_content)
    return {pkg: (op, ver) for pkg, op, ver in version_requirements}

# Function to check for Python version compatibility with the package
def is_python_compatible(package_name, required_version=None):
    python_version = packaging_version.parse(".".join(map(str, sys.version_info[:3])))  # Get Python version as a packaging.Version object
    if required_version:
        operator, required_version_str = required_version
        required_version = packaging_version.parse(required_version_str)

        logging.info(f"Checking if Python version {python_version} is compatible with {package_name} version {required_version}")
        if operator == '==':
            return python_version == required_version
        elif operator == '>=':
            return python_version >= required_version
        elif operator == '<=':
            return python_version <= required_version
        elif operator == '>':
            return python_version > required_version
        elif operator == '<':
            return python_version < required_version
        else:
            return True  # Assume compatibility if no valid operator is found
    return True  # Assume compatibility if no version specified

# Function to check if a package is a standard Python library
def is_standard_library(package_name):
    # Get standard library directories from sysconfig
    standard_lib_dirs = sysconfig.get_paths()["stdlib"]
    # Check if the package is within any of these directories
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

# Cross-platform function to get the correct virtual environment activation script
def get_activate_script(venv_dir="venv"):
    if os.name == 'nt':  # Windows
        return os.path.join(venv_dir, 'Scripts', 'activate.bat')
    else:  # Unix-based systems (Linux, macOS)
        return os.path.join(venv_dir, 'bin', 'activate')

# Cross-platform temporary directory handling for lock file
def get_lock_file(package_name):
    lock_dir = tempfile.gettempdir()  # This works across platforms
    lock_path = os.path.join(lock_dir, f'{package_name}.lock')
    return lock_path

# Improved function to install packages with retry and detailed feedback using locking
def install_with_lock(package_name, retries=3):
    lock_path = get_lock_file(package_name)  # Get platform-independent lock path
    lock = FileLock(lock_path)

    with lock:  # Acquire lock
        for attempt in range(retries):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"{package_name} installed successfully.")
                logging.info(f"Successfully installed {package_name}")
                break
            except subprocess.CalledProcessError as e:
                logging.error(f"Attempt {attempt + 1} failed for {package_name}. Error: {e}")
                if e.returncode == 1:
                    print(f"Error: Failed to install {package_name}. Please check your network connection or pip version.")
                elif e.returncode == 2:
                    print(f"Error: There seems to be an issue with pip. Try upgrading pip using: pip install --upgrade pip")
                elif e.returncode == 3:
                    print(f"Error: There might be a conflict with dependencies. Try using a virtual environment to resolve issues.")
                else:
                    print(f"Unknown error occurred while installing {package_name}. Please try again or check logs.")
            
            time.sleep(2 ** attempt)  # Exponential backoff
            if attempt == retries - 1:
                logging.error(f"Failed to install {package_name} after {retries} attempts.")
                print(f"Failed to install {package_name} after {retries} attempts.")

# Function to create a virtual environment if not already in one, with dependencies
def create_virtualenv(venv_dir="venv", install_deps=False, dependencies=None):
    if dependencies is None:
        dependencies = ['requests', 'flask']  # Default list of dependencies to install
    
    # Check if virtual environment already exists
    if not os.path.exists(venv_dir):
        logging.info(f"Virtual environment not found. Creating one at {venv_dir}...")
        # Create the virtual environment if it doesn't exist
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        logging.info(f"Created virtual environment at {venv_dir}")
    else:
        logging.info(f"Virtual environment already exists at {venv_dir}")
    
    # Get the activation script for the current platform
    activate_script = get_activate_script(venv_dir)
    
    # Ensure the activation script exists
    try:
        if not os.path.exists(activate_script):
            raise FileNotFoundError(f"Activation script not found: {activate_script}")
    except FileNotFoundError as e:
        logging.error(e)
        show_popup("Error", f"Error: {str(e)}")
        return
    
    # Optionally install dependencies
    if install_deps:
        install_dependencies(venv_dir, dependencies)

    # Show the activation instructions in a popup
    show_popup("Virtual Environment Setup", f"To activate the virtual environment, run:\n\n{activate_script}")

# Function to install dependencies in the virtual environment
def install_dependencies(venv_dir, dependencies):
    # Activate the virtual environment
    activate_script = get_activate_script(venv_dir)
    for dep in dependencies:
        install_with_lock(dep)

# Show popup notifications
def show_popup(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10  # The popup will stay for 10 seconds
    )

# Function to check and install the required package
def check_and_install_package(package_name, required_version=None, upgrade=False, use_venv=False):
    try:
        # Check if the package is a standard library
        if is_standard_library(package_name):
            logging.info(f"{package_name} is a standard library, skipping installation.")
            print(f"{package_name} is a standard library, skipping installation.")
            return

        # Check if we are already in a virtual environment
        if use_venv and sys.prefix == sys.base_prefix:
            # Not in a virtual environment, so create one
            create_virtualenv()

        # Attempt to install the package
        install_with_lock(package_name)

    except subprocess.CalledProcessError:
        logging.error(f"Error during installation of {package_name}: {e}")
        print(f"Error during installation of {package_name}: {e}")
        
        # After failed installation, ask if the user wants to use a virtual environment
        if sys.prefix == sys.base_prefix:  # Only ask if the user is not in a virtual environment
            show_virtualenv_prompt(package_name)
    except Exception as e:
        logging.error(f"Unexpected error with {package_name}: {e}")
        print(f"Unexpected error with {package_name}: {e}")

# Function to show the virtual environment creation prompt (GUI)
def show_virtualenv_prompt(package_name):
    # Create a Tkinter window to ask user for virtual environment creation
    root = Tk()
    root.withdraw()  # Hide the main window
    user_response = messagebox.askquestion("Virtual Environment Creation",
                                           f"Installation of {package_name} failed. Would you like to create a virtual environment and try again?")
    
    if user_response == 'yes':
        print(f"Creating a virtual environment and installing {package_name}...")
        create_virtualenv()
        reinstall_libraries_in_virtualenv()  # Reinstall all required libraries inside the virtual environment
    else:
        print("You chose not to create a virtual environment. Please install manually.")
        logging.info(f"User chose not to create a virtual environment for {package_name}.")

# Function to reinstall all libraries inside a virtual environment
def reinstall_libraries_in_virtualenv():
    # List of all libraries that need to be installed
    for package in packages_to_install:
        check_and_install_package(package, use_venv=True)

# List to keep track of packages that need to be installed
packages_to_install = []

# Function to monitor imports and install missing libraries
def monitor_imports(frame, event, arg):
    if event == 'call' and frame.f_code.co_name == "exec":
        # Get the code being executed
        code = frame.f_globals.get('__code__')
        if code:
            for line in code.co_lines():
                if 'import' in line:
                    package_name = line.split()[1]  # Extract the package name from the import
                    if package_name not in imported_packages:  # Avoid processing the same package multiple times
                        print(f"Detected import statement for: {package_name}")
                        # Trigger library installation
                        check_and_install_package(package_name)
                        imported_packages.add(package_name)  # Mark as processed

    return None

# Function to start the monitoring process
def start_monitoring():
    print("Library downloader is now active. Waiting for imports...")
    sys.setprofile(monitor_imports)  # Set the import monitoring hook

# Start monitoring imports
start_monitoring()

