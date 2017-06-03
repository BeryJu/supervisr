
from supervisr.mod.saml_idp.service import Service

class NIM(Service):
    def do(self, query, binding, relay_state="", encrypt_cert=None):
        req = IDP.parse_name_id_mapping_request(query, binding)
        request = req.message
        # Do the necessary stuff
        try:
            name_id = IDP.ident.handle_name_id_mapping_request(
                request.name_id, request.name_id_policy)
        except Unknown:
            resp = BadRequest("Unknown entity")
            return resp(self.environ, self.start_response)
        except PolicyError:
            resp = BadRequest("Unknown entity")
            return resp(self.environ, self.start_response)

        info = IDP.response_args(request)
        _resp = IDP.create_name_id_mapping_response(name_id, **info)

        # Only SOAP
        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % _resp, "", "",
                                  response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)
