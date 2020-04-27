#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging.config

import falcon

import messages
import middlewares
from resources import account_resources, common_resources, user_resources
from settings import configure_logging
from falcon_multipart.middleware import MultipartMiddleware


# LOGGING
mylogger = logging.getLogger(__name__)
configure_logging()


# DEFAULT 404
# noinspection PyUnusedLocal
def handle_404(req, resp):
    resp.media = messages.resource_not_found
    resp.status = falcon.HTTP_404


# FALCON
app = application = falcon.API(
    middleware=[
        middlewares.DBSessionManager(),
        middlewares.Falconi18n(),
        MultipartMiddleware()
    ]
)
application.add_route("/", common_resources.ResourceHome())

application.add_route("/account/profile", account_resources.ResourceAccountUserProfile())
application.add_route("/account/create_token", account_resources.ResourceCreateUserToken())
application.add_route("/account/delete_token", account_resources.ResourceDeleteUserToken())
#editar perfil
application.add_route("/account/update_profile", account_resources.ResourceAccountUpdateUserProfile())
#Canviar la foto del perfil
application.add_route("/account/profile/update_profile_image", account_resources.ResourceAccountUpdateProfileImage())
application.add_route("/users/register", user_resources.ResourceRegisterUser())
#Entrar en un perfil publico
application.add_route("/users/show/{username}", user_resources.ResourceGetUserProfile())

# Aquesta no te sentit
# application.add_route("/users/show/{prefsmash}", user_resources.ResourceGetUserProfile())

#buscar usuarios  poner filtros
application.add_route("/users", user_resources.ResourceGetUsers())
application.add_sink(handle_404, "")
