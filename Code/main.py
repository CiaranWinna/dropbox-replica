# importing the required libraries
import os
import webapp2
import jinja2
import collections
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from myuser import MyUser
from directory import Directory
from blobcollection import BlobCollection
from downloadhandler import DownloadHandler
from uploadhandler import UploadHandler
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class MainPage(webapp2.RequestHandler):

    # feedback messages
    feedback = ""

    # directory management variable
    parent_directory = ""
    directory_saved_in = "home"

    # tracking parents
    parent_pointer = 0
    parent = []

    # temp username
    username = "Temp"

    # checking for structure wide duplicates
    duplicates = []
    cur_duplicates = []

    # non current directories
    non_current_directories = []
    counter = 0

    # method that will be called when methods call the redirect method using the "/"
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        # using the user libraries to get the current user who called the method
        user = users.get_current_user()

        # if the user is a guest
        if user == None:
            # set the templates value that can be used in the html file
            template_values = {
                'login_url': users.create_login_url(self.request.uri)}
            # get the passed html file that will be used in the generaton of the template
            template = JINJA_ENVIRONMENT.get_template('mainpage_guest.html')
            # respond to the request by rendering the html page of the guest user
            self.response.write(template.render(template_values))
            return

        # login
        # user login details, getting the MyUser object in the datastore
        myuser_key = ndb.Key('MyUser', user.user_id())
        # pulling the MyUser object thats linked to the key
        myuser = myuser_key.get()
        # if the object doesn't exist then create one and push changes to the datastore
        if myuser == None:
            # genarte a new MyUser object with the id gathered by the user method
            myuser = MyUser(id=user.user_id())
            myuser.username = MainPage.username
            # push changes to the datastore
            myuser.put()

        # creation of blob collection
        collection_key = ndb.Key('BlobCollection', 1)
        collection = collection_key.get()
        # if the collection doesn't exist then create a new object and push changes to the datastore
        if collection == None:
            collection = BlobCollection(id=1)
            # push changes to the datastore
            collection.put()

        # checking for duplicates in the user's directory
        temp_array = []
        # getting all the files names
        for i in collection.filenames:
            if i != "none":
                temp_array.append(i)

        # checking if there are any duplicates, if they are they are added to the duplicates array
        # this will be sent to the html page
        MainPage.duplicates = [item for item, count in collections.Counter(
            temp_array).items() if count > 1]

        # checking for duplicates in the current directory
        temp_cur_dir_duplicates = []
        # looping through the files of the current directory
        for i in range(len(collection.filenames)):
            # gettin the filename and direcotry under which it is saved
            fn = collection.filenames[i]
            dir = collection.directory_saved_in[i]
            # if the directory is the same as the current directory then append to the temp array
            if (fn != "none") and (dir == MainPage.directory_saved_in):
                temp_cur_dir_duplicates.append(fn)

        # looping through the temp array to see if there are duplicates. If there are,
        # then add them to the current dirrectory duplicates array
        MainPage.cur_duplicates = [item for item, count in collections.Counter(
            temp_cur_dir_duplicates).items() if count > 1]

        # adding non current directories
        nc_directories = myuser.directories
        # looping through all directories and adding those that aren't the current directory
        MainPage.non_current_directories = filter(
            lambda a: a != MainPage.directory_saved_in, nc_directories)

        # getting filename properties from the blob object variable
        collection_filnames = collection.filenames
        collection_creations = collection.creations
        collection_sizes = collection.sizes
        collection_types = collection.types
        collection_blobs = collection.blobs
        collection_directory = collection.directory_saved_in
        collection_user = collection.user

        # assigning the templates values that will be sent to the html
        # file with the variables that are stored in this class
        template_values = {'logout_url': users.create_logout_url(self.request.uri),
                           'directories': myuser.directories,
                           'feedback': MainPage.feedback,
                           'directory_saved_in': MainPage.directory_saved_in,
                           'parent_directory': MainPage.parent_directory,
                           'collection': collection,
                           'upload_url': blobstore.create_upload_url('/upload'),
                           'parents': MainPage.parent,
                           'parent_pointer': MainPage.parent_pointer,
                           'collection_filenames': collection_filnames,
                           'collection_creations': collection_creations,
                           'collection_sizes': collection_sizes,
                           'collection_types': collection_types,
                           'collection_blobs': collection_blobs,
                           'collection_directory': collection_directory,
                           'username': MainPage.username,
                           'collection_user': collection_user,
                           'duplicates': MainPage.duplicates,
                           'cur_duplicates': MainPage.cur_duplicates,
                           'non_cur_directories': MainPage.non_current_directories,
                           'counter': MainPage.counter
                           }
        # setting the template the sending the template as a response to the request
        template = JINJA_ENVIRONMENT.get_template('mainpage.html')
        self.response.write(template.render(template_values))

    # method used if the html p
    def post(self):
        # setting the response to a html file
        self.response.headers['Content-Type'] = 'text/html'
        # getting the passed form that has the name 'button'
        action = self.request.get('button')

        # if the passed the form has the name '+Directory'
        if action == '+ Directory':
            # getting the response variables form the passed form
            line1 = self.request.get('line1')
            directory_saved_in = self.request.get('directory_saved_in')
            owner = self.request.get('owner')

            # getting the current user of the website
            user = users.get_current_user()

            # retrieving the key of the MyUser model
            myuser_key = ndb.Key('MyUser', user.user_id())
            # pulling the object that has the retrived key
            myuser = myuser_key.get()

            # getting the directory key in the MyUser model
            valid_name_direcotry_key = myuser.directories
            # checking if the direcotry name is already used
            is_valid = True
            for i in valid_name_direcotry_key:
                # if the passed name already exists in the current direcotry this set the variabel
                if i.line1 == line1:
                    is_valid = False
            # if the direcotry is not taken, then create a new Directory object
            if is_valid == True:
                # genearing a new object and assigning the passed values to the object
                new_directory = Directory(
                    line1=line1,
                    directory_saved_in=directory_saved_in,
                    owner=owner
                )
                # appending the new object to the directory list in the MyUser object
                myuser.directories.append(new_directory)
                MainPage.feedback = "Directory has been added!"
                # pushing changes to the datastore
                myuser.put()
            else:
                # send feeback to the user that the directory name is already taken
                MainPage.feedback = "Directory name ALREADY exists in current directory! Please use another directory name"

            # redirect to main directory
            self.redirect('/')

        # if user enter into a created diretory
        elif action == "Enter Directory":
            # getting the directory that the user wants to enter into
            entered_directory = self.request.get('entered_directory')
            parent_directory = str(self.request.get('parent_directory'))
            # append to the parent stack
            MainPage.parent.append(parent_directory)
            # change parent variable
            MainPage.directory_saved_in = entered_directory
            if len(MainPage.parent) == 0:
                # reset the pointer
                MainPage.parent_pointer = 0
            else:
                # setting the pointer to the max size -1 of the length of the parent array
                MainPage.parent_pointer = len(MainPage.parent) - 1
            # setting the parent variable to the last position of the stack
            MainPage.parent_directory = MainPage.parent[MainPage.parent_pointer]
            # redirect to main directory
            self.redirect('/')

        # if the user wants to go back to the parent directory
        elif action == "../":
            # setting the current directory to the last item of the stack
            MainPage.directory_saved_in = MainPage.parent[MainPage.parent_pointer]
            # pop the last item of the stack
            MainPage.parent.pop(MainPage.parent_pointer)
            # if the len is 0 then assign the pointer to 0
            if len(MainPage.parent) == 0:
                MainPage.parent_pointer = 0
            else:
                # reduce the pointer by one to account for the stack pop
                MainPage.parent_pointer = len(MainPage.parent) - 1
            # redirect to the main directory
            self.redirect('/')

        elif action == 'Delete':
            # save the passed index
            index = int(self.request.get('index'))

            # getting the current user key
            user = users.get_current_user()
            # get the MyUser key
            myuser_key = ndb.Key('MyUser', user.user_id())
            # pull the object from the datastore
            myuser = myuser_key.get()
            # delete the directory from the datastore
            del myuser.directories[index]
            # push changes to the datastore
            myuser.put()
            # give feedback to the user
            MainPage.feedback = "Directory has been deleted!"
            # redirect to the main directory
            self.redirect('/')

        # if a user wants to delete a file
        elif action == 'Delete File':
            # get the passed to index variable
            index = int(self.request.get('delete_index'))

            # getting the blob collection key
            collection_key = ndb.Key('BlobCollection', 1)
            collection = collection_key.get()

            # removing the file from the direcotry
            collection.filenames[index] = "none"
            collection.directory_saved_in[index] = "none"
            # push changes to the datastore
            collection.put()
            # give feedback to the user
            MainPage.feedback = "File was successfully deleted from directory!"
            # redirect to the main directory
            self.redirect('/')

        # if the user wants to the change their username
        elif action == 'Change username':
            # get the passed username
            name = self.request.get('changed_username')

            # changing file owner to the chanaged username
            user = users.get_current_user()
            myuser_key = ndb.Key('MyUser', user.user_id())
            # getting the user object
            myuser = myuser_key.get()

            # changing the username on the MyUser object
            myuser.username = name

            # looping through directories and changing directory ownership to the new username
            directories = myuser.directories
            for i in directories:
                # if the owner field of the directory equals the user's old username
                if i.owner == MainPage.username:
                    # change the field to the new username
                    i.owner = name
            # push changes to the datastore
            myuser.put()

            # getting the blob collection key, looping through and changing file ownership to the new username
            collection_key = ndb.Key('BlobCollection', 1)
            # getting the collection object
            collection = collection_key.get()
            # getting the user list of the collection model
            file_user = collection.user
            for i in file_user:
                # if indexed name equals the old username
                if i == MainPage.username:
                    # assign the index name to the new username
                    i == name
            # push changes
            collection.put()

            # changing template value and storing changes to datastore
            MainPage.username = name
            # redirect back to the main directory
            MainPage.feedback = "Username has been changed!"
            self.redirect('/')

        # if the user wants to change a file to a new directory
        elif action == 'Send File':
            # assign the passed variables for the file transfer
            index = int(self.request.get('index'))
            change_to_dir = self.request.get('optradio')
            old_dir = self.request.get('directory')

            # retrieving the collection blob object
            collection_key = ndb.Key('BlobCollection', 1)
            collection = collection_key.get()
            # getting the collection variable list 'directory_saved_in'
            dir_to_change_to = collection.directory_saved_in
            # setting the file's directory field to the changed directory
            dir_to_change_to[index] = change_to_dir
            # pushing changes
            collection.put()
            # sending feedback
            MainPage.feedback = "Successfully changed filed to chosen directory!"
            # redirect to the main directory
            self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/upload', UploadHandler),
    ('/download', DownloadHandler)
])
