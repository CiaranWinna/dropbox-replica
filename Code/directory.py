# importing the required libraries
from google.appengine.ext import ndb


class Directory(ndb.Model):
    # when a directory is created, this model will store the name, the parent
    # directory and user name that created the directory
    line1 = ndb.StringProperty()
    directory_saved_in = ndb.StringProperty()
    owner = ndb.StringProperty()
