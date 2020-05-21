#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
import os
import random

from sqlalchemy.sql import text

import db
import settings
from db.models import SQLAlchemyBase, User, GenereEnum, UserToken, RolEnum, PositionEnum, SmashEnum, TournamentTypeEnum, \
    TournamentPrivacyTypeEnum, Facility, TournamentGenereEnum, AgeCategoriesTypeEnum, Category, Tournament, Couple, \
    Round, Match
from settings import DEFAULT_LANGUAGE

# LOGGING
mylogger = logging.getLogger(__name__)
settings.configure_logging()


def execute_sql_file(sql_file):
    sql_folder_path = os.path.join(os.path.dirname(__file__), "sql")
    sql_file_path = open(os.path.join(sql_folder_path, sql_file), encoding="utf-8")
    sql_command = text(sql_file_path.read())
    db_session.execute(sql_command)
    db_session.commit()
    sql_file_path.close()


if __name__ == "__main__":
    settings.configure_logging()

    db_session = db.create_db_session()

    # -------------------- REMOVE AND CREATE TABLES --------------------
    mylogger.info("Removing database...")
    SQLAlchemyBase.metadata.drop_all(db.DB_ENGINE)
    mylogger.info("Creating database...")
    SQLAlchemyBase.metadata.create_all(db.DB_ENGINE)



    # -------------------- CREATE USERS --------------------
    mylogger.info("Creating default users...")
    # noinspection PyArgumentList
    clubs = ["Club Tennis Manresa", "Club Padel Igualada", "Pistes Municipals Igualada", "Club Padel Odena",
             "Club Padel Pro"]
    words = ["pro", "demon", "tiger", "king", "cobra", "awesome", "moon", "sun", "vibora", "padel", "shoot", "power"]
    for p in range(1, 33):
        player = User(
            username="player" + str(p),
            email="player" + str(p) + "@gmail.com",
            name="player",
            surname=str(p),
            phone="660626960",
            rol=RolEnum.player,
            position=random.choice(list(PositionEnum)),
            genere=random.choice(list(GenereEnum)),
            matchname=random.choice(words) + random.choice(words),
            prefsmash=random.choice(list(SmashEnum)),
            club=random.choice(clubs)
            )
        player.set_password("000000")
        db_session.add(player)
    db_session.commit()
    user_admin = User(
        created_at=datetime.datetime(2020, 1, 1, 0, 1, 1),
        username="admin",
        email="admin@damcore.com",
        name="Administrator",
        surname="DamCore",
        phone="63812910",
        rol=RolEnum.player,
        genere=GenereEnum.male,
        position=PositionEnum.left,
        matchname="Jordi",
        prefsmash= SmashEnum.derecha,
        club="Club Tennis Manresa"
    )
    user_admin.set_password("DAMCoure")

    # noinspection PyArgumentList
    player_1 = User(
        created_at=datetime.datetime(2020, 1, 1, 0, 1, 1),
        username="sergialsina",
        email="sergia@gmail.com",
        name="Sergi",
        surname="Alsina",
        phone="63812910",
        rol=RolEnum.player,
        birthdate=datetime.datetime(1989, 1, 1),
        genere=GenereEnum.male,
        position=PositionEnum.rigth,
        matchname="Jordi",
        prefsmash=SmashEnum.cortada,
        club="Club Padel Inventat"

    )
    player_1.set_password("000000")
    player_1.tokens.append(UserToken(token="656e50e154865a5dc469b80437ed2f963b8f58c8857b66c9bf"))

    # noinspection PyArgumentList
    user_2 = User(
        created_at=datetime.datetime(2020, 1, 1, 0, 1, 1),
        username="user2",
        email="user2@gmail.com",
        name="user",
        surname="two",
        phone="63812910",
        rol=RolEnum.player,
        birthdate=datetime.datetime(2017, 1, 1),
        genere=GenereEnum.male,
        position=PositionEnum.left,
        matchname="Jordi",
        prefsmash= SmashEnum.globo,
        club="Club Tennis Manresa"
    )
    user_2.set_password("r45tgt")
    user_2.tokens.append(UserToken(token="0a821f8ce58965eadc5ef884cf6f7ad99e0e7f58f429f584b2"))

    db_session.add(user_admin)
    db_session.add(player_1)
    db_session.add(user_2)
    db_session.commit()

