from peewee import * # type: ignore

db = SqliteDatabase('test.db')

class BaseModel(Model):
    class Meta:
        database = db

class Vault(BaseModel):
    ID = AutoField(primary_key=True)
    name = CharField(20)
    passcode = CharField(6)

class FileData(BaseModel):
    oname = CharField(100)
    filename = CharField(12)
    filesize = FloatField()
    when = FloatField()
    vault = ForeignKeyField(Vault, backref="files")

class Session(BaseModel):
    ID = AutoField(primary_key=True)
    vault = ForeignKeyField(Vault, backref='sessions')

def db_start():
    db.connect()
    db.create_tables([Vault, FileData, Session])