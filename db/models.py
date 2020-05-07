#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import datetime
import enum
import logging
import os
from _operator import and_
from builtins import getattr
from urllib.parse import urljoin

import falcon
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Unicode, \
    UnicodeText, Float, Table, case, type_coerce
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_i18n import make_translatable
from falcon_multipart.middleware import MultipartMiddleware
import messages
from db.json_model import JSONModel
import settings

mylogger = logging.getLogger(__name__)

SQLAlchemyBase = declarative_base()
make_translatable(options={"locales": settings.get_accepted_languages()})


def _generate_media_url(class_instance, class_attibute_name, default_image=False):
    class_base_url = urljoin(urljoin(urljoin("http://{}".format(settings.STATIC_HOSTNAME), settings.STATIC_URL),
                                     settings.MEDIA_PREFIX),
                             class_instance.__tablename__ + "/")
    class_attribute = getattr(class_instance, class_attibute_name)
    if class_attribute is not None:
        return urljoin(urljoin(urljoin(urljoin(class_base_url, class_attribute), str(class_instance.id) + "/"),
                               class_attibute_name + "/"), class_attribute)
    else:
        if default_image:
            return urljoin(urljoin(class_base_url, class_attibute_name + "/"), settings.DEFAULT_IMAGE_NAME)
        else:
            return class_attribute


def _generate_media_path(class_instance, class_attibute_name):
    class_path = "/{0}{1}{2}/{3}/{4}/".format(settings.STATIC_URL, settings.MEDIA_PREFIX, class_instance.__tablename__,
                                              str(class_instance.id), class_attibute_name)
    return class_path

class RolEnum(enum.Enum):
    owner = "O"
    player = "P"


class GenereEnum(enum.Enum):
    male = "M"
    female = "F"

class TournamentGenereEnum(enum.Enum):
    male = "H"
    female = "F"
    mixt = "X"

class PositionEnum(enum.Enum):
    left = "L"
    rigth = "R"


class LicenseEnum(enum.Enum):
    have = "Y"
    dont = "N"


class SmashEnum(enum.Enum):
    saque = "S"
    derecha = "R"
    reves = "L"
    globo = "G"
    cortada = "C"
    mate = "M"
    volea = "V"

class TournamentTypeEnum(enum.Enum):
    americana = "A"
    league = "L"
    draft = "D"

class TournamentPrivacyTypeEnum(enum.Enum):
    public = "O"
    privat = "C"


class AgeCategoriesTypeEnum(enum.Enum):
    menors = "M"
    seniors = "S"

class TournamentStatusEnum(enum.Enum):
    open = "O"
    closed = "C"
    playing = "G"




