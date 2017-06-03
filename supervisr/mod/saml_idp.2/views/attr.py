
from supervisr.mod.saml_idp.service import Service

class ATTR(Service):
    def do(self, request, binding, relay_state="", encrypt_cert=None):
        logger.info("--- Attribute Query Service ---")

        _req = IDP.parse_attribute_query(request, binding)
        _query = _req.message

        name_id = _query.subject.name_id
        uid = name_id.text
        logger.debug("Local uid: %s", uid)
        identity = EXTRA[uid]

        # Comes in over SOAP so only need to construct the response
        args = IDP.response_args(_query, [BINDING_SOAP])
        msg = IDP.create_attribute_response(identity,
                                            name_id=name_id, **args)

        logger.debug("response: %s", msg)
        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % msg, "", "",
                                  response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)

