class supervisr_core::users {

  group { 'puppet_systemgroup':
    gid => {{ settings.USER_PROFILE_ID_START }},
  }

  {% for user in User.all %}
  supervisr_core::resources::user { '{{ user.userprofile.unix_username }}':
    id       => {{ user.userprofile.unix_userid }},
    password => '{{ user.userprofile.crypt6_password }}',
    {% if puppet_systemgroup in user.groups.all %}
    shell    => '/bin/bash',
    groups   => ['{{ user.userprofile.unix_username }}', 'puppet_systemgroup'],
    {% endif %}
  }
  {% endfor %}

}
