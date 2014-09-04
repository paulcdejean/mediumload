class phpfpm {
  package { 'php-fpm':
    ensure => installed,
  }

  file { '/etc/init.d/php-fpm':
    require => Package['php-fpm'],
    mode => 755,
    source => "puppet:///modules/$module_name/php-fpm",
  }

  file { '/etc/php.ini':
    require => Package['php-fpm'],
    mode => 644,
    source => "puppet:///modules/$module_name/php.ini",
  }

  service { 'php-fpm':
    require => [File['/etc/php.ini'], File['/etc/init.d/php-fpm']],
    enable => true,
    subscribe => File['/etc/php.ini'],
  }

  # Lets get some memcached up in this.
  package { 'memcached':
    ensure => installed,
  }

  service { 'memcached':
    ensure => running,
    enable => true,
  }

  package { 'php-pecl-memcached':
    ensure => installed,
    notify => Service['php-fpm'],
  }

  package { 'php-pecl-memcache':
    ensure => installed,
    notify => Service['php-fpm'],
  }
  
}
