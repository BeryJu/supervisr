class Service(object):
    def __init__(self, environ, start_response, user=None):
        self.environ = environ
        logger.debug("ENVIRON: %s", environ)
        self.start_response = start_response
        self.user = user

    def unpack_redirect(self):
        if "QUERY_STRING" in self.environ:
            _qs = self.environ["QUERY_STRING"]
            return dict([(k, v[0]) for k, v in parse_qs(_qs).items()])
        else:
            return None

    def unpack_post(self):
        _dict = parse_qs(get_post(self.environ))
        logger.debug("unpack_post:: %s", _dict)
        try:
            return dict([(k, v[0]) for k, v in _dict.items()])
        except Exception:
            return None

    def unpack_soap(self):
        try:
            query = get_post(self.environ)
            return {"SAMLRequest": query, "RelayState": ""}
        except Exception:
            return None

    def unpack_either(self):
        if self.environ["REQUEST_METHOD"] == "GET":
            _dict = self.unpack_redirect()
        elif self.environ["REQUEST_METHOD"] == "POST":
            _dict = self.unpack_post()
        else:
            _dict = None
        logger.debug("_dict: %s", _dict)
        return _dict

    def operation(self, saml_msg, binding):
        logger.debug("_operation: %s", saml_msg)
        if not (saml_msg and 'SAMLRequest' in saml_msg):
            resp = BadRequest('Error parsing request or no request')
            return resp(self.environ, self.start_response)
        else:
            # saml_msg may also contain Signature and SigAlg
            if "Signature" in saml_msg:
                try:
                    kwargs = {"signature": saml_msg["Signature"],
                              "sigalg": saml_msg["SigAlg"]}
                except KeyError:
                    resp = BadRequest(
                        'Signature Algorithm specification is missing')
                    return resp(self.environ, self.start_response)
            else:
                kwargs = {}

            try:
                kwargs['encrypt_cert'] = encrypt_cert_from_item(
                    saml_msg["req_info"].message)
            except KeyError:
                pass

            try:
                kwargs['relay_state'] = saml_msg['RelayState']
            except KeyError:
                pass

            return self.do(saml_msg["SAMLRequest"], binding, **kwargs)

    def artifact_operation(self, saml_msg):
        if not saml_msg:
            resp = BadRequest("Missing query")
            return resp(self.environ, self.start_response)
        else:
            # exchange artifact for request
            request = IDP.artifact2message(saml_msg["SAMLart"], "spsso")
            try:
                return self.do(request, BINDING_HTTP_ARTIFACT,
                               saml_msg["RelayState"])
            except KeyError:
                return self.do(request, BINDING_HTTP_ARTIFACT)

    def response(self, binding, http_args):
        resp = None
        if binding == BINDING_HTTP_ARTIFACT:
            resp = Redirect()
        elif http_args["data"]:
            resp = Response(http_args["data"], headers=http_args["headers"])
        else:
            for header in http_args["headers"]:
                if header[0] == "Location":
                    resp = Redirect(header[1])

        if not resp:
            resp = ServiceError("Don't know how to return response")

        return resp(self.environ, self.start_response)

    def do(self, query, binding, relay_state="", encrypt_cert=None):
        pass

    def redirect(self):
        """ Expects a HTTP-redirect request """

        _dict = self.unpack_redirect()
        return self.operation(_dict, BINDING_HTTP_REDIRECT)

    def post(self):
        """ Expects a HTTP-POST request """

        _dict = self.unpack_post()
        return self.operation(_dict, BINDING_HTTP_POST)

    def artifact(self):
        # Can be either by HTTP_Redirect or HTTP_POST
        _dict = self.unpack_either()
        return self.artifact_operation(_dict)

    def soap(self):
        """
        Single log out using HTTP_SOAP binding
        """
        logger.debug("- SOAP -")
        _dict = self.unpack_soap()
        logger.debug("_dict: %s", _dict)
        return self.operation(_dict, BINDING_SOAP)

    def uri(self):
        _dict = self.unpack_either()
        return self.operation(_dict, BINDING_SOAP)

    def not_authn(self, key, requested_authn_context):
        ruri = geturl(self.environ, query=False)

        kwargs = dict(authn_context=requested_authn_context, key=key, redirect_uri=ruri)
        # Clear cookie, if it already exists
        kaka = delete_cookie(self.environ, "idpauthn")
        if kaka:
            kwargs["headers"] = [kaka]
        return do_authentication(self.environ, self.start_response, **kwargs)
