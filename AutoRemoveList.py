import threading

class AutoRemoveList:
    def __init__(self, delay=1):
        self.delay = delay
        self.elements = []

    def add(self, item):
        self.elements.append(item)
        threading.Timer(self.delay, self._remove, args=[item]).start()

    def get(self):
        return self.elements

    def _remove(self, item):
        if item in self.elements:
            self.elements.remove(item)

    def __repr__(self):
        return repr(self.elements)
