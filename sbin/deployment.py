#!/usr/bin/python
import MySQLdb
import os
import subprocess
from ssh import ssh

class deployment:
	"""A site of a appcenter app."""
	# Constants.
	db_name = "appcenter123"
	db_user = "teamcity"
	db_password = "vAPDUgqR9J39"
	fpm_configs = "/usr/local/var/php5-fpm/"

	# Connection.
	database_connection = None
	c = None

	# Core values.
	reseller_id = None
	app_id = None
	commit_id = None
	domain = None
	magic_number = None
	server_web_id = None
	app_name = None

	# Cached values.
	remote_repo = None
	local_repo = None
	server_web_dns = None

	# Constructors.
	def grab_existing(self, domain):
		"""Gets an existing deployment from the deployments database"""
		self.c.execute("select reseller_id, app_id, commit_id, magic_number, server_web from deployments where domain = %s;", domain)
		results = self.c.fetchone()
		self.reseller_id = results[0]
		self.app_id = results[1]
		self.commit_id = results[2]
		self.domain = domain
		self.magic_number = results[3]
		self.server_web_id = results[4]

	def __init__(self, domain, reseller=None, app=None, server=None, version=None):
		"""Creates a instance from the supplied values, ready for deployment."""
		self._database_connect()

		# I hate not having multiple constructors.
		if not reseller or not app:
			self.grab_existing(domain)
			return

		if not version:
			version = "master"

		# Fill in the reseller_id.
		self.c.execute("select id from resellers where domain = %s;", reseller)
		self.reseller_id = self.c.fetchone()[0]

		# Fill in the app_id.
		self.c.execute("select id from apps where name = %s;", app)
		self.app_id = self.c.fetchone()[0]
		self.app_name = app

		# Fill in the commit_id.
		os.chdir(self._get_local_repo())
		proc = subprocess.Popen(["git", "log", "-n", "1", version], stdout = subprocess.PIPE)
		self.commit_id = proc.stdout.read(47)[7:47]

		# Fill in the domain.
		self.domain = domain

		# Fill in the magic number with the smallest magic number that isn't used.
		available_magic_numbers = range(50000, 60000)
		self.c.execute("select magic_number from deployments where magic_number is not null;")
		for row in self.c:
			available_magic_numbers.remove(row[0])
		self.magic_number =  min(available_magic_numbers)

		# Fill in the server_web_id.
		self.c.execute("select default_server_web from apps where name = %s;", app)
		self.server_web_id = self.c.fetchone()[0]

	# Private methods.
	def _database_connect(self):
		if not self.database_connection:
			self.database_connection = MySQLdb.connect(user = self.db_user,
			                                           passwd = self.db_password,
			                                           db = self.db_name)
			self.c = self.database_connection.cursor()

	def _get_local_repo(self):
		return "/usr/local/var/repositories/" + self.app_name

	def _get_web_server(self):
		if not self.server_web_dns:
			self.c.execute("select dns from servers where id = %s;", self.server_web_id)
			self.server_web_dns = self.c.fetchone()[0]
		return self.server_web_dns
	def _add_to_database(self):
		self.c.execute("""insert into deployments (reseller_id, app_id, commit_id, domain, magic_number, server_web) values
		               (%s, %s, %s, %s, %s, %s);""", 
		               (self.reseller_id, self.app_id, self.commit_id, self.domain, self.magic_number, self.server_web_id))
		self.c.execute("commit;");

	# Public methods.
	def get_magic_number(self):
		return self.magic_number

	def get_default_database_server_address(self):
		# Thank you Mario.
		self.c.execute("""SELECT
		               servers.dns
		               FROM
		               deployments
		               Inner Join apps ON deployments.app_id = apps.id
		               Inner Join servers ON apps.default_server_db = servers.id
		               where deployments.domain = %s;""", self.domain)
		return self.c.fetchone()[0]

	def get_language(self):
		return "en"

	def get_timezone(self):
		return -5

	def get_country(self):
		return "us"

	def deploy_to_production(self):
		"""Deploys the site to the production environment."""
		s = ssh(self._get_web_server())
		status = s.do("useradd -b /var/www -g sites -s /bin/bash -u {0} {1}".format(self.magic_number, self.domain))
		if status != 0:
			print "useradd -b /var/www -g sites -s /bin/bash -u {0} {1}".format(self.magic_number, self.domain)
			print "useradd error."
		        exit(1)
		s.do("mkdir /var/www/{0}".format(self.domain))


		os.chdir(self._get_local_repo())
		subprocess.call(["git", "checkout", "-q", self.commit_id])
		subprocess.call(["rsync", "-rvc", "--exclude=/.git/", ".", "{0}:/var/www/{1}".format(self._get_web_server(), self.domain)])
		s.do("chown -R {0}:daemon /var/www/{0}".format(self.domain))
		s.do("chmod o-rx /var/www/{0}".format(self.domain))

		# Deploy the php-fpm configuration and fix its permissions.
		s.do("mkdir {1}{0}".format(self.domain, self.fpm_configs))
		s.put("/usr/local/etc/php-fpm.conf", "{1}{0}/php-fpm.conf".format(self.domain, self.fpm_configs))
		s.do("sed -i -e 's/%DOMAIN%/{0}/g' -e 's/%MAGIC_NUMBER%/{1}/' '{2}{0}/php-fpm.conf'".format(self.domain,
		                                                                                            self.magic_number,
		                                                                                            self.fpm_configs))
		s.do("chown -R {0}:sites {1}{0}".format(self.domain, self.fpm_configs))
		s.do("chmod og-rx {1}{0}".format(self.domain, self.fpm_configs))

		# Start up php-fpm for this user.
		s.do("sudo -u {0} /usr/sbin/php5-fpm -c {1}{0}/php.ini -y {1}{0}/php-fpm.conf".format(self.domain, self.fpm_configs))
		s.do("echo '{0} {1}' >> '{2}portmap.txt'".format(self.domain, self.magic_number, self.fpm_configs))
		s.do("httxt2dbm -v -i {0}portmap.txt -o {0}portmap.dbm".format(self.fpm_configs))

		# TEMP TEMP TEMP TEMP TEMP TEMP TEMP TEMP TEMP TEMP TEMP TEMP
		s.do("rm /tmp/include_path.log")
		s.close()

		self._add_to_database()
