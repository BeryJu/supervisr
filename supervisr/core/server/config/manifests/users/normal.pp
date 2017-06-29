# This class creates all normal users
class supervisr_core::users::normal {

  {% for user in User.all %}
  {% if puppet_systemgroup not in user.groups.all %}
  supervisr_core::resources::user { '{{ user.userprofile.unix_username }}':
    id       => {{ user.userprofile.unix_userid }},
    password => '{{ user.userprofile.crypt6_password }}',
  }
  {% endif %}
  {% endfor %}

}
