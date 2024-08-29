from crypt import methods
from genericpath import isfile
import os
import flask
import time
from database import Vault, FileData, db_start, Session
from playhouse.shortcuts import model_to_dict
app = flask.Flask(__name__)
@app.route('/')
def index():
    return flask.render_template('index.html')
@app.route('/create')
def create():
    return flask.render_template('create.html')
@app.route('/dash')
def dash():
    has_create = ""
    if 'create' in flask.request.args:
        has_create = '1'
    return flask.render_template('dash.html', from_create=has_create)

@app.route('/create_handler', methods=["POST"])
def create_handler():
    data = flask.request.get_json()
    vault = Vault.create(name = data['name'], passcode=data['passcode'])
    vault.save()
    session = Session.create(vault=vault)
    session.save()
    return {'session_id':session.ID, 'name': data['name'], 'vault_id': vault.ID}

@app.route('/upload_handler', methods=["POST"])
def upload_handler():
    data = flask.request.form
    session = Session.get_or_none(Session.ID == data['session'])
    if not session:
        return {}, 404
    filename = str(int(time.time()))
    filedata = FileData.create(oname=data['oname'], filename=filename, filesize=data['size'], when=data['created'], vault=session.vault)
    filedata.save()
    file = flask.request.files['file']
    file.save(os.path.join('user_files', filename))
    return flask.redirect('/dash'), 200

@app.route('/download')
def download():
    data = flask.request.args
    session = Session.get_or_none(Session.ID == data['session_id'])
    if not session:
        return {}, 404
    file = FileData.get_or_none(FileData.filename == data['filename'])
    if not file:
        return {}, 418
    if file.vault != session.vault:
        return {}, 406
    return flask.send_file(open(f"user_files/{file.filename}", 'rb'), download_name=file.oname)

@app.route('/delete')
def delete():
    data = flask.request.args
    session = Session.get_or_none(Session.ID == data['session_id'])
    if not session:
        return {}, 404
    file = FileData.get_or_none(FileData.filename == data['filename'])
    if not file:
        return {}, 418
    if file.vault != session.vault:
        return {}, 406
    filepath = os.path.join('user_files', file.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        file.delete_instance()
    return flask.redirect('/dash'), 200

@app.route('/get_files')
def get_files():
    data = flask.request.args
    session = Session.get_or_none(Session.ID == data['session_id'])
    if not session:
        return {}, 404
    files = session.vault.files
    nfiles = []
    for file in files:
        nfiles.append(model_to_dict(file))
    return {
        "files": nfiles,
    }

if __name__ == "__main__":
    db_start()
    app.run('localhost', port=8000, debug=True)