TournamentInscriptionsAssociation = Table("tournament_inscriptions_association",
SQLAlchemyBase.metadata,
Column("tournament_id", Integer,ForeignKey("tournaments.id",
        onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
Column("users_id", Integer,
       ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
       nullable=False)
)

TournamentCategoriesAssociation = Table("tournament_categories_association",
SQLAlchemyBase.metadata,
Column("tournament_id", Integer, ForeignKey("tournaments.id",
        onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
Column("category_id", Integer,
       ForeignKey("categories.id", onupdate="CASCADE", ondelete="CASCADE"),
       nullable=False)
)


class UserToken(SQLAlchemyBase):
    __tablename__ = "users_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(Unicode(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="tokens")

class Category(SQLAlchemyBase, JSONModel):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    genere = Column(Enum(TournamentGenereEnum), nullable=False)
    age = Column(Enum(AgeCategoriesTypeEnum), nullable=False)
    level = Column(Integer)

    tournament_categories = relationship("Tournament",
                                         secondary=TournamentCategoriesAssociation,
                                         back_populates="categories")



class Facility(SQLAlchemyBase, JSONModel):
    __tablename__ = "facilities"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(Unicode(255))
    postal_code = Column(Unicode(12))
    town = Column(Unicode(12))
    provincia = Column(Unicode(12))
    phone = Column(Unicode(50))
    email = Column(Unicode(255))
    web = Column(Unicode(255))

    tournaments = relationship("Tournament", back_populates="facility")


class Tournament(SQLAlchemyBase, JSONModel):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    edited_at = Column(DateTime, default=None)
    name = Column(Unicode(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    finish_date = Column(DateTime, nullable=False)
    start_register_date = Column(DateTime, nullable=False)
    finish_register_date = Column(DateTime, nullable=False)
    limit_couples = Column(Integer)
    inscription_type = Column(Enum(TournamentPrivacyTypeEnum)) # Public o privat (requeix codi d'invitació)
    type = Column(Enum(TournamentTypeEnum), nullable=False)
    price_1 = Column(Float, nullable=False)
    price_2 = Column(Float, nullable=False)

    description = Column(UnicodeText)
    poster = Column(Unicode(255))

    # Relació (User-Tournament) per tenir l'organitzador.
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tournament_owner")

    # Relació inscripcions
    inscriptions = relationship ("User", secondary=TournamentInscriptionsAssociation, back_populates="tournament_inscriptions")

    # Relació (Facility-Tournament) per tenir el club
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    facility = relationship("Facility", back_populates="tournaments")

    # Categories
    categories = relationship("Category",
                               secondary=TournamentCategoriesAssociation,
                               back_populates="tournament_categories")

    @hybrid_property
    def status(self):
        current_datetime = datetime.datetime.now()
        if current_datetime < self.finish_register_date:
            return TournamentStatusEnum.open
        elif (current_datetime > self.finish_register_date) and (current_datetime < self.finish_date):
            return TournamentStatusEnum.playing
        else:
            return TournamentStatusEnum.closed

    @status.expression
    def status(cls):
        current_datetime = datetime.datetime.now()
        return case(
            [
                (current_datetime < cls.finish_register_date,
                 type_coerce(TournamentStatusEnum.open, Enum(TournamentStatusEnum))),
                (and_(current_datetime > cls.finish_register_date, current_datetime < cls.finish_date),
                 type_coerce(TournamentStatusEnum.in_game, Enum(TournamentStatusEnum)))
            ],
            else_=type_coerce(TournamentStatusEnum.closed, Enum(TournamentStatusEnum))
        )


    @hybrid_property
    def json_model(self):
        return {
                "created_at": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
                "name": self.name,
                "inscription_type" : self.inscription_type.value,
                "start_date": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
                "status": self.status.value,
                "type": self.type.value,
                "facility": self.facility.to_json_model(id="id", name="name", province="province", town="town",
                                                    latitude="latitude", longitude="longitude"),
                "categories": [category.json_model for category in self.categories],
         }

    @hybrid_property
    def poster_url(self):
        return _generate_media_url(self, "poster", default_image=True)





class User(SQLAlchemyBase, JSONModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    username = Column(Unicode(50), nullable=False, unique=True)
    password = Column(UnicodeText, nullable=False)
    email = Column(Unicode(255), nullable=False)
    tokens = relationship("UserToken", back_populates="user", cascade="all, delete-orphan")
    name = Column(Unicode(50))
    surname = Column(Unicode(50))
    birthdate = Column(Date)
    genere = Column(Enum(GenereEnum), nullable=False)
    rol = Column(Enum(RolEnum), nullable=False)
    position = Column(Enum(PositionEnum))
    phone = Column(Unicode(50))
    photo = Column(Unicode(255))
    license = Column(Enum(LicenseEnum))
    matchname = Column(Unicode(50))
    prefsmash = Column(Enum(SmashEnum))
    club = Column(Unicode(50))
    timeplay= Column(Unicode(50))

    tournament_owner = relationship("Tournament", back_populates="owner")
    tournament_inscriptions = relationship("Tournament", back_populates="inscriptions")

    @hybrid_property
    def public_profile(self):
        return {
            "created_at": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "genere": self.genere.value,
            "photo": self.photo,
            "rol": self.rol.value,
            "position": self.position.value,
            "matchname": self.matchname,
            "timeplay": self.timeplay,
            "prefsmash": self.prefsmash.value,
            "club": self.club
        }

    @hybrid_property
    def photo_url(self):
        return _generate_media_url(self, "photo", default_image=True)

    @hybrid_property
    def photo_path(self):
        return _generate_media_path(self, "photo")


    @hybrid_method
    def set_password(self, password_string):
        self.password = pbkdf2_sha256.hash(password_string)

    @hybrid_method
    def check_password(self, password_string):
        return pbkdf2_sha256.verify(password_string, self.password)

    @hybrid_method
    def create_token(self):
        if len(self.tokens) < settings.MAX_USER_TOKENS:
            token_string = binascii.hexlify(os.urandom(25)).decode("utf-8")
            aux_token = UserToken(token=token_string, user=self)
            return aux_token
        else:
            raise falcon.HTTPBadRequest(title=messages.quota_exceded, description=messages.maximum_tokens_exceded)

    @hybrid_property
    def json_model(self):
        return {
            "created_at": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "surname": self.surname,
            "birthdate": self.birthdate.strftime(
                settings.DATE_DEFAULT_FORMAT) if self.birthdate is not None else self.birthdate,
            "genere": self.genere.value,
            "rol": self.rol.value,
            "position":self.position.value,
            "phone": self.phone,
            "photo": self.photo_url,
            "matchname": self.matchname,
            "timeplay": self.timeplay,
            "prefsmash": self.prefsmash.value,
            "club": self.club,
            "license": self.license


        }
