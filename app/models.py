# -*- encoding: utf-8 -*-
"""
Flask Boilerplate
Author: AppSeed.us - App Generator
"""

from app         import db
from flask_login import UserMixin

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

from . common    import COMMON, STATUS, DATATYPE

class User(UserMixin, db.Model):

    id          = db.Column(db.Integer,     primary_key=True)
    user        = db.Column(db.String(64),  unique = True)
    email       = db.Column(db.String(120), unique = True)
    name        = db.Column(db.String(500))
    role        = db.Column(db.Integer)
    password    = db.Column(db.String(500))
    password_q  = db.Column(db.Integer)
    projetos    = db.relationship('Projeto', backref='user', lazy=True)

    def __init__(self, user, password, name, email):
        self.user       = user
        self.password   = password
        self.password_q = DATATYPE.CRYPTED
        self.name       = name
        self.email      = email

        self.group_id = None
        self.role     = None

    def __repr__(self):
        return '<User %r>' % (self.id)

    def save(self):

        # inject self into db session
        db.session.add ( self )

        # commit change and save the object
        db.session.commit( )

        return self

class Projeto (db.Model):
    id          =   db.Column(db.Integer,     primary_key=True)
    nome        =   db.Column(db.String(500))
    user_id     =   db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    artigos     =   db.relationship('Artigo', backref='projeto', lazy=True, cascade="delete")
    referencias =   db.relationship('Referencia', backref='projeto', lazy=True, cascade="delete")
    cross_refs  =   db.relationship('ReferenciaCruzada', backref='projeto', lazy=True, cascade="delete")
    palavras    =   db.relationship('Palavra', backref='projeto', lazy=True, cascade="delete")

class Artigo (db.Model):
    id          =   db.Column(db.Integer,     primary_key=True)
    titulo      =   db.Column(db.String(500))
    country     =   db.Column(db.String(500))
    abstract    =   db.Column(db.Text)
    path        =   db.Column(db.String(500))
    projeto_id  =   db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)
    referencias =   db.relationship('Referencia', backref='artigo', lazy=True, cascade="delete")
    palavras    =   db.relationship('Palavra', backref='artigo', lazy=True, cascade="delete")

class Referencia (db.Model):
    __tablename__   =   "referencia"
    id              =   db.Column(db.Integer,     primary_key=True)
    texto           =   db.Column(db.String(500), nullable=False)
    artigo_id       =   db.Column(db.Integer, db.ForeignKey('artigo.id'), nullable=False)
    projeto_id      =   db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)
    cross_ref       =   db.relationship('ReferenciaCruzada', lazy="dynamic", cascade="delete", foreign_keys = 'ReferenciaCruzada.ref1')
    back_cross_ref  =   db.relationship('ReferenciaCruzada', lazy="dynamic", cascade="delete", foreign_keys = 'ReferenciaCruzada.ref2', backref = 'referencia_cruzada')

    #@hybrid_property
    #def referencia_cruzada(self):
    #    return self.cross_ref + self.back_cross_ref

    #def __init__ (self):
    #    self.referencia_cruzada = self.cross_ref + self.back_cross_ref


class ReferenciaCruzada (db.Model):
    __tablename__   =   "referencia_cruzada"
    id          =   db.Column(db.Integer, primary_key=True)
    ref1        =   db.Column(db.Integer, db.ForeignKey('referencia.id'), nullable=False)
    ref2        =   db.Column(db.Integer, db.ForeignKey('referencia.id'), nullable=False)
    projeto_id  =   db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)
    #referencia  =   db.relationship("Referencia", back_populates="back_cross_ref")

class Palavra (db.Model):
    id          =   db.Column(db.Integer, primary_key=True)
    palavra     =   db.Column(db.String(100), nullable=False)
    rank        =   db.Column(db.Integer, nullable=False)
    projeto_id  =   db.Column(db.Integer, db.ForeignKey('projeto.id'), nullable=False)
    artigo_id   =   db.Column(db.Integer, db.ForeignKey('artigo.id'), nullable=False)
