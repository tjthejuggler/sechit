class GameSummary:
    def __init__(self, summary=None):
        if summary is None:
            self.summary = []
        else:
            self.summary = summary
    
    def read(self):
        return self.summary
    
    def append(self, new_entry):
        self.summary.append({"role": new_entry[0], "content": new_entry[1]})
