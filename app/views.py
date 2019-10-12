# -*- encoding: utf-8 -*-
"""
Dark Dashboard - coded in Flask
Author: AppSeed.us - App Generator
"""

# all the imports necessary
from flask import json, url_for, redirect, render_template, flash, g, session, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException, NotFound, abort

import os

from app  import app

from flask       import url_for, redirect, render_template, flash, g, session, jsonify, request, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from app         import app, lm, db, bc
from . models    import User, Projeto, Artigo, Referencia
from . common    import COMMON, STATUS
from . assets    import *
from . forms     import LoginForm, RegisterForm, ProjetoForm, ArtigoUploadForm
from werkzeug.utils import secure_filename

import os, shutil, re, cgi, random, string

# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# authenticate user
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('login'))

# register user
@app.route('/register.html', methods=['GET', 'POST'])
def register():

    # define login form here
    form = RegisterForm(request.form)

    msg = None

    # custommize your pate title / description here
    page_title       = 'Registro - Extrator Automático de Literatura'
    page_description = 'Página de registro para o extrator automático de literatura.'

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)
        name     = request.form.get('name'    , '', type=str)
        email    = request.form.get('email'   , '', type=str)

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'

        else:
            pw_hash = bc.generate_password_hash(password)

            user = User(username, pw_hash, name, email)

            user.save()

            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'

    # try to match the pages defined in -> themes/light-bootstrap/pages/
    return render_template( 'layouts/default.html',
                            title=page_title,
                            content=render_template( 'pages/register.html',
                                                     form=form,
                                                     msg=msg) )

# authenticate user
@app.route('/login.html', methods=['GET', 'POST'])
def login():

    # define login form here
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # custommize your page title / description here
    page_title = 'Login - Extrator Automático de Literatura'
    page_description = 'Login para o extrator automático de literatura.'

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        if user:

            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unkkown user"

    # try to match the pages defined in -> themes/light-bootstrap/pages/
    return render_template( 'layouts/default.html',
                            title=page_title,
                            content=render_template( 'pages/login.html',
                                                     form=form,
                                                     msg=msg) )

# Used only for static export
@app.route('/user.html')
@login_required
def user():

    # custommize your page title / description here
    page_title = '{} homepage'.format(current_user.name)
    page_description = 'Open-Source Flask Dark Dashboard, the icons page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/user.html',
                                                     user=current_user) )


# Used only for static export
@app.route('/projetos.html')
@login_required
def projetos():

    # custommize your page title / description here
    page_title = 'Projetos - Extrator Automático de Literatura'
    page_description = 'Projetos de extração de literatura criados pelo usuário.'

    projetos = current_user.projetos

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/projetos.html',
                                                     projetos=projetos) )

# Used only for static export
@app.route('/<projeto_id>/projeto.html')
@login_required
def projeto(projeto_id):

    # custommize your page title / description here
    page_title          = 'Projeto - Extrator Automático de Literatura'
    page_description    = 'Projeto de extração de literatura criados pelo usuário.'

    projeto             = Projeto.query.get(projeto_id)

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/projeto.html',
                                                     projeto=projeto,
                                                     artigo_upload=ArtigoUploadForm()) )

@app.route('/<projeto_id>/artigo_upload', methods=['POST'])
@login_required
def artigo_upload(projeto_id):
    form = ArtigoUploadForm()

    if form.validate_on_submit():
        f           = form.artigo.data
        filename    = secure_filename(f.filename)
        filepath    = os.path.join(
            app.instance_path, 'artigos', filename
            )
        f.save(filepath)

        artigo = Artigo(titulo=filename,
                        country=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)),
                        abstract=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(500)),
                        path=filepath,
                        projeto_id=projeto_id)
        db.session.add(artigo)
        db.session.commit()

        for _ in range(0, random.randint(5, 10)):
            referencia = Referencia(texto=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)),
                                    artigo_id=artigo.id,
                                    projeto_id=projeto_id)
            db.session.add(referencia)
            db.session.commit()


        flash('Seu artigo foi criado')

        return redirect('{}/projeto.html'.format(projeto_id))


