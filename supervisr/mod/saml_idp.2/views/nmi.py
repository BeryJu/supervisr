
from supervisr.mod.saml_idp.service import Service

class NMI(Service):
    def do(self, query, binding, relay_state="", encrypt_cert=None):
        logger.info("--- Manage Name ID Service ---")
        req = IDP.parse_manage_name_id_request(query, binding)
        request = req.message

        # Do the necessary stuff
        name_id = IDP.ident.handle_manage_name_id_request(
            request.name_id, request.new_id, request.new_encrypted_id,
            request.terminate)

        logger.debug("New NameID: %s", name_id)

        _resp = IDP.create_manage_name_id_response(request)

        # It's using SOAP binding
        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % _resp, "",
                                  relay_state, response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)

