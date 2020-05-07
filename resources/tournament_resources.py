#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import falcon
from falcon.media.validators import jsonschema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import messages
from db.models import Tournament, TournamentTypeEnum, TournamentPrivacyTypeEnum, TournamentGenereEnum, Category, \
    TournamentCategoriesAssociation, AgeCategoriesTypeEnum
from hooks import requires_auth
from resources.base_resources import DAMCoreResource

from resources.schemas import SchemaRegisterUser

mylogger = logging.getLogger(__name__)


class ResourceGetTournament(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetTournament, self).on_get(req, resp, *args, **kwargs)

        if "id" in kwargs:
            try:
                aux_tourn = self.db_session.query(Tournament).filter(Tournament.id == kwargs["id"]).one()

                resp.media = aux_tourn.json_model
                resp.status = falcon.HTTP_200
            except NoResultFound:
                raise falcon.HTTPBadRequest(description=messages.torunament_not_found)


@falcon.before(requires_auth)
class ResourceGetTournaments(DAMCoreResource):
    def on_get(self, req, resp, *args, **kwargs):
        super(ResourceGetTournaments, self).on_get(req, resp, *args, **kwargs)

        # Mirem si ens passen un argument opcional que sigui el Type
        request_tournament_type = req.get_param("type", False)
        if request_tournament_type is not None:
            request_tournament_type = request_tournament_type.upper()
            if (len(request_tournament_type) != 1) or (
                    request_tournament_type not in [i.value for i in TournamentTypeEnum.__members__.values()]):
                raise falcon.HTTPInvalidParam(messages.type_invalid, "type")

        # Mirem si ens passen un argument opcional que sigui el Tipus de inscripcio(Privat o public)
        request_inscription_type = req.get_param("inscription_type", False)
        if request_inscription_type is not None:
            request_inscription_type = request_inscription_type.upper()
            if (len(request_inscription_type) != 1) or (
                    request_inscription_type not in [i.value for i in TournamentPrivacyTypeEnum.__members__.values()]):
                raise falcon.HTTPInvalidParam(messages.inscription_type_invalid, "inscription_type")

        # Mirem si ens passen un genere
        request_tournament_genere = req.get_param("genere", False)
        if request_tournament_genere is not None:
            request_tournament_genere = request_tournament_genere.upper()
            if (len(request_tournament_genere) != 1) or (
                    request_tournament_genere not in [i.value for i in TournamentGenereEnum.__members__.values()]):
                raise falcon.HTTPInvalidParam(messages.genere_invalid, "genere")

        # Mirem si ens passen un age
        request_tournament_age = req.get_param("age", False)
        if request_tournament_age is not None:
            request_tournament_age = request_tournament_age.upper()
            if (len(request_tournament_age) != 1) or (
                    request_tournament_age not in [i.value for i in AgeCategoriesTypeEnum.__members__.values()]):
                raise falcon.HTTPInvalidParam(messages.age_invalid, "age")

        response_tournaments = list()
        aux_tournaments = self.db_session.query(Tournament)

        if request_tournament_type is not None:
            aux_tournaments = aux_tournaments.filter(
                Tournament.type == TournamentTypeEnum(request_tournament_type))

        if request_inscription_type is not None:
            aux_tournaments = aux_tournaments.filter(
                Tournament.inscription_type == TournamentPrivacyTypeEnum(request_inscription_type))

        if request_tournament_genere is not None:
            aux_tournaments = aux_tournaments.join(TournamentCategoriesAssociation,Category).filter(
                Category.genere == TournamentGenereEnum(request_tournament_genere))

        if request_tournament_age is not None:
            aux_tournaments = aux_tournaments.join(TournamentCategoriesAssociation,Category).filter(
                Category.age == AgeCategoriesTypeEnum(request_tournament_age))

        if aux_tournaments is not None:
            for current_torunament in aux_tournaments.all():
                response_tournaments.append(current_torunament.json_model)

        resp.media = response_tournaments
        resp.status = falcon.HTTP_200




##QUan pasem mes dun filtre al hora
##