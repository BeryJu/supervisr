class supervisr_core::users {

  group { 'puppet_systemgroup':
    gid => {{ settings.USER_PROFILE_ID_START }},
  }

  {% for user in puppet_systemgroup.user_set.all %}
  {% if user.userprofile %}
  user { '{{ user.userprofile.unix_username }}':
    name       => '{{ user.userprofile.unix_username }}',
    ensure     => present,
    managehome => true,
    home       => "/home/{{ user.userprofile.unix_username }}",
    gid        => {{ settings.USER_PROFILE_ID_START }},
    groups     => ['sudo'],
    shell      => '/bin/bash',
    uid        => {{ user.userprofile.unix_userid}}
  }
  {% endif %}
  {% endfor %}

}
