class mediumbackup {
  include apache24

  package { 'glibc-devel':
    ensure => installed,
  }
  package { 'openssl-devel':
    ensure => installed,
  }
  package { 'zlib-devel':
    ensure => installed,
  }
  package { 'e2fsprogs-devel':
    ensure => installed,
  }

  file { '/usr/local/sbin/mediumwebbackup.py':
    require => [File['/usr/local/lib64/python/mediumwebsite.py'],
                File['/usr/local/lib64/python/mediumcore.py']],
    mode => 755,
    source => "puppet:///modules/$module_name/mediumwebbackup.py",
  }

  file { '/usr/local/sbin/mediumdbbackup.py':
    require => [File['/usr/local/lib64/python/mediumwebsite.py'],
                File['/usr/local/lib64/python/mediumcore.py']],
    mode => 755,
    source => "puppet:///modules/$module_name/mediumdbbackup.py",
  }

  cron { web_backup:
    require => File['/usr/local/sbin/mediumwebbackup.py'],
    command => "/usr/local/sbin/mediumwebbackup.py",
    user    => root,
    hour    => 1,
    minute  => 0
  }

  cron { database_backup:
    require => File['/usr/local/sbin/mediumdbbackup.py'],
    command => "/usr/local/sbin/mediumdbbackup.py",
    user    => root,
    hour    => 1,
    minute  => 0
  }
}
