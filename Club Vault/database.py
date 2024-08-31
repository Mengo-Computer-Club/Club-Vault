from peewee import * # type: ignore

# For this file I don't need to be too detailed since it's a database
# So I'm just going to write what the fields and models mean
db = SqliteDatabase('test.db')

class BaseModel(Model): # This just simplifies life for me
    class Meta:
        database = db

# Stores data about the Vault
class Vault(BaseModel):
    ID = AutoField(primary_key=True) # Unique ID
    name = CharField(20) # name of the vault
    passcode = CharField(6) # passcode of the vault

# This is the file metadata. It is used to identify files.
class FileData(BaseModel):
    oname = CharField(100) # The file's original name
    filename = CharField(12) # The file name assigned to it ( It's upload timestamp ) PS: It is unique since we don't time travel
    filesize = FloatField() # The size of the file
    when = FloatField() # Timestamp of when upload
    vault = ForeignKeyField(Vault, backref="files") # Vault it belongs to

# This stores user sessions on the server
class Session(BaseModel):
    ID = AutoField(primary_key=True) # Unique ID of the session
    vault = ForeignKeyField(Vault, backref='sessions') # The Vault it's linked to

def db_start():
    db.connect()
    db.create_tables([Vault, FileData, Session])