@app.route('/artigo/<artigo_id>/delete', methods=['GET'])
@login_required
def artigo_delete(artigo_id):
    artigo = Artigo.query.get(artigo_id)
    projeto_id = artigo.projeto.id
    db.session.delete(artigo)
    db.session.commit()
    return redirect('{}/projeto.html'.format(projeto_id))

@app.route('/form_projetos.html', methods=['GET', 'POST'])
@login_required
def form_projetos():

    # define login form here
    form = ProjetoForm()

    # Flask message injected into the page, in case of any errors
    msg = None

    # custommize your page title / description here
    page_title = 'Cadastrar Projeto - Extrator Automático de Literatura'
    page_description = 'Cadastrar projetos de extração automática de literatura.'

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        projeto = Projeto(nome=form.nome.data, user_id=current_user.id)
        db.session.add(projeto)
        db.session.commit()
        flash('Seu projeto foi criado')
        return redirect(url_for('projetos'))



    # try to match the pages defined in -> themes/light-bootstrap/pages/
    return render_template( 'layouts/default.html',
                            title=page_title,
                            content=render_template( 'pages/form_projetos.html',
                                                     form=form,
                                                     msg=msg) )


# Used only for static export
@app.route('/icons.html')
@login_required
def icons():

    # custommize your page title / description here
    page_title = 'Icons - Flask Dark Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Dark Dashboard, the icons page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/icons.html') )

# Used only for static export
@app.route('/tables.html')
@login_required
def tables():

    # custommize your page title / description here
    page_title = 'Tables - Flask Dark Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Dark Dashboard, the tables page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/tables.html') )

# Used only for static export
@app.route('/notifications.html')
@login_required
def notifications():

    # custommize your page title / description here
    page_title = 'Tables - Flask Dark Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Dark Dashboard, the tables page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/notifications.html') )

# Used only for static export
@app.route('/typography.html')
@login_required
def typography():

    # custommize your page title / description here
    page_title = 'Typography - Flask Dark Dashboard | AppSeed App Generator'
    page_description = 'Open-Source Flask Dark Dashboard, the tables page.'

    # try to match the pages defined in -> pages/
    return render_template('layouts/default.html',
                            content=render_template( 'pages/typography.html') )

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
@login_required
def index(path):

    content = None

    try:

        # try to match the pages defined in -> themes/light-bootstrap/pages/
        return render_template('layouts/default.html',
                                content=render_template( 'pages/'+path) )
    except:
        abort(404)

#@app.route('/favicon.ico')
#def favicon():
#    return send_from_directory(os.path.join(app.root_path, 'static'),
#                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

#@app.route('/sitemap.xml')
#def sitemap():
#    return send_from_directory(os.path.join(app.root_path, 'static'),
#                               'sitemap.xml')

# ------------------------------------------------------

# error handling
# most common error codes have been added for now
# TO DO:
# they could use some styling so they don't look so ugly

def http_err(err_code):

    err_msg = 'Oups !! Some internal error ocurred. Thanks to contact support.'

    if 400 == err_code:
        err_msg = "It seems like you are not allowed to access this link."

    elif 404 == err_code:
        err_msg  = "The URL you were looking for does not seem to exist."
        err_msg += "<br /> Define the new page in /pages"

    elif 500 == err_code:
        err_msg = "Internal error. Contact the manager about this."

    else:
        err_msg = "Forbidden access."
        return redirect(url_for('login'))


    return err_msg

@app.errorhandler(401)
def e401(e):
    return http_err( 401) # "It seems like you are not allowed to access this link."

@app.errorhandler(404)
def e404(e):
    return http_err( 404) # "The URL you were looking for does not seem to exist.<br><br>
	                      # If you have typed the link manually, make sure you've spelled the link right."

@app.errorhandler(500)
def e500(e):
    return http_err( 500) # "Internal error. Contact the manager about this."

@app.errorhandler(403)
def e403(e):
    return http_err( 403 ) # "Forbidden access."

@app.errorhandler(410)
def e410(e):
    return http_err( 410) # "The content you were looking for has been deleted."


