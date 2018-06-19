from sqlalchemy import Table, Column, Integer, ForeignKey, String, Sequence, DateTime
from sqlalchemy.orm import relationship, backref
from database import connector


class Profesor(connector.Manager.Base):
    __tablename__ = 'profesor'
    id = Column(Integer, Sequence('user_id_seq'),primary_key=True)
    email = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))
    alumnos=relationship("Alumno", backref="profesor")

class Alumno(connector.Manager.Base):
    __tablename__ = 'alumno'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    edad=Column(Integer)
    test1 =Column(Integer)
    test2 = Column(Integer)
    resultado=Column(String(50))
    profesor_id = Column(Integer, ForeignKey('profesor.id'))