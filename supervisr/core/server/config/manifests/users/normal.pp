# This class creates all normal users
class supervisr_core::users::normal {

  {% for user in User.all %}
  {% if puppet_systemgroup not in user.groups.all %}
  supervisr_core::resources::user { '{{ user.unix_username }}':
    id       => {{ user.unix_userid }},
    password => '{{ user.crypt6_password }}',
  }
  {% endif %}
  {% endfor %}

}
