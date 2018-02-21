### OmniAuth Settings
###! Docs: https://docs.gitlab.com/ce/integration/omniauth.html
gitlab_rails['omniauth_enabled'] = true
gitlab_rails['omniauth_allow_single_sign_on'] = ['saml']
gitlab_rails['omniauth_sync_email_from_provider'] = 'saml'
gitlab_rails['omniauth_sync_profile_from_provider'] = ['saml']
gitlab_rails['omniauth_sync_profile_attributes'] = ['email']
gitlab_rails['omniauth_auto_sign_in_with_provider'] = 'saml'
gitlab_rails['omniauth_block_auto_created_users'] = false
# gitlab_rails['omniauth_auto_link_ldap_user'] = false
gitlab_rails['omniauth_auto_link_saml_user'] = true
# gitlab_rails['omniauth_external_providers'] = ['twitter', 'google_oauth2']
gitlab_rails['omniauth_providers'] = [
  {
    name: 'saml',
    args: {
      assertion_consumer_service_url: 'https://<gitlab install url>/users/auth/saml/callback',
      idp_cert_fingerprint: '<cert fingerprint from /app/mod/auth/saml/idp/settings/SAML2/IDP/>',
      idp_sso_target_url: 'https://<supervisr install url>/app/mod/auth/saml/idp/login/',
      issuer: 'https://<gitlab install url>',
      name_identifier_format: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddresos',
      attribute_statements: {
        email: ['urn:oid:1.3.6.1.4.1.5923.1.1.1.6'],
        first_name: ['urn:oid:2.5.4.3'],
        nickname: ['urn:oid:2.16.840.1.113730.3.1.241']
      }
    },
    label: 'Supervisr'
  }
]
