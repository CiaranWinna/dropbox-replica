# importing the required libraires
from google.appengine.ext import ndb
from directory import Directory
from blobcollection import BlobCollection


class MyUser(ndb.Model):
    # MyUser model which will be user to track the current user
    username = ndb.StringProperty()
    directories = ndb.StructuredProperty(Directory, repeated=True)
    directory_files = ndb.StructuredProperty(BlobCollection)
