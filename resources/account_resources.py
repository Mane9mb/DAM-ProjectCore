#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import logging
import datetime
import falcon
import os

from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from resources import utils
import settings
import messages
from db.models import User, UserToken, GenereEnum, RolEnum, PositionEnum, SmashEnum
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaUserToken, SchemaUpdateUser
from settings import STATIC_DIRECTORY

mylogger = logging.getLogger(__name__)


@falcon.before(requires_auth)
class ResourceAccountUpdateProfileImage(DAMCoreResource):
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceAccountUpdateProfileImage, self).on_post(req, resp, *args, **kwargs)


        # Get the user from the token
        current_user = req.context["auth_user"]
        resource_path = current_user.photo_path
        print("TAG"+current_user.photo_path)
        print(resource_path)
        # Get the file from form
        incoming_file = req.get_param("image_file")

        # Run the common part for storing
        filename = utils.save_static_media_file(incoming_file, resource_path)

        # Update db model
        current_user.photo = filename
        self.db_session.add(current_user)
        self.db_session.commit()

        resp.status = falcon.HTTP_200

class ResourceCreateUserToken(DAMCoreResource):
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceCreateUserToken, self).on_post(req, resp, *args, **kwargs)

        basic_auth_raw = req.get_header("Authorization")
        if basic_auth_raw is not None:
            basic_auth = basic_auth_raw.split()[1]
            auth_username, auth_password = (base64.b64decode(basic_auth).decode("utf-8").split(":"))
            if (auth_username is None) or (auth_password is None) or (auth_username == "") or (auth_password == ""):
                raise falcon.HTTPUnauthorized(description=messages.username_and_password_required)
        else:
            raise falcon.HTTPUnauthorized(description=messages.authorization_header_required)

        current_user = self.db_session.query(User).filter(User.email == auth_username).one_or_none()
        if current_user is None:
            current_user = self.db_session.query(User).filter(User.username == auth_username).one_or_none()

        if (current_user is not None) and (current_user.check_password(auth_password)):
            current_token = current_user.create_token()
            try:
                self.db_session.commit()
                resp.media = {"token": current_token.token}
                resp.status = falcon.HTTP_200
            except Exception as e:
                mylogger.critical("{}:{}".format(messages.error_saving_user_token, e))
                self.db_session.rollback()
                raise falcon.HTTPInternalServerError()
        else:
            raise falcon.HTTPUnauthorized(description=messages.user_not_found)


@falcon.before(requires_auth)
class ResourceDeleteUserToken(DAMCoreResource):
    @jsonschema.validate(SchemaUserToken)
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceDeleteUserToken, self).on_post(req, resp, *args, **kwargs)

        current_user = req.context["auth_user"]
        selected_token_string = self.json_request["token"]
        selected_token = self.db_session.query(UserToken).filter(UserToken.token == selected_token_string).one_or_none()

        if selected_token is not None:
            if selected_token.user.id == current_user.id:
                try:
                    self.db_session.delete(selected_token)
                    self.db_session.commit()

                    resp.status = falcon.HTTP_200
                except Exception as e:
                    mylogger.critical("{}:{}".format(messages.error_removing_user_token, e))
                    raise falcon.HTTPInternalServerError()
            else:
                raise falcon.HTTPUnauthorized(description=messages.token_doesnt_belongs_current_user)
        else:
            raise falcon.HTTPUnauthorized(description=messages.token_not_found)


@falcon.before(requires_auth)
class ResourceAccountUserProfile(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceAccountUserProfile, self).on_get(req, resp, *args, **kwargs)

        current_user = req.context["auth_user"]

        resp.media = current_user.json_model
        resp.status = falcon.HTTP_200

@falcon.before(requires_auth)
class ResourceAccountUpdateUserProfile(DAMCoreResource):
    @jsonschema.validate(SchemaUpdateUser)
    def on_put(self, req, resp, *args, **kwargs):
        super(ResourceAccountUpdateUserProfile, self).on_put(req, resp, *args, **kwargs)

        current_user = req.context["auth_user"]

        for key in req.media:
            value = req.media[key]
            if key == "genere":
                try:
                    value = GenereEnum(value.upper())
                except ValueError:
                    raise falcon.HTTPBadRequest(description=messages.genere_invalid)
            if key == "rol":
                try:
                    value = RolEnum(value.upper())
                except ValueError:
                    raise falcon.HTTPBadRequest(description=messages.rol_invalid)
            if key == "position":
                try:
                    value = PositionEnum(value.upper())
                except ValueError:
                    raise falcon.HTTPBadRequest(description=messages.position_invalid)

            if key == "prefsmash":
                try:
                     value = SmashEnum(value.upper())
                except ValueError:
                     raise falcon.HTTPBadRequest(description=messages.smash_invalid)

            try:
                getattr(current_user,key)
                if (key != "username"):
                    setattr(current_user, key, value)
            except AttributeError:
                raise falcon.HTTPBadRequest(description=messages.parameters_invalid)


        self.db_session.commit()
        resp.status = falcon.HTTP_200