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
}
