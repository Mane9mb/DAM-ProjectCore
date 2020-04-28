#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import datetime
import enum
import logging
import os
from builtins import getattr
from urllib.parse import urljoin

import falcon
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Unicode, \
    UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_i18n import make_translatable

import messages
from db.json_model import JSONModel
import settings

mylogger = logging.getLogger(__name__)

SQLAlchemyBase = declarative_base()
make_translatable(options={"locales": settings.get_accepted_languages()})


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


class PositionEnum(enum.Enum):
    left = "L"
    rigth = "R"


class LicenseEnum(enum.Enum):
    have = "Y"
    dont = "N"


class SmashEnum(enum, Enum):
    Saque = "S"
    Derecha = "R"
    Reves = "L"
    Globo = "G"
    Cortada = "C"
    Mate = "M"
    Volea = "V"


class UserToken(SQLAlchemyBase):
    __tablename__ = "users_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(Unicode(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="tokens")


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
    photo_path = Column(Unicode(255))
    license = Column(Enum(LicenseEnum))
    matchname = Column(Unicode(50))
    prefsmash = Column(Enum(SmashEnum))
    club = Column(Unicode(50))
    timeplay = Column(Unicode(50))

    @hybrid_property
    def public_profile(self):
        return {
            "created_at": self.created_at.strftime(settings.DATETIME_DEFAULT_FORMAT),
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "genere": self.genere.value,
            "photo": self.photo_path,
            "rol": self.rol,
            "position": self.position,
            "matchname": self.matchname,
            "timeplay": self.timeplay,
            "prefsmash": self.prefsmash,
            "club": self.club
        }

    @hybrid_property
    def poster_path(self):
        return _generate_media_path(self, "poster")

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
            "position": self.position.value,
            "phone": self.phone,
            "photo": self.photo_path,
            "matchname": self.matchname,
            "timeplay": self.timeplay,
            "prefsmash": self.prefsmash,
            "club": self.club,
            "license": self.license

        }
