###################################
# Exceptions
###################################

class FileExistsException(Exception):
    def __init__(self, filepath, limit):
        self.error = "File \"{0}\" already exist and we reached the limit of {1} copies".format(filepath, limit)

    def __str__(self):
        return self.error


class FileUnwritableException(Exception):
    def __init__(self, filepath, error):
        self.error = "Error trying to create file \"{0}\": {1}".format(filepath, error)

    def __str__(self):
        return self.error

