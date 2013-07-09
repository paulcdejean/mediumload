class phpfpm {
  package { 'php-fpm':
    ensure => installed,
  }
}
