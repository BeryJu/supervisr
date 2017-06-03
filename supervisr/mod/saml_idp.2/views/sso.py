
from supervisr.mod.saml_idp.service import Service

class SSO(Service):

    def __init__(self, environ, start_response, user=None):
        Service.__init__(self, environ, start_response, user)
        self.binding = ""
        self.response_bindings = None
        self.resp_args = {}
        self.binding_out = None
        self.destination = None
        self.req_info = None
        self.op_type = ""

    def verify_request(self, query, binding):
        """
        :param query: The SAML query, transport encoded
        :param binding: Which binding the query came in over
        """
        resp_args = {}
        if not query:
            logger.info("Missing QUERY")
            resp = Unauthorized('Unknown user')
            return resp_args, resp(self.environ, self.start_response)

        if not self.req_info:
            self.req_info = IDP.parse_authn_request(query, binding)

        logger.info("parsed OK")
        _authn_req = self.req_info.message
        logger.debug("%s", _authn_req)

        try:
            self.binding_out, self.destination = IDP.pick_binding(
                "assertion_consumer_service",
                bindings=self.response_bindings,
                entity_id=_authn_req.issuer.text, request=_authn_req)
        except Exception as err:
            logger.error("Couldn't find receiver endpoint: %s", err)
            raise

        logger.debug("Binding: %s, destination: %s", self.binding_out,
                                                       self.destination)

        resp_args = {}
        try:
            resp_args = IDP.response_args(_authn_req)
            _resp = None
        except UnknownPrincipal as excp:
            _resp = IDP.create_error_response(_authn_req.id,
                                              self.destination, excp)
        except UnsupportedBinding as excp:
            _resp = IDP.create_error_response(_authn_req.id,
                                              self.destination, excp)

        return resp_args, _resp

    def do(self, query, binding_in, relay_state="", encrypt_cert=None,
           **kwargs):
        """
        :param query: The request
        :param binding_in: Which binding was used when receiving the query
        :param relay_state: The relay state provided by the SP
        :param encrypt_cert: Cert to use for encryption
        :return: A response
        """
        try:
            resp_args, _resp = self.verify_request(query, binding_in)
        except UnknownPrincipal as excp:
            logger.error("UnknownPrincipal: %s", excp)
            resp = ServiceError("UnknownPrincipal: %s" % (excp,))
            return resp(self.environ, self.start_response)
        except UnsupportedBinding as excp:
            logger.error("UnsupportedBinding: %s", excp)
            resp = ServiceError("UnsupportedBinding: %s" % (excp,))
            return resp(self.environ, self.start_response)

        if not _resp:
            identity = USERS[self.user].copy()
            # identity["eduPersonTargetedID"] = get_eptid(IDP, query, session)
            logger.info("Identity: %s", identity)

            if REPOZE_ID_EQUIVALENT:
                identity[REPOZE_ID_EQUIVALENT] = self.user
            try:
                try:
                    metod = self.environ["idp.authn"]
                except KeyError:
                    pass
                else:
                    resp_args["authn"] = metod

                _resp = IDP.create_authn_response(
                    identity, userid=self.user,
                    encrypt_cert_assertion=encrypt_cert,
                    **resp_args)
            except Exception as excp:
                logging.error(exception_trace(excp))
                resp = ServiceError("Exception: %s" % (excp,))
                return resp(self.environ, self.start_response)

        logger.info("AuthNResponse: %s", _resp)
        if self.op_type == "ecp":
            kwargs = {"soap_headers": [
                ecp.Response(
                    assertion_consumer_service_url=self.destination)]}
        else:
            kwargs = {}

        http_args = IDP.apply_binding(self.binding_out,
                                      "%s" % _resp, self.destination,
                                      relay_state, response=True, **kwargs)

        logger.debug("HTTPargs: %s", http_args)
        return self.response(self.binding_out, http_args)

    @staticmethod
    def _store_request(saml_msg):
        logger.debug("_store_request: %s", saml_msg)
        key = sha1(saml_msg["SAMLRequest"]).hexdigest()
        # store the AuthnRequest
        IDP.ticket[key] = saml_msg
        return key

    def redirect(self):
        """ This is the HTTP-redirect endpoint """

        logger.info("--- In SSO Redirect ---")
        saml_msg = self.unpack_redirect()

        try:
            _key = saml_msg["key"]
            saml_msg = IDP.ticket[_key]
            self.req_info = saml_msg["req_info"]
            del IDP.ticket[_key]
        except KeyError:
            try:
                self.req_info = IDP.parse_authn_request(saml_msg["SAMLRequest"],
                                                        BINDING_HTTP_REDIRECT)
            except KeyError:
                resp = BadRequest("Message signature verification failure")
                return resp(self.environ, self.start_response)

            if not self.req_info:
                resp = BadRequest("Message parsing failed")
                return resp(self.environ, self.start_response)

            _req = self.req_info.message

            if "SigAlg" in saml_msg and "Signature" in saml_msg:
                # Signed request
                issuer = _req.issuer.text
                _certs = IDP.metadata.certs(issuer, "any", "signing")
                verified_ok = False
                for cert in _certs:
                    if verify_redirect_signature(saml_msg, IDP.sec.sec_backend,
                                                 cert):
                        verified_ok = True
                        break
                if not verified_ok:
                    resp = BadRequest("Message signature verification failure")
                    return resp(self.environ, self.start_response)

            if self.user:
                saml_msg["req_info"] = self.req_info
                if _req.force_authn is not None and \
                        _req.force_authn.lower() == 'true':
                    key = self._store_request(saml_msg)
                    return self.not_authn(key, _req.requested_authn_context)
                else:
                    return self.operation(saml_msg, BINDING_HTTP_REDIRECT)
            else:
                saml_msg["req_info"] = self.req_info
                key = self._store_request(saml_msg)
                return self.not_authn(key, _req.requested_authn_context)
        else:
            return self.operation(saml_msg, BINDING_HTTP_REDIRECT)

    def post(self):
        """
        The HTTP-Post endpoint
        """
        logger.info("--- In SSO POST ---")
        saml_msg = self.unpack_either()

        try:
            _key = saml_msg["key"]
            saml_msg = IDP.ticket[_key]
            self.req_info = saml_msg["req_info"]
            del IDP.ticket[_key]
        except KeyError:
            self.req_info = IDP.parse_authn_request(
                saml_msg["SAMLRequest"], BINDING_HTTP_POST)
            _req = self.req_info.message
            if self.user:
                if _req.force_authn is not None and \
                        _req.force_authn.lower() == 'true':
                    saml_msg["req_info"] = self.req_info
                    key = self._store_request(saml_msg)
                    return self.not_authn(key, _req.requested_authn_context)
                else:
                    return self.operation(saml_msg, BINDING_HTTP_POST)
            else:
                saml_msg["req_info"] = self.req_info
                key = self._store_request(saml_msg)
                return self.not_authn(key, _req.requested_authn_context)
        else:
            return self.operation(saml_msg, BINDING_HTTP_POST)

    # def artifact(self):
    # # Can be either by HTTP_Redirect or HTTP_POST
    #     _req = self._store_request(self.unpack_either())
    #     if isinstance(_req, basestring):
    #         return self.not_authn(_req)
    #     return self.artifact_operation(_req)

    def ecp(self):
        # The ECP interface
        logger.info("--- ECP SSO ---")
        resp = None

        try:
            authz_info = self.environ["HTTP_AUTHORIZATION"]
            if authz_info.startswith("Basic "):
                try:
                    _info = base64.b64decode(authz_info[6:])
                except TypeError:
                    resp = Unauthorized()
                else:
                    try:
                        (user, passwd) = _info.split(":")
                        if is_equal(PASSWD[user], passwd):
                            resp = Unauthorized()
                        self.user = user
                        self.environ[
                            "idp.authn"] = AUTHN_BROKER.get_authn_by_accr(
                            PASSWORD)
                    except ValueError:
                        resp = Unauthorized()
            else:
                resp = Unauthorized()
        except KeyError:
            resp = Unauthorized()

        if resp:
            return resp(self.environ, self.start_response)

        _dict = self.unpack_soap()
        self.response_bindings = [BINDING_PAOS]
        # Basic auth ?!
        self.op_type = "ecp"
        return self.operation(_dict, BINDING_SOAP)
