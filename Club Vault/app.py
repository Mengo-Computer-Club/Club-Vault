from crypt import methods
from genericpath import isfile
import os
import flask
import time
from database import Vault, FileData, db_start, Session
from playhouse.shortcuts import model_to_dict
app = flask.Flask(__name__)
# Returns the index page (the one with the open vault)
@app.route('/')
def index():
    return flask.render_template('index.html')

# Returns the create page (where one can create a vault)
@app.route('/create')
def create():
    return flask.render_template('create.html')

# Returns the dashboard page (where one can view files, download and upload)
# It also checks if it is from the create.html so that it can show a helpful message.
# This message will inform the user that their vault ID must be memorised or written down.
@app.route('/dash')
def dash():
    has_create = ""
    if 'create' in flask.request.args:
        has_create = '1'
    return flask.render_template('dash.html', from_create=has_create)

# This creates new vaults when given the name of the vault and the passcode
# This does not use password hashing since it is a waste of time
# In addition to that, it also create an initial session for the user to upload files
@app.route('/create_handler', methods=["POST"])
def create_handler():
    data = flask.request.get_json()
    vault = Vault.create(name = data['name'], passcode=data['passcode'])
    vault.save()
    session = Session.create(vault=vault)
    session.save()
    return {'session_id':session.ID, 'name': data['name'], 'vault_id': vault.ID}

# This handles file uploads to the server
@app.route('/upload_handler', methods=["POST"])
def upload_handler():
    data = flask.request.form
    session = Session.get_or_none(Session.ID == data['session']) # checks the session in the database
    if not session:
        return {}, 404
    filename = str(int(time.time())) # The filename for these files is the timestamp of upload
    filedata = FileData.create(
        oname=data['oname'],
        filename=filename,
        filesize=data['size'],
        when=data['created'],
        vault=session.vault
    ) # Create a dataentry in the database for this file inorder to track it
    filedata.save()
    file = flask.request.files['file']
    file.save(os.path.join('user_files', filename)) # Then store the file data in a file with the respective filename
    return flask.redirect('/dash'), 200

# Handler for the download button on the files
@app.route('/download')
def download():
    data = flask.request.args
    session = Session.get_or_none(Session.ID == data['session_id']) # Get session
    if not session:
        return {}, 404
    file = FileData.get_or_none(FileData.filename == data['filename']) # get the file
    if not file:
        return {}, 418
    if file.vault != session.vault:
        return {}, 406
    return flask.send_file(open(f"user_files/{file.filename}", 'rb'), download_name=file.oname) # Send the file

# This one deletes files
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
    if os.path.exists(filepath): # Check file if exists
        os.remove(filepath) # Delete the file
        file.delete_instance() # Delete the file metadata
    return flask.redirect('/dash'), 200

# This function runs when the user opens the dashboard and needs their data
@app.route('/get_files')
def get_files():
    data = flask.request.args
    session = Session.get_or_none(Session.ID == data['session_id'])
    if not session:
        return {}, 404
    files = session.vault.files
    nfiles = []
    for file in files:
        nfiles.append(model_to_dict(file)) # converts the tables to json
    return {
        "files": nfiles,
    }

if __name__ == "__main__":
    db_start()
    app.run('localhost', port=8000, debug=True)
