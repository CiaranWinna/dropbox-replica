from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    # post method
    def post(self):
        self.response.headers['Content-Type'] = 'multipart/form-data'
        # getting the passed file
        upload = self.get_uploads()[0]
        # getting the passed variable
        directory = self.request.get('directory')
        owner = self.request.get('owner')
        # getting the blob information of the uploaded file by using the upload key
        blobinfo = blobstore.BlobInfo(upload.key())
        filename = blobinfo.filename
        content_type = blobinfo.content_type
        size = blobinfo.size
        creation = blobinfo.creation

        # getting the key of the stored collection blob that will hold the file
        collection_key = ndb.Key('BlobCollection', 1)
        collection = collection_key.get()

        # appending the various info points taken from the blob info to the blob collection object
        collection.filenames.append(filename)
        collection.creations.append(creation)
        collection.sizes.append(size)
        collection.types.append(content_type)
        collection.blobs.append(upload.key())
        collection.directory_saved_in.append(directory)
        collection.user.append(owner)
        # pushing the changes to the datastore to the database
        collection.put()

        # redirecting to the main directory
        self.redirect('/')
