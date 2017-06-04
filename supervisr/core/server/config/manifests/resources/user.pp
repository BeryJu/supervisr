# Manages a customer as unix user
#
# @param customer_name Name of the Customer/Unix user. No special chars. Defaults to $title.
# @param password Crypt-Formatted Hash of User Password. Defaults to '!!' (disabled password).
# @param shell Shell of the user. Defaults to sftp-server.
# @param groups Groups the user belongs to. Defaults to $title.
# @param id Id of the Customer/Unix user. Starts at 5000. Defaults to undef.
# @param nginx_group Group under which nginx runs. Defaults to 'www-data'.
# @param root_path Root to prepend for customer directory creation.
define supervisr_core::resources::user (
  String        $customer_name = $title,
  String        $password      = '!!',
  String        $shell         = '/usr/lib/sftp-server',
  Array[String] $groups        = [$title],
  Integer       $id            = undef,
  String        $nginx_group   = 'www-data',
  String        $root_path     = '/srv/sites/',
) {

  group { $customer_name:
    ensure => 'present',
    gid    => $id,
  }

  user { $customer_name:
    ensure     => 'present',
    shell      => $shell,
    password   => $password,
    groups     => $groups,
    gid        => $id,
    uid        => $id,
    require    => Group[$customer_name],
    home       => "${root_path}/${customer_name}",
    managehome => true,
  }

  @php::fpm::pool { $customer_name:
    listen          => "/var/run/php5-${customer_name}.sock",
    listen_owner    => 'www-data',
    listen_group    => 'www-data',
    user            => $customer_name,
    group           => $customer_name,
    pm_max_requests => 500,
    pm_max_children => 100,
    require         => User[$customer_name],
  }

  if !defined(File[$root_path]) {
    file { $root_path:
      ensure => 'directory'
    }
  }

  file { "${root_path}/${customer_name}":
    ensure  => 'directory',
    group   => $customer_name,
    owner   => $customer_name,
    mode    => '0770',
    require => File[$root_path],
  }

}
