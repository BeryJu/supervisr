class supervisr_mail::exim {

  include supervisr_core::users::system

  package { 'exim4-daemon-heavy':
    ensure => 'latest',
  }

  file { '/etc/exim4':
    ensure  => directory,
    require => Package['exim4-daemon-heavy'],
    source  => 'puppet:///modules/supervisr_mail/exim',
    recurse => true,
    notify  => Exec['update-exim4.conf'],
  }

  exec { 'update-exim4.conf':
    command => 'update-exim4.conf',
    refreshonly => true,
    provider => 'shell',
  }

}
