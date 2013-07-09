class apache24 {
  file { "/tmp/httpd-2.4.4_x86_64.rpm":
    mode => 644,
    source => "puppet:///modules/$module_name/httpd-2.4.4_x86_64.rpm",
  }
  
  package { 'httpd':
    require => File["/tmp/httpd-2.4.4_x86_64.rpm"],
    provider => 'rpm',
    ensure => installed,
    source => "/tmp/httpd-2.4.4_x86_64.rpm",
  }

  file { "/usr/local/conf/httpd.conf":
    require => Package['httpd'],
    mode => 644,
    source => "puppet:///modules/$module_name/httpd.conf",
  }

  file { '/etc/init.d/httpd':
    require => Package['httpd'],
    mode => 755,
    source => "puppet:///modules/$module_name/httpd",
  }

  service { 'httpd':
    require => File['/etc/init.d/httpd'],
    ensure => running,
    enable => true,
    subscribe => File['/usr/local/conf/httpd.conf'],
    }
}
