from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    pw = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, nullable=False)
    h = Column(Integer, nullable=False)
    a = Column(Integer, nullable=False)

class Bonus(Base):
    __tablename__ = "bonuses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    champ = Column(String, nullable=True)
    scorer = Column(String, nullable=True)

class FantasySquad(Base):
    __tablename__ = "fantasy_squads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    squad_data = Column(JSON, nullable=True)
    cap = Column(String, nullable=True)
    vc = Column(String, nullable=True)

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    team = Column(String, nullable=False)
    position = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(String, nullable=True)  # <--- התמונה שלנו יושבת פה בבטחה

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_num = Column(Integer, nullable=False, unique=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    home_code = Column(String, nullable=False)
    away_code = Column(String, nullable=False)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    status = Column(String, default="scheduled")
    stage = Column(String, default="group")
    kickoff = Column(String, nullable=True)