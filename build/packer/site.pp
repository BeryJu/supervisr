node default {

  include ::redis
  include '::mysql::server'

  apt::source { 'beryju.org':
    location => 'https://apt.beryju.org/',
    release  => 'stable',
    repos    => 'beryjuorg',
    key      => {
      'id'     => 'EEB2544FAA2FC778E6C77C994C66B2475FD29847',
      'source' => 'https://apt.beryju.org/public.key',
    }
  }->package { 'supervisr':
    ensure => 'latest',
  }

}
