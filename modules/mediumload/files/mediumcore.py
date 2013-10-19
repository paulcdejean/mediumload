import MySQLdb

class mediumconf:
    """An abstraction layer for the mediumload configuration.

    Attributes:
        __cache       The values of the config file cached.
        __file        The config file handle.

    Knobs:
        __conf_file   The path to the medium load database configuration file.
    """

    __cache = {}
    __file = None

    __conf_file = "/etc/mediumload.conf"

    def __init__(self):
        self.__file = open(self.__conf_file, 'r')

    def get(self, value):
        result = None
        
        if value in self.__cache.keys():
            return self.__cache[value]

        for line in self.__file:
            splitline = line.split("=", 1)
            linekey = splitline[0].strip()

            # Just to make sure we don't get comments.
            if linekey[0] == "#":
                continue

            if linekey == value:
                result = splitline[1].strip()
                self.__cache[value] = result
                return result
        return None

class mediumdb:
    """The database backend for mediumload.

    Attributes:
        __database    The MySQLdb database object for the mediumload database.
        
    Knobs:
        __conf_file   The path to the medium load database configuration file.
    """
    __database = None

    def __init__(self):
        address = None
        username = None
        password = None
        database = None

        conf = mediumconf()
        address = conf.get("address")
        username = conf.get("username")
        password = conf.get("password")
        database = conf.get("database")

        self.__database = MySQLdb.connect(user=username, passwd=password, host=address, db=database)

    def cursor(self):
        return self.__database.cursor()

    def commit(self):
        self.__database.commit()
