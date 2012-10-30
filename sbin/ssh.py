import sys
import warnings
# http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=586925
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import paramiko

class ssh:
    def __init__(self, remote):
	self.connection = paramiko.SSHClient()
	self.connection.load_system_host_keys()
	self.connection.connect(remote)

	self.sftp = paramiko.SFTPClient.from_transport(self.connection.get_transport())
    def do(self, command):
	self.session = self.connection.get_transport().open_session()
	self.session.exec_command(command)
	sys.stdout.write(self.session.recv(None))
	sys.stdout.flush()
	sys.stderr.write(self.session.recv_stderr(None))
	sys.stderr.flush()
	return self.session.recv_exit_status()
    def put(self, source, destination):
	self.sftp.put(source, destination)
    def close(self):
	self.connection.close()
