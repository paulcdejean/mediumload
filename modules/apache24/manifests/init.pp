class apache24 {
  package { 'git':
    ensure => present,
  }
  notify {"Hello apache :)":}
}
