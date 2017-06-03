# -*- coding: utf-8 -*-
import logging


def get_saml_logger():
    """
    Get a logger named `saml2idp` after the main package.
    """
    return logging.getLogger('supervisr.mod.saml_idp')
