#!/usr/bin/python

# Third party modules.
import subprocess
import traceback
import os

# Medium load modules.
import mediumcore

class website:
    """A website managed by mediumload.

    Attributes:
        __id        The id of the website in the database.
        __port      The port that the php-fpm process for the website listens on.
        __user      The user id of the user the php-fpm process runs as.
        __url       The url of the website, and the name of the folder it occupies.

    Cached values:
        __valid     Whether or not the site is valid and can be setup.
        __setup     Whether or not the site has been setup.
       __db        A handle to the medium load database.

    Knobs:
        __min_user  The minimum number mediumload will select for a website user id.
        __max_user  The maximum number mediumload will select for a website user id.
        __min_port  The minimum number mediumload will select for a website listening port.
        __max_port  The maximum number mediumload will select for a website listening port.
        __docroot   The document root in apache.
        __portmap   The file used for the rewritemap in the custom mediumload apache config.
    """
    __id = None
    __port = None
    __user = None
    __url = None

    __valid = True
    __setup = False
    __db = None

    __min_user = 50000
    __max_user = 60000
    __min_port = 50000
    __max_port = 60000
    __docroot = "/usr/local/htdocs/"
    __portmap = "/usr/local/var/php-fpm/portmap.txt"

    def __init__(self, url):
        # Url from user input.
        self.__url = url
        
        # Connect to the database.
        self.__db = mediumcore.mediumdb()
        c = self.__db.cursor()
        c.execute("""select id, port, user, url, created, server, invalid, setup
                     from websites where url = %s""", self.__url)
        result = c.fetchone()

        if result:
            # Use the database values if the website already exists.
            self.__id = result[0]
            self.__port = result[1]
            self.__user = result[2]
            self.__invalid = result[6]
            self.__setup = result[7]
            
        else:
            # Otherwise we initialize the website with available values.
            c = self.__db.cursor()
            c.execute("select user, port from websites")
            self.__user = self.__min_user
            for user in c:
                if user[0] != self.__user:
                    break
                self.__user += 1

            self.__port = self.__min_port
            for port in c:
                if port[1] != self.__port:
                    break
                self.__port += 1

            # Insert this data into the database.
            try:
                c.execute("""insert into websites (port, user, url, created)
                          values(%s, %s, %s, CURDATE())""", 
                          (self.__port, self.__user, self.__url))
            except:
                print "The website could not be initialized due to an error in the data."
                traceback.print_exc()
                return

            self.__db.commit()

            # Use mysql's LAST_INSERT_ID() to get the id.
            c.execute("select LAST_INSERT_ID()")
            self.__id = c.fetchone()[0]

    def setup(self):
        """Sets up a website. Changing it from a database entry to a useable site."""
        if self.__id == None:
            print "This website has no database ID, so it can't be setup."
            return

        if self.__get_valid() == False:
            print "This website is invalid and can not be setup."
            return

        if self.__get_setup(self.__url) == True:
            print "This website has already been sucessfully set up and can not be setup again."
            return

        try:
            self.__setup_user()
            self.__setup_rewritemap()
            self.__setup_folders()

            # Wow! Such magic!
            cycle_pupet()

            self.__set_setup(True)
        except:
            print "There was an error while setting up this website. It has been marked invalid."
            traceback.print_exc()
            self.__set_valid(False)

    def __setup_user(self):
        # The username will be the same as the user id.
        # Initially we had the username be the url, which was good for readability.
        # We ran into problems with username length restrictions however.
        subprocess.check_call(["/usr/sbin/useradd", "-d", self.__docroot + self.__url, "-g", "nobody", "-u", str(self.__user), str(self.__user)])

    def __setup_rewritemap(self):
        with open(self.__portmap, 'a') as portmap:
            portmap.write(self.__url + ' ' + str(self.__port))

    def __setup_folders(self):
        os.chmod(self.__docroot + self.__url, 0750)
        os.chown(self.__docroot + self.__url, self.__user, 0)
        return

    def __get_valid(self):
        if not self.__valid:
            return False
        else:
            c = self.__db.cursor()
            c.execute("select invalid from websites where id = %s", self.__id)
            if c.fetchone()[0] == 1:
                self.__valid = False
                return False
            else:
                return True

    def __set_valid(self, to):
        c = self.__db.cursor()
        if to == False:
            c.execute("update websites set invalid = 1 where id = %s", self.__id)
        else:
            c.execute("update websites set invalid = 0 where id = %s", self.__id)
        self.__db.commit()
        return

    def __set_setup(self, to):
        c = self.__db.cursor()
        if to == True:
            c.execute("update websites set setup = 1 where id = %s", self.__id)
        else:
            c.execute("update websites set setup = 0 where id = %s", self.__id)
        self.__db.commit()
        return

    def __get_setup(self, url):
        if self.__setup:
            return True
        else:
            c = self.__db.cursor()
            c.execute("select setup from websites where id = %s", self.__id)
            if c.fetchone()[0] == 1:
                self.__setup = True
                return True
            else:
                return False

test_site = website("test3.appcenter123.com")
test_site.setup()
