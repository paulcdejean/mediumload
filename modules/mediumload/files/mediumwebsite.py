#!/usr/bin/python

# Third party modules.
import subprocess
import traceback
import os
import signal
import shutil

# Medium load modules.
import mediumcore

class mediumwebsite:
    """A website managed by mediumload.

    Attributes:
        __id        The id of the website in the database.
        __port      The port that the php-fpm process for the website listens on.
        __user      The user id of the user the php-fpm process runs as.
        __url       The url of the website, and the name of the folder it occupies.
        __config    The folder where the php-fpm configuration files are.

    Cached values:
        __valid     Whether or not the site is valid and can be setup.
        __setup     Whether or not the site has been setup.
       __db         A handle to the medium load database.

    Knobs:
        __min_user     The minimum number mediumload will select for a website user id.
        __max_user     The maximum number mediumload will select for a website user id.
        __min_port     The minimum number mediumload will select for a website listening port.
        __max_port     The maximum number mediumload will select for a website listening port.
        __docroot      The document root in apache.
        __portmap      The file used for the rewritemap in the custom mediumload apache config.
        __apacheg      The group ID apache uses.
        __fpm_path     The path to the php-fpm binary.
        __fpm_ini      The path to the php-fpm php.ini file.
        __config_base  The name of the folder that the php-fpm config folders are stored in.
        __config_fpm   The file name of the php-fpm configuration file.
        __config_pid   The file name of the file containing the php-fpm process id.
        __fpm_template The file name of the template the individual php-fpm.conf files will be based off of.
        __url_text     The string in config files that we're replacing with the actual url.
        __port_text    The string in config files that we're replacing with the actual port.
        __user_text    The string in config files that we're replacing with the actual user id.

    Public functions:
        start()      Starts the php-fpm process.
        stop()       Stops the php-fpm process.
        setup()      Sets up the foundations of the website.
        get_url()    Returns the url of the webiste.
    """
    __id = None
    __port = None
    __user = None
    __url = None
    __config = None

    __valid = True
    __setup = False
    __db = None

    __min_user = 49000
    __max_user = 60000
    __min_port = 49000
    __max_port = 60000
    __docroot = "/usr/local/htdocs/"
    __portmap = "/usr/local/var/php-fpm/portmap.txt"
    __apacheg = 2
    __fpm_path = "/usr/sbin/php-fpm"
    __fpm_ini = "/etc/php.ini"
    __config_base = "/usr/local/var/php-fpm/"
    __config_fpm = "php-fpm.conf"
    __config_pid = "running.pid"
    __fpm_template = "/usr/local/etc/php-fpm.conf"
    __url_text = "___url___"
    __user_text = "___user___"
    __port_text = "___port___"

    def __init__(self, url):
        # Url from user input.
        self.__url = url
        
        # Connect to the database.
        self.__db = mediumcore.mediumdb()
        c = self.__db.cursor()
        c.execute("""select id, port, user, url, created, server, invalid, setup, config
                     from websites where url = %s""", self.__url)
        result = c.fetchone()

        if result:
            # Use the database values if the website already exists.
            self.__id = result[0]
            self.__port = result[1]
            self.__user = result[2]
            self.__invalid = result[6]
            self.__setup = result[7]
            self.__config = result[8]
            
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

            self.__config = self.__config_base + self.__url + "/"

            # Insert this data into the database.
            try:
                c.execute("""insert into websites (port, user, url, config, created)
                          values(%s, %s, %s, %s, CURDATE())""", 
                          (self.__port, self.__user, self.__url, self.__config))
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

        if self.get_valid() == False:
            print "This website is invalid and can not be setup."
            return

        if self.__get_setup() == True:
            print "This website has already been sucessfully set up and can not be setup again."
            return

        try:
            self.__setup_user()
            self.__setup_rewritemap()
            self.__setup_folders()
            self.__setup_config()

            self.__set_setup(True)
        except:
            print "There was an error while setting up this website. It has been marked invalid."
            traceback.print_exc()
            self.__set_valid(False)

    def start(self):
        """Starts up a website. Running the php-fpm processes with the necesary configuration.
        Only works for sites that are valid and setup."""
        if self.get_valid() and self.__get_setup():
            subprocess.check_call(["/usr/bin/sudo", "-n", "-u", str(self.__user), self.__fpm_path,
                                   "-c", self.__fpm_ini,
                                   "-y", self.__config + self.__config_fpm])

    def stop(self):
        """Stops a currently running website by killing its php-fpm process."""
        with open(self.__config + self.__config_pid, 'r') as pidfile:
            pid = pidfile.read()
            pid = pid.strip()
            os.kill(int(pid), signal.SIGTERM)

    def __setup_user(self):
        # The username will be the same as the user id.
        # Initially we had the username be the url, which was good for readability.
        # We ran into problems with username length restrictions however.
        subprocess.check_call(["/usr/sbin/useradd", "-N", "-d", self.__docroot + self.__url, "-g", "nobody", "-u", str(self.__user), str(self.__user)])

    def __setup_rewritemap(self):
        with open(self.__portmap, 'a') as portmap:
            portmap.write(self.__url + ' ' + str(self.__port) + '\n')
        subprocess.check_call(["/usr/local/bin/httxt2dbm", "-i", self.__config_base + "portmap.txt", "-o", self.__config_base + "portmap.dbm"])

    def __setup_folders(self):
        web_folder = self.__docroot + self.__url
        os.chmod(web_folder, 0750)
        os.chown(web_folder, self.__user, self.__apacheg)
        os.mkdir(self.__config)
        os.chmod(self.__config, 0750)
        os.chown(self.__config, self.__user, self.__apacheg)

        # Remove everything that was copied from skel.
        os.chdir(web_folder)
        for useless_file in os.listdir(web_folder):
            os.unlink(useless_file)
        return

    def __setup_config(self):
        f = open(self.__fpm_template)
        template = f.read()
        result = template.replace(self.__url_text, self.__url)
        result = result.replace(self.__user_text, str(self.__user))
        result = result.replace(self.__port_text, str(self.__port))
        with open(self.__config + self.__config_fpm, "w") as output:
            output.write(result)
        return

    def get_valid(self):
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

    def __get_setup(self):
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

    def get_url(self):
        """Access function for the URL."""
        return self.__url

    def delete(self):
        """Deletes an already existing site. The site doesn't necessarily have to be setup or valid.
        For safety it won't delete a site that is currently running. The site has to be stopped with stop() before it can be deleted."""
        try:
            pidfile = open(self.__config + self.__config_pid, 'r')
            pid = pidfile.read()
            pid = pid.strip()
        except:
            print "No pidfile file found, the site will be deleted"
            pid = None
        if pid != None and not os.kill(int(pid), 0):
            print "Website with url", self.get_url(), "can not be deleted because it is running."
            return
        else:
            print "Website with url", self.get_url(), "will be deleted."
                
            # Delete the config files. The web folder is deleted when the user is removed.
            shutil.rmtree(self.__config)

            # Delete rewrite map.
            mapfile = open(self.__portmap, 'r')
            rewriterules = mapfile.readlines()
            mapfile.close()
            newmap = [ rule for rule in rewriterules if not rule.startswith(self.get_url()) ]
            os.rename(self.__portmap, self.__portmap + ".old")
            newmapfile = open(self.__portmap, 'w')
            newmapfile.writelines(newmap)
            
            # Delete user.
            subprocess.check_call(["/usr/sbin/userdel", "-r", str(self.__user)])

            # Delete database entry.
            c = self.__db.cursor()
            c.execute("delete from websites where url = %s", self.get_url())
            
            # Mark as invalid.
            self.__set_valid(False)
        return

def get_all_websites(server=None):
    """Gets a list of all the websites that currently exist.
    If the server argument isn't included, then all the websites will be returned.
    If the server argument is included, then all the websites on that servers will be returned."""    
    result = []

    db = mediumcore.mediumdb()
    c = db.cursor()
    c.execute("select url from websites")
    for url in c:
        result.append(mediumwebsite(url[0]))
    return result
