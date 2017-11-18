# This class creates all system users and administrators
class supervisr_core::users::system {

  group { 'supervisr_system':
    gid => {{ settings.USER_PROFILE_ID_START }},
  }

  {% for user in User.all %}
    {% if puppet_systemgroup in user.groups.all %}
    user { '{{ user.unix_username }}':
      uid      => {{ user.unix_userid }},
      gid      => {{ settings.USER_PROFILE_ID_START }},
      password => '{{ user.crypt6_password }}',
      shell    => '/bin/bash',
      groups   => ['supervisr_system'],
    }
    {% endif %}
  {% endfor %}

}
