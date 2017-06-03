
from supervisr.mod.saml_idp.service import Service

class AIDR(Service):
    def do(self, aid, binding, relay_state="", encrypt_cert=None):
        logger.info("--- Assertion ID Service ---")

        try:
            assertion = IDP.create_assertion_id_request_response(aid)
        except Unknown:
            resp = NotFound(aid)
            return resp(self.environ, self.start_response)

        hinfo = IDP.apply_binding(BINDING_URI, "%s" % assertion, response=True)

        logger.debug("HINFO: %s", hinfo)
        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)

    def operation(self, _dict, binding, **kwargs):
        logger.debug("_operation: %s", _dict)
        if not _dict or "ID" not in _dict:
            resp = BadRequest('Error parsing request or no request')
            return resp(self.environ, self.start_response)

        return self.do(_dict["ID"], binding, **kwargs)

