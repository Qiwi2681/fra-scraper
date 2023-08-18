import os
import pickle

# memory efficent url filter
class URLDatabase():
    def __init__(self, filename):
        self.filename = filename + '.pkl'
        self.current = set()
        self.seen = set()

    # loads the bytestream to memory in self.seen
    def load(self):
        try:
            with open(self.filename, 'rb') as file:
                data = pickle.load(file)
                self.seen = data.get('seen', set())
        except FileNotFoundError:
            self.seen = set()

    # dumps self.seen to bytestream and unloads the set from memory
    def save(self):
        data = {'seen': self.seen}
        with open(self.filename, 'wb') as file:
            pickle.dump(data, file)
        self.seen = set()

    def set_current(self, urls: set):
        self.current = urls

    def get_unique(self):
        self.load()
        unique = self.current - self.seen
        print(self.current, self.seen)
        self.seen.update(self.current)
        self.save()

        return unique

    def clear(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
            self.seen = set()
