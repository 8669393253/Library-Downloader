# Library Installation and Import Monitoring

This repository contains two Python scripts that aim to automatically manage the installation of libraries when they are imported and also ensure compatibility with specified versions. The system checks whether the necessary packages are installed and attempts to install missing ones. Additionally, the scripts handle issues like network failures, version compatibility, and the option to create a virtual environment if needed.

## Table of Contents

1. [Overview](#overview)
2. [Setup Instructions](#setup-instructions)
3. [Usage](#usage)
4. [Features](#features)
5. [Dependencies](#dependencies)
6. [Logging](#logging)
7. [Error Handling](#error-handling)
8. [License](#license)

## Overview

The two Python scripts work together to automate the process of checking and installing required libraries for your projects.

- **First Script**: Uses a custom import hook to monitor when a library is imported and automatically attempts to install it if it is not already installed. 
- **Second Script**: Provides more robust functionality to manage package installations, including creating a virtual environment if needed, handling version compatibility, retry mechanisms for installations, and offering user prompts through graphical notifications.

## Setup Instructions

To use these scripts, ensure that Python is installed on your system. You can use these scripts on any platform (Windows, macOS, Linux) that supports Python.

### 1. Clone the repository (if applicable)
   ```
   git clone <repository_url>
   cd <repository_folder>
   ```

### 2. Install Dependencies

Before running the scripts, you need to install the required dependencies. You can install them using `pip`:

```
pip install filelock plyer packaging
```

These libraries are used for locking mechanisms, notifications, and version parsing.

## Usage

The two scripts can be used together for seamless package management. When you run the scripts, they will monitor imports and install any missing dependencies.

### Running the Scripts

1. **First Script** (`LibraryImportHook`):

   The `LibraryImportHook` module will automatically install missing libraries when they are imported in your project. It uses the `install_with_lock` function to ensure no concurrent installation attempts for the same package.

   To use this script:
   - Simply import this module in your Python code, and it will automatically trigger the installation process when necessary.
   ```python
   import sys
   from library_import_hook import LibraryImportHook
   ```

2. **Second Script** (`Library Management`):

   The second script offers more control, including features such as:
   - Automatic package installation with retry mechanisms.
   - Creating virtual environments for isolated package management.
   - Compatibility checks for the installed Python version.
   - GUI prompts for virtual environment creation when installation fails.

   You can run this script directly from the command line or incorporate it into your project:
   ```python
   from library_management import start_monitoring
   start_monitoring()
   ```

## Features

### 1. **Automatic Package Installation**

   When a library is imported but not installed, the first script automatically installs it. If the package is already installed, the import proceeds without any interruptions.

### 2. **Handling Installation Failures**

   The second script includes a retry mechanism with exponential backoff, providing multiple attempts to install packages and handle network or dependency conflicts. If the installation fails after multiple attempts, the system logs the error and provides useful feedback to the user.

### 3. **Version Compatibility**

   Both scripts can handle version compatibility checks, ensuring that your packages are compatible with the current Python version.

### 4. **Virtual Environment Management**

   The second script allows you to create a virtual environment if you are not already working within one. This ensures that the required packages are installed in an isolated environment, preventing conflicts with other projects.

### 5. **Graphical User Interface Prompts**

   If an installation fails, the second script will prompt the user to create a virtual environment via a Tkinter message box, providing an easy way for users to manage their Python environments.

### 6. **Logging**

   Both scripts log their actions, such as package installation attempts and errors, into a `library_installation.log` file. This helps you keep track of actions taken by the scripts.

### 7. **Cross-Platform Support**

   The scripts support both Windows and Unix-based systems (Linux/macOS). They automatically adjust the paths for virtual environments and lock files based on the operating system.


## Dependencies

- **filelock**: A Python package that implements a file-based locking mechanism, ensuring that only one installation process runs for a given package at any time.
- **plyer**: A cross-platform library for sending notifications to the user (used for GUI prompts).
- **packaging**: A library for handling and comparing package versions in Python.
- **tkinter**: Used for creating pop-up dialog boxes for user interaction (on installation failure).
- **sysconfig**: Used to get standard library paths for checking if a package is part of the Python standard library.

Install the dependencies using the following:
```bash
pip install filelock plyer packaging
```

## Logging

The scripts log important events and errors into a log file called `library_installation.log`. The logging configuration includes timestamps, logging levels (INFO, ERROR), and descriptive messages, which helps in troubleshooting any issues related to package installation.

Example log entry:
```
2024-12-14 10:30:02,123 - INFO - Successfully installed requests
2024-12-14 10:35:45,987 - ERROR - Failed to install flask after 3 attempts.
```


## Error Handling

The script has built-in error handling for common issues such as:

1. **Network Issues**: If the network is down or the package cannot be fetched, the script retries several times with exponential backoff.
2. **Pip Errors**: If `pip` encounters issues, the script suggests upgrading `pip` or using a virtual environment to avoid conflicts.
3. **File Locking**: The script uses `filelock` to avoid multiple concurrent installation attempts for the same package, ensuring safe package installation.
4. **Virtual Environment Creation**: If installation fails and the user is not in a virtual environment, the script offers to create one and retry the installation.


## License

This project is licensed under the MIT License. See the LICENSE file for more details.
