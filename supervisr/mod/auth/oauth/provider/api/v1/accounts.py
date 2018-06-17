"""supervisr oauth account API wrapper"""
from oauth2_provider.views import ProtectedResourceView
from supervisr.core.api.v1.accounts import AccountAPI


# pylint: disable=too-many-ancestors
class OAuthAccountAPI(ProtectedResourceView, AccountAPI):
    """OAuth Wrapper for Account API"""
    pass
