import pickle
"""memory efficient class to manage urls"""


class URLDatabase():
    def __init__(self, filename):
        self.filename = filename + '.pkl'
        self.current = set()

    # loads the bytestream to memory in self.seen
    def load(self):
        try:
            with open(self.filename, 'rb') as file:
                data = pickle.load(file)
                # attribute is loaded regardless
                self.seen = data.get('seen', set())
        except FileNotFoundError:
            print(f'File not found: {self.filename}')
            self.seen = set()

    # dumps self.seen to bytestream and unloads the set from memory
    def save(self):
        data = {'seen': self.seen}
        with open(self.filename, 'wb') as file:
            pickle.dump(data, file)
        self.seen = set()
