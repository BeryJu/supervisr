
from supervisr.mod.saml_idp.service import Service

class AQS(Service):
    def do(self, request, binding, relay_state="", encrypt_cert=None):
        logger.info("--- Authn Query Service ---")
        _req = IDP.parse_authn_query(request, binding)
        _query = _req.message

        msg = IDP.create_authn_query_response(_query.subject,
                                              _query.requested_authn_context,
                                              _query.session_index)

        logger.debug("response: %s", msg)
        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % msg, "", "",
                                  response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)
