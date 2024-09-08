import os
import json
import pandas as pd

class JsonMetadataLoader:
    def __init__(self, root_dir):
        """
        Initialize the loader with a root directory where JSON files are located.
        
        :param root_dir: The root directory to search for JSON files.
        """
        self.root_dir = root_dir

    def find_json_files(self):
        """
        Recursively find all JSON files in the root directory.

        :return: A list of file paths to JSON files.
        """
        json_files = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.json'):
                    json_files.append(os.path.join(root, file))
        return json_files

    def load_json_files_to_dataframe(self):
        """
        Load the JSON data into a DataFrame and add filename and last folder as columns.

        :return: A pandas DataFrame with all JSON data, including the filename and last folder.
        """
        json_files = self.find_json_files()
        dataframes = []
        for file in json_files:
            with open(file, 'r') as f:
                try:
                    data = json.load(f)
                    # Assuming each JSON is a dictionary-like structure with named columns
                    df = pd.DataFrame(data)
                    df['file_name'] = os.path.basename(file)  # Add file name as a new column
                    df['last_folder'] = os.path.basename(os.path.dirname(file))  # Add last folder name as a new column
                    dataframes.append(df)
                except json.JSONDecodeError:
                    print(f"Error loading {file}")
        if dataframes:
            return pd.concat(dataframes, ignore_index=True)
        else:
            return pd.DataFrame()  # Return empty dataframe if no valid dataframes are loaded
