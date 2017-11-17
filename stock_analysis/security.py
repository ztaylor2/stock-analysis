"""Security settings to configure login, logout, and user registration."""

import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow
from .models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)

from stock_analysis.models.mymodel import User


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


def is_authorized(request, username, password):
    """Check user-provided credentials compared to users stored in the database."""
    result = request.dbsession.query(User).get(username)
    return result.password == password
