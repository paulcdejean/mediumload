include stdlib
include firewall

resources { "firewall":
  purge => true
}

firewall { '000 Accept related and established.':
  proto   => 'all',
  state => ['RELATED', 'ESTABLISHED'],
  action  => 'accept',
}

firewall { '001 Accept all icmp.':
  proto   => 'icmp',
  action  => 'accept',
}

firewall { '002 Accept all loopback.':
  proto   => 'all',
  iniface => 'lo',
  action  => 'accept',
}

firewall { '100 Accept ssh.':
  port   => 22,
  proto  => tcp,
  action => accept,
}

firewall { '999 Reject everything not explicitly accepted.':
  proto  => 'all',
  action => 'reject',
  reject => 'icmp-host-prohibited',
}

firewall { '999 Reject everything in the forward chain.':
  proto  => 'all',
  chain  => 'FORWARD',
  action => 'reject',
  reject => 'icmp-host-prohibited',
}

include mediumload

