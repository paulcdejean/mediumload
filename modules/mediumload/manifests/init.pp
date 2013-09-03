class mediumload {
  include apache24
  include phpfpm
  if $medium_config == "false" {
    file { "/etc/mediumload.conf.example":
      mode => 644,
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
}

