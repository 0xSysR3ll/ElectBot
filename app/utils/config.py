"""
This module provides functionalities to manage configuration files using the YAML format.
"""

import os
import sys
import yaml

class Config:
    """
    A class to handle operations related to a configuration file.
    
    Attributes:
        filename (str): The path to the configuration file.
        data (dict): A dictionary containing the loaded configuration data.
    """

    def __init__(self, filename):
        """
        Initializes the Config class with a filename and an empty data dictionary.

        Args:
            filename (str): The path to the configuration file.
        """
        self.filename = filename
        self.data = {}

    def load(self):
        """
        Loads the configuration data from the specified file into the data dictionary.

        Raises:
            SystemExit: If the configuration file is not found.
        """
        if not os.path.isfile(self.filename):
            sys.exit(f"{self.filename} not found! Please add it and try again.")
        else:
            with open(self.filename, 'r', encoding='utf-8') as file:
                self.data = yaml.safe_load(file)

    def get_config(self, key, value=None):
        """
        Retrieves a specific configuration value from the data dictionary.

        Args:
            key (str): The primary key to look up in the data dictionary.
            value (str, optional): The secondary key to look up if present. Defaults to None.

        Returns:
            The requested configuration value or a dictionary of values.
        """
        if value:
            return self.data[key][value]
        return self.data[key]
