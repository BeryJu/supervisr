
from supervisr.mod.saml_idp.service import Service

class SLO(Service):
    def do(self, request, binding, relay_state="", encrypt_cert=None, **kwargs):

        logger.info("--- Single Log Out Service ---")
        try:
            logger.debug("req: '%s'", request)
            req_info = IDP.parse_logout_request(request, binding)
        except Exception as exc:
            logger.error("Bad request: %s", exc)
            resp = BadRequest("%s" % exc)
            return resp(self.environ, self.start_response)

        msg = req_info.message
        if msg.name_id:
            lid = IDP.ident.find_local_id(msg.name_id)
            logger.info("local identifier: %s", lid)
            if lid in IDP.cache.user2uid:
                uid = IDP.cache.user2uid[lid]
                if uid in IDP.cache.uid2user:
                    del IDP.cache.uid2user[uid]
                del IDP.cache.user2uid[lid]
            # remove the authentication
            try:
                IDP.session_db.remove_authn_statements(msg.name_id)
            except KeyError as exc:
                logger.error("Unknown session: %s", exc)
                resp = ServiceError("Unknown session: %s", exc)
                return resp(self.environ, self.start_response)

        resp = IDP.create_logout_response(msg, [binding])

        if binding == BINDING_SOAP:
            destination = ""
            response = False
        else:
            binding, destination = IDP.pick_binding("single_logout_service",
                                                    [binding], "spsso",
                                                    req_info)
            response = True

        try:
            hinfo = IDP.apply_binding(binding, "%s" % resp, destination,
                                      relay_state, response=response)
        except Exception as exc:
            logger.error("ServiceError: %s", exc)
            resp = ServiceError("%s" % exc)
            return resp(self.environ, self.start_response)

        #_tlh = dict2list_of_tuples(hinfo["headers"])
        delco = delete_cookie(self.environ, "idpauthn")
        if delco:
            hinfo["headers"].append(delco)
        logger.info("Header: %s", (hinfo["headers"],))

        if binding == BINDING_HTTP_REDIRECT:
            for key, value in hinfo['headers']:
                if key.lower() == 'location':
                    resp = Redirect(value, headers=hinfo["headers"])
                    return resp(self.environ, self.start_response)

            resp = ServiceError('missing Location header')
            return resp(self.environ, self.start_response)
        else:
            resp = Response(hinfo["data"], headers=hinfo["headers"])
            return resp(self.environ, self.start_response)
