import os
import re


class BasicModel:

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.folder_path = os.path.join(os.path.dirname(current_dir), 'uploads')

    
    def find_pdf_file(self):
        for file in os.listdir(self.folder_path):
            if (file.lower().endswith('.xlsx') or file.lower().endswith('.xls')) and file.lower().startswith('received'):
                return self.folder_path + '/' + file

    def regex_finder(self, text):
        pattern = r'\b\d{2,4}[-./]\d{2}[-./]\d{2,4}\b'
        matches = re.findall(pattern, text)

        if matches:
            return True
        return False
            

basic_model = BasicModel()