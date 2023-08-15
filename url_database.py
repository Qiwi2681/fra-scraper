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

    # load seen urls, update the sets, return uniques
    def update(self, method, *args):
        # get current set
        self.current = method(*args)

        # load seen from .pkl
        try:
            if self.seen == {}:
                self.load()
        except AttributeError:
            self.load()

        # get 'new' urls
        unique = self.current - self.seen

        print(f'found {len(unique)} new urls')

        # update seen & cleanup
        self.seen.update(self.current)
        self.save()

        return unique
