import json
#import os


class AutoSaveDict(dict):
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.save_to_file()

    def save_to_file(self):
        with open(self.file_path, 'w') as file:
            json.dump(self, file)

    def load_from_file(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            self.update(data)
        except FileNotFoundError:
            print('Backup file not found.')


# # create an instance of AutoSaveDict
# cwd = os.getcwd()
# my_dict = AutoSaveDict(cwd+'/backups/game_state_backup.json')

# # update the dictionary as usual
# my_dict['key'] = 'value'
