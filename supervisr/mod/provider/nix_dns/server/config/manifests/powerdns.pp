# Install and configure PowerDNS
class supervisr_nix_dns::powerdns {

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

  $files = ['pdns.conf', 'pdns.d/supervisr_gmysql.conf']
  $files.each |String $file| {
    file { "/etc/powerdns/${file}":
      ensure  => file,
      require => Package['pdns-server'],
      source  => "puppet:///modules/supervisr_dns/powerdns/${file}",
      notify  => Service['pdns'],
    }
  }

}
