# importing the required libraries
import webapp2
import jinja2
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    # model that is used when downloading a file
    def get(self):
        # a get method that will accept the passed index of the file to be downloaded
        index = int(self.request.get('index'))
        # getting the collection key
        collection_key = ndb.Key('BlobCollection', 1)
        # retrieving the the blobcollection object from the datastore
        collection = collection_key.get()
        # sending the blob with the specified location to the user
        self.send_blob(collection.blobs[index])