# -------------------- CREATE CATEGORIES --------------------
    mylogger.info("Creating default categories...")

    cat_1 = Category(
        genere=TournamentGenereEnum.mixt,
        age = AgeCategoriesTypeEnum.seniors
    )

    cat_2 = Category(
        genere=TournamentGenereEnum.male,
        age=AgeCategoriesTypeEnum.juniors
    )

    cat_3 = Category(
        genere=TournamentGenereEnum.female,
        age=AgeCategoriesTypeEnum.seniors
    )

    db_session.add(cat_1)
    db_session.add(cat_2)
    db_session.add(cat_3)
    db_session.commit()

# -------------------- CREATE FACILITIES --------------------
    mylogger.info("Creating default facilities...")

    facility_1 = Facility(
    name = "Club Tennis Manresa",
    latitude = 41.748809,
    longitude = 1.844407,
    provincia = "Barcelona"
    )

    facility_2 = Facility(
    name = "Club Padel Inventat",
    latitude = 42.748809,
    longitude = 1.844407,
    provincia = "Barcelona"
    )

    facility_3 = Facility(
    name="Infinit Igualada",
    latitude=41.584437,
    longitude=1.603788,
    provincia="Barcelona"
    )

    db_session.add(facility_1)
    db_session.add(facility_2)
    db_session.add(facility_3)
    db_session.commit()
