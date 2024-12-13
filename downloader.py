# library_downloader/downloader.py
import subprocess
import sys
import os
import time
import logging
from plyer import notification
from tkinter import Tk, messagebox
from packaging import version as packaging_version
import sysconfig
import importlib
import importlib.util
import re

# Set up logging to a file
logging.basicConfig(filename='library_installation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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

# Improved function to install packages with retry and detailed feedback
def install_with_retry(package_name, retries=3):
    for attempt in range(retries):
        try:
            # Attempt to install the package
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"{package_name} installed successfully.")
            logging.info(f"Successfully installed {package_name}")
            break
        except subprocess.CalledProcessError as e:
            logging.error(f"Attempt {attempt + 1} failed for {package_name}. Error: {e}")
            
            # Check for specific error codes and handle accordingly
            if e.returncode == 1:
                # Generic error, possibly due to pip issues or network failure
                print(f"Error: Failed to install {package_name}. Please check your network connection or pip version.")
                logging.error(f"Generic error during installation of {package_name}. Please check your network or pip version.")
            elif e.returncode == 2:
                # Specific error related to pip issues (e.g., outdated pip)
                print(f"Error: There seems be an issue with pip. Try upgrading pip using: pip install --upgrade pip")
                logging.error(f"Outdated pip version detected for {package_name}. Suggest upgrading pip.")
            elif e.returncode == 3:
                # Dependency conflicts or version issues
                print(f"Error: There might be a conflict with dependencies. Try using a virtual environment to resolve issues.")
                logging.error(f"Dependency conflict detected for {package_name}. Suggest using a virtual environment.")
            else:
                # For any other unknown errors
                print(f"Unknown error occurred while installing {package_name}. Please try again or check logs.")
                logging.error(f"Unknown error for {package_name}. Return code: {e.returncode}")
            
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
    
    # Determine the correct activation script based on the OS
    if os.name == 'nt':  # Windows
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')
    else:  # Unix-based systems (Linux, macOS)
        activate_script = os.path.join(venv_dir, 'bin', 'activate')
    
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

def install_dependencies(venv_dir, dependencies):
    """Install a list of dependencies using pip."""
    try:
        pip_path = os.path.join(venv_dir, 'Scripts', 'pip') if os.name == 'nt' else os.path.join(venv_dir, 'bin', 'pip')
        logging.info(f"Installing dependencies: {', '.join(dependencies)}...")

        subprocess.check_call([pip_path, 'install'] + dependencies)
        logging.info("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install dependencies: {e}")
        show_popup("Installation Error", f"Error installing dependencies: {e}")
        return

# Function to show a popup message
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
        install_with_retry(package_name)

    except subprocess.CalledProcessError:
        logging.error(f"Error during installation of {package_name}: {e}")
        print(f"Error during installation of {package_name}: {e}")
        
        # After failed installation, ask if the user wants to use a virtual environment
        if sys.prefix == sys.base_prefix:  # Only ask if the user is not in a virtual environment
            show_virtualenv_prompt(package_name)
    except Exception as e:
        logging.error(f"Unexpected error with {package_name}: {e}")
        print(f"Unexpected error with {package_name}: {e}")

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

# Function to start the library download process
def start_library_download():
    print("Library downloader started...")
    # Example script path - You can change this to point to your script
    script_path = "your_script.py"
    
    # Open the script and scan for required packages
    with open(script_path, 'r') as file:
        script_content = file.read()

    # Extract version requirements
    version_requirements = extract_version_from_comments(script_content)

    # Find all package names (this assumes all import statements are in the form `import package` or `from package import ...`)
    import_statements = [line.strip() for line in script_content.splitlines() if line.startswith('import') or line.startswith('from')]
    
    for stmt in import_statements:
        package_name = stmt.split()[1].split('.')[0]  # Get the package name (handling submodules)
        if package_name not in version_requirements:
            packages_to_install.append(package_name)

    for package_name in packages_to_install:
        check_and_install_package(package_name)
