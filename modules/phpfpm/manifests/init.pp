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
}
