import json
import os


class AutoSaveDict(dict):
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        self.parent_dir = os.path.dirname(self.file_path)
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.save_to_file()

    def save_to_file(self):
        #make a copy of self.summary
        backup_copy = self.copy()
        if "player_roles" in self:
            with open(self.parent_dir+"/player_roles.txt", 'w') as file:
                json.dump(self["player_roles"], file)
        
            backup_copy.pop("player_roles")

        with open(self.file_path, 'w') as file:
            json.dump(backup_copy, file)

    def load_from_file(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            self.update(data)
        except FileNotFoundError:
            print('Backup file not found.')
        try:
            with open(self.parent_dir+"/player_roles.txt", 'r') as file:
                data = json.load(file)
            self["player_roles"] = data
        except FileNotFoundError:
            print('Backup file not found.')





# # create an instance of AutoSaveDict
# cwd = os.getcwd()
# my_dict = AutoSaveDict(cwd+'/backups/game_state_backup.json')

# # update the dictionary as usual
# my_dict['key'] = 'value'
