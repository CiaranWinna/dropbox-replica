# importing the required libraires
from google.appengine.ext import ndb


class BlobCollection(ndb.Model):
    # blobcollection model that holds a number of lists that will be used when uploading a file,
    # it will store the various data gathered from the blob info method
    filenames = ndb.StringProperty(repeated=True)
    creations = ndb.DateTimeProperty(repeated=True)
    sizes = ndb.IntegerProperty(repeated=True)
    types = ndb.StringProperty(repeated=True)
    blobs = ndb.BlobKeyProperty(repeated=True)
    directory_saved_in = ndb.StringProperty(repeated=True)
    user = ndb.StringProperty(repeated=True)
