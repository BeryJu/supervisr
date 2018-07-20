"""supervisr common regexs"""


DOMAIN_REGEX = (r'([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.'
                r'([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*')
EMAIL_DOMAIN_REGEX = DOMAIN_REGEX
EMAIL_ADDRESS_REGEX = r'[a-zA-Z0-9_.+-/]+'

EMAIL_REGEX = r'%s@%s' % (EMAIL_ADDRESS_REGEX, DOMAIN_REGEX)

UUID_REGEX = r'[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'

# Regex used to match modules for admin/modules
MOD_REGEX = r'[a-zA-Z0-9/._]+'

SLUG_REGEX = r'[-\w]+'
