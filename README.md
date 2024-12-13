# Library Downloader README

## Overview

The `library_downloader` module automates the process of installing required Python libraries for a script. It scans the script for library dependencies, checks for version requirements, handles virtual environments, and installs missing or outdated libraries using `pip`. Additionally, the system includes functionality to manage failed installation attempts with retries, logging, and system notifications.

This tool is particularly useful when you need to ensure that a Python script has all necessary libraries installed, either in a global environment or within a virtual environment.

## Project Structure

The project consists of two primary Python files:

1. `__init__.py` - Initializes the library download process when the module is imported.
2. `downloader.py` - Contains the core logic to handle the extraction of package dependencies, version checks, installation processes, virtual environment setup, and error handling.

### Files:

library_downloader/
│
├── __init__.py          # Initializes the module and triggers the library download
└── downloader.py        # Core functionality for downloading libraries, version checks, and virtual environments


## Features

### 1. **Automatic Library Download**
   - The module triggers the download process as soon as it is imported (`start_library_download`).
   - It reads the target Python script and extracts library dependencies, including version requirements (if specified in the script's comments).
   - It installs any missing libraries or updates existing ones according to the version requirements.

### 2. **Virtual Environment Setup**
   - If the script is not running within a virtual environment, the module can create one automatically and install all required libraries within it.
   - A pop-up notification will inform users how to activate the virtual environment.

### 3. **Error Handling with Retries**
   - If a library installation fails, the system retries up to three times using exponential backoff.
   - Detailed error messages are logged for each failure and shown to the user (e.g., pip issues, network failures, or dependency conflicts).

### 4. **Python Version Compatibility**
   - It checks the required Python version for each library and verifies that the current Python installation is compatible.
   - Supports version comparisons using operators like `==`, `>=`, `<=`, etc.

### 5. **Logging**
   - Logs detailed information about the installation process, including successes, errors, and retries, in a file named `library_installation.log`.
   - The log provides valuable insight into any issues that occur during installation.

### 6. **Standard Library Check**
   - The module checks whether a package is part of Python’s standard library. If it is, the package is skipped, avoiding unnecessary installations.

### 7. **Graphical User Interface (GUI) Prompts**
   - If a library installation fails and a virtual environment is not active, the user is prompted to create a virtual environment via a GUI dialog (Tkinter).
   - Users are given the option to create a virtual environment and retry installing missing libraries.

## Installation

### Prerequisites:
- Python 3.6 or higher
- `pip` for installing Python packages

You will also need to install the following Python packages:

pip install plyer packaging


### Installation Steps:
1. Clone or download this repository to your local machine.

2. Install the required dependencies:
   
   pip install -r requirements.txt


   Alternatively, manually install:

   pip install plyer packaging
 

### Usage

1. **Importing the Library**

   Simply import the `library_downloader` module into your Python script:

   import library_downloader


   When the module is imported, it will automatically start the library download process, checking the script for dependencies and installing any missing libraries.

2. **Creating a Virtual Environment**
   
   If the script is not running inside a virtual environment, the `library_downloader` will create one automatically. You can specify the name of the virtual environment directory by modifying the `create_virtualenv()` function call in the `downloader.py`.

3. **Custom Script Path**
   
   Modify the `script_path` variable in `start_library_download()` to point to your target script if it's not named `your_script.py`.

4. **Handle Errors and Retry Logic**
   
   If the installation fails, the system will automatically retry up to three times with exponential backoff. If necessary, the user will be prompted with suggestions for resolving installation issues (e.g., upgrading `pip`, checking network connections, etc.).

5. **Custom Dependencies**
   
   If you want to specify custom dependencies, you can modify the `dependencies` list in the `create_virtualenv()` function.

## Code Explanation

### `__init__.py`

This file is used to automatically trigger the library download process when the `library_downloader` module is imported. It calls `start_library_download()` from `downloader.py` which starts the entire process.

from .downloader import start_library_download

# Automatically trigger the library download process when the module is imported
start_library_download()


### `downloader.py`

This file contains the core logic for handling the download process.

#### Key Functions:

- **`extract_version_from_comments()`**: Extracts version constraints from comments in the Python script (e.g., `# Required: requests>=2.0.0`).
  
- **`is_python_compatible()`**: Checks if the current Python version meets the required version for a package.

- **`install_with_retry()`**: Installs a package using `pip` with retries on failure.

- **`create_virtualenv()`**: Creates a virtual environment if it doesn't exist and installs the necessary dependencies within it.

- **`install_dependencies()`**: Installs the list of required dependencies using `pip`.

- **`show_popup()`**: Displays a system notification (using `plyer`) to inform the user of important updates, like installation status or errors.

- **`check_and_install_package()`**: Checks if a package is installed, if not, it attempts to install it (handling errors and retries).

- **`is_standard_library()`**: Checks if a package is part of Python’s standard library (and should not be installed).

- **`show_virtualenv_prompt()`**: Displays a GUI prompt asking the user if they want to create a virtual environment when an installation fails.

- **`start_library_download()`**: The main entry point that reads a script, identifies required libraries, and installs them.

### Logging

The module uses Python's built-in `logging` library to log installation processes, errors, and retries. Logs are written to `library_installation.log`, which can help debug any installation issues.

logging.basicConfig(filename='library_installation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


### Notifications

Notifications are displayed to the user using the `plyer` library. This provides cross-platform notifications for Windows, macOS, and Linux.

## Troubleshooting

1. **Failed Package Installation**:
   - Ensure that `pip` is up to date. If you encounter issues, try upgrading `pip` with:

     pip install --upgrade pip

   - If installing from a virtual environment, check that the virtual environment is activated correctly.

2. **Permissions Errors**:
   - On Unix-like systems (Linux/macOS), you might need elevated permissions to install some packages. Use `sudo` to resolve permission issues:

     sudo pip install <package>


3. **Network Issues**:
   - If installations fail due to network errors (e.g., timeouts), check your internet connection or retry after some time.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements. We welcome contributions!
