
from supervisr.mod.saml_idp.service import Service

class ARS(Service):
    def do(self, request, binding, relay_state="", encrypt_cert=None):
        _req = IDP.parse_artifact_resolve(request, binding)

        msg = IDP.create_artifact_response(_req, _req.artifact.text)

        hinfo = IDP.apply_binding(BINDING_SOAP, "%s" % msg, "", "",
                                  response=True)

        resp = Response(hinfo["data"], headers=hinfo["headers"])
        return resp(self.environ, self.start_response)

