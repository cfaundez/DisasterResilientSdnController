class Loggable:
    _is_verbose = True

    def print_verbose_log(self, text):
        if self.is_verbose():
            print(self.__class__.__name__ + ": " + text)

    def print_log(self, text):
        print(self.__class__.__name__ + ": " + text)

    def is_verbose(self):
        return self._is_verbose

    def set_verbose(self, boolean):
        _is_verbose = boolean

