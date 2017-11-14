"""Security settings to configure login, logout, and user registration."""

import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow


def includeme(config):
    """Security includeme."""
    auth_secret = os.environ.get('AUTH_SECRET', 'secretpotato')
    authn_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg='sha512'
    )
    config.set_authentication_policy(authn_policy)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('view')
    config.set_root_factory(SecRoot)


class SecRoot(object):
    """Security root class."""

    def __init__(self, request):
        """Initializing ACL."""
        self.request = request

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'secret'),
    ]


def check_credentials(username, password):
    """Check user-provided credentials compared to users stored in the database."""
    # submitted_username = os.environ.get('AUTH_USERNAME', '')
    # submitted_password = os.environ.get('AUTH_PASSWORD', '')
    is_authenticated = False
    if stored_username and stored_password:
        if username == stored_username:
            if password == stored_password:
                is_authenticated = True
    return is_authenticated
