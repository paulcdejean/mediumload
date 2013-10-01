class mediumload {
  include apache24
  include phpfpm
  if $medium_config == "false" {
    file { "/etc/mediumload.conf.example":
      mode => 600,
      source => "puppet:///modules/$module_name/mediumload.conf.example",
    }
    
    notify {"For mediumload to fucntion, it needs to be configured to connect to a mediumload database.
      Please see /etc/mediumload.conf.example for more details.":}
  }
  
  file { '/usr/local/var/':
    ensure => "directory",
    mode => 755,
  }
  file { '/usr/local/var/php-fpm/':
    require => File['/usr/local/var/'],
    ensure => "directory",
    mode => 755,
  }
  file { '/usr/local/var/php-fpm/portmap.txt':
    require => File['/usr/local/var/php-fpm/'],
    ensure => "file",
    owner => "root",
    group => "daemon",
    mode => 640,
  }

  # It doesn't hurt to run this every time.
  exec { "/usr/local/bin/httxt2dbm -i portmap.txt -o portmap.dbm":
    cwd => "/usr/local/var/php-fpm/",
    require => File['/usr/local/var/php-fpm/portmap.txt'],
    before => [File['/usr/local/var/php-fpm/portmap.dbm.dir'],
               File['/usr/local/var/php-fpm/portmap.dbm.pag'],
               ],
    #creates => "/usr/local/var/php-fpm/portmap.dbm",
  }

  file { '/usr/local/var/php-fpm/portmap.dbm.dir':
    require => File['/usr/local/var/php-fpm/'],
    ensure => "file",
    owner => "root",
    group => "daemon",
    mode => 640,
  }
  file { '/usr/local/var/php-fpm/portmap.dbm.pag':
    require => File['/usr/local/var/php-fpm/'],
    ensure => "file",
    owner => "root",
    group => "daemon",
    mode => 640,
  }

  file { '/usr/lib/python2.6/site-packages/mediumload.pth':
    mode => 644,
    source => "puppet:///modules/$module_name/mediumload.pth",
  }

  file { '/usr/local/lib64/python/':
    mode => 755,
    ensure => directory,
  }

  file { '/usr/local/lib64/python/mediumcore.py':
    require => File['/usr/local/lib64/python/'],
    mode => 644,
    source => "puppet:///modules/$module_name/mediumcore.py",
  }

  file { '/usr/local/lib64/python/mediumwebsite.py':
    require => File['/usr/local/lib64/python/'],
    mode => 644,
    source => "puppet:///modules/$module_name/mediumwebsite.py",
  }

  file { '/usr/local/etc/php-fpm.conf':
    mode => 644,
    source => "puppet:///modules/$module_name/php-fpm.conf",
  }

  package { 'MySQL-python':
    ensure => installed,
  }
}
