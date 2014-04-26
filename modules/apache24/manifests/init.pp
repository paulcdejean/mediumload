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

  $subdomains = hiera('subdomains')
  $domain_name = hiera('domain_name')
  $cert_path = hiera('cert_path')
  $key_path = hiera('key_path')
  
  notify{ $domain_name :}
  
  file { "/usr/local/conf/httpd.conf":
    require => Package['httpd'],
    mode => 644,
    content => template("$module_name/httpd.conf.erb"),
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
