import sys
import importlib
import subprocess
import logging
from .downloader import install_with_lock  # Import the new function with lock

# Automatically trigger the library download process when the module is imported
class LibraryImportHook:
    def find_spec(self, name, path, target=None):
        """Triggered whenever a module is imported"""
        # Check if the module is already installed, otherwise try installing it
        try:
            importlib.import_module(name)
        except ImportError:
            # If the module is not installed, attempt to install it with a lock
            install_with_lock(name)  # Use the new function with lock
        return None

# Register the import hook globally
sys.meta_path.insert(0, LibraryImportHook())

