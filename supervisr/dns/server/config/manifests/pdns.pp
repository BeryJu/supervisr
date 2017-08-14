class supervisr_dns::powerdns {

  include supervisr_core::users::system

  package { ['pdns-server', 'pdns-backend-mysql', 'dnsutils']:
    ensure => 'latest',
  }

  package { 'pdns-backend-bind':
    ensure => 'absent',
  }

  service { 'pdns':
    ensure  => 'running',
    require => Package['pdns-server'],
  }

  file { '/etc/powerdns/':
    ensure  => directory,
    require => Package['pdns-server'],
    source  => 'puppet:///modules/supervisr_dns/powerdns',
    recurse => true,
    purge   => true,
    notify  => Service['pdns'],
  }

}
