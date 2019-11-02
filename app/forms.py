# -*- encoding: utf-8 -*-
"""
Flask Boilerplate
Author: AppSeed.us - App Generator
"""

from flask_wtf          import FlaskForm, RecaptchaField
from flask_wtf.file     import FileField, FileRequired
from wtforms            import StringField, TextAreaField, SubmitField, PasswordField, MultipleFileField
from wtforms.validators import InputRequired, Email, DataRequired

class LoginForm(FlaskForm):
    username    = StringField  (u'Username'        , validators=[DataRequired()])
    password    = PasswordField(u'Password'        , validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username    = StringField  (u'Username'  , validators=[DataRequired()])
    password    = PasswordField(u'Password'  , validators=[DataRequired()])
    email       = StringField  (u'Email'     , validators=[DataRequired(), Email()])
    name        = StringField  (u'Name'      , validators=[DataRequired()])

class ProjetoForm(FlaskForm):
    nome        = StringField(u'Nome', validators=[DataRequired()])
    descricao   = StringField(u'Descrição', validators=[DataRequired()])

class ArtigoUploadForm(FlaskForm):
    artigo      = MultipleFileField(validators=[DataRequired()])

class ReferenciaForm(FlaskForm):
    texto       = TextAreaField(u'Texto', validators=[DataRequired()])

class ArtigoForm(FlaskForm):
    titulo      = StringField(u'Título', validators=[DataRequired()])
    country     = StringField(u'País', validators=[DataRequired()])
    abstract    = TextAreaField(u'Resumo (Abstract)', validators=[DataRequired()])
