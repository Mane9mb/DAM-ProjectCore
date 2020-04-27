#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import User, GenereEnum, RolEnum, PositionEnum
from hooks import requires_auth
from resources.base_resources import DAMCoreResource
from resources.schemas import SchemaRegisterUser

mylogger = logging.getLogger(__name__)


@falcon.before(requires_auth)
class ResourceGetUserProfile(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUserProfile, self).on_get(req, resp, *args, **kwargs)
        users_rol = req.get_param("rol")
        if users_rol == "P":
            if "username" in kwargs:
                try:
                    aux_user = self.db_session.query(User).filter(User.username == kwargs["username"]).one()

                    resp.media = aux_user.public_profile
                    resp.status = falcon.HTTP_200
                except NoResultFound:
                    raise falcon.HTTPBadRequest(description=messages.user_not_found)
            if "prefsmash" == "derechazo":
                try:
                    aux_user = self.db_session.query(User).filter(User.username == kwargs["username"]).one()

                    resp.media = aux_user.public_profile
                    resp.status = falcon.HTTP_200
                except NoResultFound:
                    raise falcon.HTTPBadRequest(description=messages.prefsmash_not_found)





@falcon.before(requires_auth)
class ResourceGetUsers(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetUsers, self).on_get(req, resp, *args, **kwargs)

        # Mirem si ens passen un argument opcional que sigui el rol
        request_users_rol = req.get_param("rol", False)
        if request_users_rol is not None:
            request_users_rol = request_users_rol.upper()
            if (len(request_users_rol) != 1) or (
                    request_users_rol not in [i.value for i in RolEnum.__members__.values()]):
                raise falcon.HTTPInvalidParam(messages.rol_invalid, "rol")
            
        # Mirem si ens passen un argument opcional que sigui la posicio
        request_users_position = req.get_param("position", False)
        if request_users_position is not None:
            request_users_position = request_users_position.upper()
            if (len(request_users_position) != 1) or (
                    request_users_position not in [i.value for i in PositionEnum.__members__.values()]):
                raise falcon.HTTPInvalidParam(messages.position_invalid, "position")

        # Mirem si ens passen un argument opcional que sigui el club
        request_users_club = req.get_param("club", False)

        response_users = list()
        aux_users = self.db_session.query(User)

        if request_users_rol is not None:
            aux_users = aux_users.filter(
                    User.rol == RolEnum(request_users_rol))

        if request_users_position is not None:
            aux_users = aux_users.filter(
                    User.position == PositionEnum(request_users_position))

        if request_users_club is not None:
            aux_users = aux_users.filter(
                    User.club == request_users_club)

        if aux_users is not None:
            for current_user in aux_users.all():
                response_users.append(current_user.json_model)
        resp.media = response_users
        resp.status = falcon.HTTP_200


class ResourceRegisterUser(DAMCoreResource):
    @jsonschema.validate(SchemaRegisterUser)
    def on_post(self, req, resp, *args, **kwargs):
        super(ResourceRegisterUser, self).on_post(req, resp, *args, **kwargs)

        aux_user = User()

        try:
            try:
                aux_genere = GenereEnum(req.media["genere"].upper())
            except ValueError:
                raise falcon.HTTPBadRequest(description=messages.genere_invalid)
            try:
                aux_rol = RolEnum(req.media["rol"].upper())

            except ValueError:
                raise falcon.HTTPBadRequest(description=messages.rol_invalid)


            aux_user.username = req.media["username"]
            aux_user.password = req.media["password"]
            aux_user.email = req.media["email"]
            aux_user.genere = aux_genere
            aux_user.rol = aux_rol

            self.db_session.add(aux_user)

            try:
                self.db_session.commit()
            except IntegrityError:
                raise falcon.HTTPBadRequest(description=messages.user_exists)

        except KeyError:
            raise falcon.HTTPBadRequest(description=messages.parameters_invalid)

        resp.status = falcon.HTTP_200