# -------------------- CREATE TOURNAMENTS --------------------
    mylogger.info("Creating default tournaments...")
    week_period = datetime.timedelta(weeks=1)
    day_period = datetime.timedelta(days=1)

    tournament_1 = Tournament(
        created_at=datetime.datetime(2020, 1, 1, 0, 1, 1),
        name="Torneig de Matats",
        start_register_date = datetime.datetime.now() - (week_period * 3),
        finish_register_date = datetime.datetime.now() - (week_period * 1),
        start_date = datetime.datetime.now() + (week_period * 1),
        finish_date = datetime.datetime.now() + (week_period * 2),
        price_1 = 20,
        price_2 = 8,
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam libero ex, rhoncus non lectus sit amet, tincidunt scelerisque nulla. Curabitur aliquet justo non facilisis volutpat. Vestibulum suscipit odio leo, sed rutrum erat euismod sollicitudin. Quisque nisi massa, volutpat ut faucibus eget, accumsan et ligula. Pellentesque vestibulum, nisi non dapibus auctor, tellus magna tempor leo, volutpat ullamcorper eros sem vel quam. Phasellus ullamcorper sem ut arcu eleifend, eget euismod nibh viverra. Nulla facilisi. Suspendisse sed sem et eros faucibus lacinia. Duis rhoncus ante laoreet ante ultrices consectetur. Suspendisse bibendum varius velit, sed viverra dui porttitor sed. In pulvinar lectus et leo porttitor interdum. Phasellus hendrerit ac lorem eget euismod. Quisque posuere et dui sit amet fringilla. Curabitur malesuada convallis mauris. Sed malesuada quis neque quis vehicula. Suspendisse viverra mi quis tortor pharetra fermentum.",
        type = TournamentTypeEnum.draft,
        inscription_type = TournamentPrivacyTypeEnum.public,
        facility_id = 1,
        categories=[cat_1, cat_2, cat_3],
        owner_id=1
    )

    tournament_2 = Tournament(
        created_at=datetime.datetime(2020, 1, 1, 0, 1, 1),
        name="Torneig de Matats 2",
        start_register_date = datetime.datetime.now() + (week_period * 3),
        finish_register_date = datetime.datetime.now() + (week_period * 4),
        start_date = datetime.datetime.now() + (week_period * 5),
        finish_date = datetime.datetime.now() + (week_period * 6),
        price_1 = 20,
        price_2 = 8,
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam libero ex, rhoncus non lectus sit amet, tincidunt scelerisque nulla. Curabitur aliquet justo non facilisis volutpat. Vestibulum suscipit odio leo, sed rutrum erat euismod sollicitudin. Quisque nisi massa, volutpat ut faucibus eget, accumsan et ligula. Pellentesque vestibulum, nisi non dapibus auctor, tellus magna tempor leo, volutpat ullamcorper eros sem vel quam. Phasellus ullamcorper sem ut arcu eleifend, eget euismod nibh viverra. Nulla facilisi. Suspendisse sed sem et eros faucibus lacinia. Duis rhoncus ante laoreet ante ultrices consectetur. Suspendisse bibendum varius velit, sed viverra dui porttitor sed. In pulvinar lectus et leo porttitor interdum. Phasellus hendrerit ac lorem eget euismod. Quisque posuere et dui sit amet fringilla. Curabitur malesuada convallis mauris. Sed malesuada quis neque quis vehicula. Suspendisse viverra mi quis tortor pharetra fermentum.",
        type = TournamentTypeEnum.draft,
        inscription_type = TournamentPrivacyTypeEnum.public,
        facility_id = 2,
        categories = [cat_1,cat_2,cat_3],
        owner_id=1
    )
    tournament_3 = Tournament(
        created_at=datetime.datetime(2020, 1, 2, 0, 1, 1),
        name="Torneig de la UDL",
        start_register_date=datetime.datetime.now() + (week_period * 1),
        finish_register_date=datetime.datetime.now() + (week_period * 7),
        start_date=datetime.datetime.now() + (week_period * 2),
        finish_date=datetime.datetime.now() + (week_period * 6),
        price_1=10,
        price_2=8,
        description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam libero ex, rhoncus non lectus sit amet, tincidunt scelerisque nulla. Curabitur aliquet justo non facilisis volutpat. Vestibulum suscipit odio leo, sed rutrum erat euismod sollicitudin. Quisque nisi massa, volutpat ut faucibus eget, accumsan et ligula. Pellentesque vestibulum, nisi non dapibus auctor, tellus magna tempor leo, volutpat ullamcorper eros sem vel quam. Phasellus ullamcorper sem ut arcu eleifend, eget euismod nibh viverra. Nulla facilisi. Suspendisse sed sem et eros faucibus lacinia. Duis rhoncus ante laoreet ante ultrices consectetur. Suspendisse bibendum varius velit, sed viverra dui porttitor sed. In pulvinar lectus et leo porttitor interdum. Phasellus hendrerit ac lorem eget euismod. Quisque posuere et dui sit amet fringilla. Curabitur malesuada convallis mauris. Sed malesuada quis neque quis vehicula. Suspendisse viverra mi quis tortor pharetra fermentum.",
        type=TournamentTypeEnum.americana,
        inscription_type=TournamentPrivacyTypeEnum.privat,
        facility_id=3,
        categories=[cat_1],
        owner_id=2
    )
    db_session.add(tournament_1)
    db_session.add(tournament_2)
    db_session.add(tournament_3)
    db_session.commit()
    mylogger.info("Creating default couples...")

    for p in range(1, 33, 2):
        couple = Couple(
            player1_id=p,
            player2_id=p + 1
        )
        db_session.add(couple)
    db_session.commit()
    mylogger.info("Creating default matches for Round 1 del Torneig de la UDL...")

    set_results = ["7/6", "6/0", "6/3", "6/4", "6/2", "6/3"]

    m = 0
    matches = []
    for p in range(1, 33, 4):
        match = Match(
            couple1_player1_id=p,
            couple1_player2_id=p + 1,
            couple2_player1_id=p + 2,
            couple2_player2_id=p + 3,
            set1=random.choice(set_results),
            set2=random.choice(set_results)
        )
        db_session.add(match)
        matches.append(match)

    round = Round(
        category_id=1,
        tournament_id=3,
        id=1,
        matches=matches
    )

    db_session.add(round)
    db_session.commit()
    matches = []
    for p in range(1, 33, 8):
        match = Match(
            couple1_player1_id=p,
            couple1_player2_id=p + 1,
            couple2_player1_id=p + 2,
            couple2_player2_id=p + 3,
            set1=random.choice(set_results),
            set2=random.choice(set_results)
        )
        db_session.add(match)
        matches.append(match)

    round = Round(
        category_id=1,
        tournament_id=3,
        id=2,
        matches=matches
    )

    db_session.add(round)
    db_session.commit()
    matches = []
    for p in range(1, 33, 16):
        match = Match(
            couple1_player1_id=p,
            couple1_player2_id=p + 1,
            couple2_player1_id=p + 2,
            couple2_player2_id=p + 3,
            set1=random.choice(set_results),
            set2=random.choice(set_results)
        )
        db_session.add(match)
        matches.append(match)

    round = Round(
        category_id=1,
        tournament_id=3,
        id=3,
        matches=matches
    )

    db_session.add(round)
    db_session.commit()
    matches = []
    for p in range(1, 33, 32):
        match = Match(
            couple1_player1_id=p,
            couple1_player2_id=p + 1,
            couple2_player1_id=p + 2,
            couple2_player2_id=p + 3,
            set1=random.choice(set_results),
            set2=random.choice(set_results)
        )
        db_session.add(match)
        matches.append(match)

    round = Round(
        category_id=1,
        tournament_id=3,
        id=4,
        matches=matches
    )

    db_session.add(round)
    db_session.commit()
    db_session.close()
