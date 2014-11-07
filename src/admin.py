from libmain import doRender
import logging
import datamodel
import urllib
import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.api import mail 
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from libuser import isContributingUser, isAdministratorUser

jinja_environment2 = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'), autoescape=True)

def doRender2(handler, tname = 'index.html', values = {}):
    from libmain import buildUserMenu
    userMenuValues = buildUserMenu()
    
    for key in userMenuValues:
        values[key] = userMenuValues[key]

    values['is_contributing_user'] = isContributingUser()
        
    temp = jinja_environment2.get_template(tname)
    handler.response.out.write(temp.render(values))
    return True
 
class ManageUsersHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            users_que = db.Query(datamodel.WikiUser).order('-join_date')
            users = users_que.fetch(50)
            administrators_que = db.Query(datamodel.AdministratorUser)
            administrators = administrators_que.fetch(50)
            contributing_users_que = db.Query(datamodel.ContributingUser)
            contributing_users = contributing_users_que.fetch(50)
            values["users"] = users
            values['administrators'] = administrators
            values['contributing_users'] = contributing_users
            doRender(self, 'ManageUsers.html', values)
        else:
            self.redirect('/')
    def post(self):
        from libuser import getUserEntity, newContributingUser, newAdministratorUser, isAdministratorUserByUID, isContributingUserByUID
        uid = self.request.get("auid")
        if uid is not "":
            if getUserEntity(uid) is not None and isAdministratorUserByUID(uid) is not True:
                admin = newAdministratorUser(getUserEntity(uid))
                admin.put()
        else:
            uid = self.request.get("cuid")
            if getUserEntity(uid) is not None and isContributingUserByUID(uid) is not True:
                contrib_user = newContributingUser(getUserEntity(uid))
                contrib_user.put()
                
                # send out a confirmation message
                aSubject = "Welcome to Wikitheoria"
                aReceiver = getUserEntity(uid).email
                aSender = "wikitheoria.public@gmail.com"
                aBody = """
                Congratulations! You are a contributor of Wikitheoria now.
                
                You could find some great tutorials on the index page.
                http://www.wikitheoria.com
                
                Sincerely,
                Wikitheoria Team
                """
                try:
                    mail.send_mail(sender = aSender, 
                                   to = aReceiver,
                                   subject = aSubject,
                                   body = aBody)
                except:
                    logging.error('Failed to send email -- Congrats contributor.')
                
        self.redirect('/administration/users/')

class ManageModulesHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            values["javascript"] = ["/static/js/jquery.js","/static/js/admin/module.js"]
            doRender(self, 'ManageModules.html', values)
        else:
            self.redirect('/')


class ManageTermsHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            values["javascript"] = ["/static/js/jquery.js","/static/js/admin/terms.js"]
            doRender(self, 'ManageTerms.html', values)
        else:
            self.redirect('/')

class ManagePrezisHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            values["javascript"] = ["/static/js/jquery.js"]
            
            preziObj = db.Query(datamodel.Prezis).filter('current_tag =', True).get()
            if preziObj:
                values['title1'] = preziObj.title_1
                values['pic1'] = preziObj.pic_1
                values['link1'] = '<' + preziObj.link_1
                
                values['title2'] = preziObj.title_2
                values['pic2'] = preziObj.pic_2
                values['link2'] = '<' + preziObj.link_2
                
                values['title3'] = preziObj.title_3
                values['pic3'] = preziObj.pic_3
                values['link3'] = '<' + preziObj.link_3
                
                values['title4'] = preziObj.title_4
                values['pic4'] = preziObj.pic_4
                values['link4'] = '<' + preziObj.link_4
            
            doRender2(self, 'ManagePrezis.html', values)
        else:
            self.redirect('/')
        
        
    def post(self):
        
        title1 = self.request.get("title1")
        pic1 = self.request.get("pic1")
        link1 = self.request.get("link1")
        if link1[0] == '<':
            link1 = link1[1:]
        else:
            pass
        
        title2 = self.request.get("title2")
        pic2 = self.request.get("pic2")
        link2 = self.request.get("link2")
        if link2[0] == '<':
            link2 = link2[1:]
        else:
            pass
        
        title3 = self.request.get("title3")
        pic3 = self.request.get("pic3")
        link3 = self.request.get("link3")
        if link3[0] == '<':
            link3 = link3[1:]
        else:
            pass
        
        title4 = self.request.get("title4")
        pic4 = self.request.get("pic4")
        link4 = self.request.get("link4")
        if link4[0] == '<':
            link4 = link4[1:]
        else:
            pass
        
        cKey = db.Query(datamodel.Prezis).filter('current_tag =', True).get().key()
        datamodel.Prezis(key=cKey, title_1=title1, pic_1=pic1, link_1=link1, title_2=title2, pic_2=pic2, link_2=link2, title_3=title3, pic_3=pic3, link_3=link3, title_4=title4, pic_4=pic4, link_4=link4, current_tag=True).put()
        
        self.redirect('/administration/')

class ManageNewsHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            values['javascript'] = ['/static/js/jquery-1.9.1.js',
                                    '/static/js/jquery-ui.js',
                                    '/static/js/plugins/wmd_stackOverflow/wmd.js', 
                                    '/static/js/plugins/wmd_stackOverflow/showdown.js']
            values['css'] = ['/static/js/jquery-ui.css',
                             '/static/js/plugins/wmd_stackOverflow/wmd.css']
            
            newsObject = db.Query(datamodel.News).get()
            
            if newsObject: 
                values['markdown'] = newsObject.newsMarkdown
                values['html'] = newsObject.newsHtml
            else:
                values['markdown'] = ""
                values['html'] = ""
                                       
            doRender(self, 'ManageNews.html', values)
        else:
            pass
        
        
    def post(self):   
        from libmain import parseMarkdown
        
        markdown = self.request.get("newsArea")
        newsObject = db.Query(datamodel.News).get()    
        if newsObject:
            newsObject.newsMarkdown = markdown
            newsObject.newsHtml = parseMarkdown(markdown)
            key = db.put(newsObject)
        else:
            news = datamodel.News(newsMarkdown = markdown, newsHtml = parseMarkdown(markdown))
            key = news.put()
        
        if key:
            self.redirect('/')
        else:
            logging.error('can not save news')        

class ManageWikiWordsHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            values['javascript'] = ['/static/js/jquery-1.9.1.js',
                                    '/static/js/jquery-ui.js',
                                    '/static/js/plugins/wmd_stackOverflow/wmd.js', 
                                    '/static/js/plugins/wmd_stackOverflow/showdown.js']
            values['css'] = ['/static/js/jquery-ui.css',
                             '/static/js/plugins/wmd_stackOverflow/wmd.css']
            
            wwObject = db.Query(datamodel.WikiWords).get()
            
            if wwObject: 
                values['markdown'] = wwObject.wwMarkdown
                values['html2'] = wwObject.wwHtml
            else:
                values['markdown'] = ""
                values['html2'] = ""
                                       
            doRender(self, 'ManageWikiWords.html', values)
        else:
            pass
        
        
    def post(self):   
        from libmain import parseMarkdown
        
        markdown = self.request.get("wwArea")
        
        wwObject = db.Query(datamodel.WikiWords).get()    
        if wwObject:
            wwObject.wwMarkdown = markdown
            wwObject.wwHtml = parseMarkdown(markdown)
            key = db.put(wwObject)
        else:
            ww = datamodel.WikiWords(wwMarkdown = markdown, wwHtml = parseMarkdown(markdown))
            key = ww.put()
        
        if key:
            self.redirect('/')
        else:
            logging.error('can not save wiki words')  
            
class SupportHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            values['javascript'] = ['/static/js/jquery.js',"/static/js/admin/support.js"]
            doRender(self, 'Support.html', values)
        else:
            self.redirect('/')
            
    def post(self):
        
        operation = self.request.get("operation")
        if operation == "cleanIndex":
            from google.appengine.api import search
            
            """Delete all the docs in the given index."""
            doc_index = search.Index(name='modIdx')
        
            # looping because get_range by default returns up to 100 documents at a time
            while True:
                # Get a list of documents populating only the doc_id field and extract the ids.
                document_ids = [document.doc_id
                                for document in doc_index.get_range(ids_only=True)]
                if not document_ids:
                    break
                # Delete the documents for the given ids from the Index.
                doc_index.delete(document_ids)
        elif operation == "cleanTerms":
            # clean all terms that are not associated with modules
#             moduleObjs = db.Query(datamodel.Module).fetch(limit=None)
#             linkedModules = [moduleObj.key for moduleObj in moduleObjs]
#             
#             modObjs = db.Query(datamodel.ModuleTerm).fetch(limit=None)
#             userfulTermList = []
#             for obj in modObjs:
#               try:
#                 userfulTermList.append(obj.term.word)
#               except:
#                 pass
#             
#             termObjs = db.Query(datamodel.Term).fetch(limit=None)
#             for termObj in termObjs:
#               if termObj.word not in userfulTermList:
#                 termObj.delete()
        
        else:
            pass
            
            
class PendingHandler(webapp2.RequestHandler):    
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            values['css'] = ['/static/css/jquery-impromptu.css']        
            values['javascript'] = ['/static/js/jquery-impromptu.min.js',"/static/js/admin/pending.js"]
            doRender(self, 'ManagePendings.html', values)
        else:
            self.redirect('/')      

class UploadHandler(webapp2.RequestHandler):    
    def get(self):
        if isAdministratorUser() is True:
            upload_url = blobstore.create_upload_url('/upload')
            values = dict()
            values["javascript"] = ["/static/js/jquery.js","/static/js/admin/pending.js"]
            blobs = blobstore.BlobInfo.all()
            values["blobs"] = blobs
            values["upload_url"] = upload_url
            doRender(self, 'UploadFiles.html', values)
        else:
            self.redirect('/administration/upload')      

class UploadHandler2(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        # 'file' is file upload field in the form
        upload_files = self.get_uploads('file')  
        blob_info = upload_files[0]
        self.redirect('/administration/')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)                        
        
class AdvancedHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
			users = db.Query(datamodel.NotifyFeedbackUser)
			values = dict()
			values["feedback_notify_group"] = users
			doRender(self, 'Advanced.html', values)
        else:
            self.redirect('/')
    def post(self):
    	arguments = self.request.arguments()
    	if "Name" in arguments:
        	try:
        	    user = datamodel.NotifyFeedbackUser(user = self.request.get("Name"),email = self.request.get("Email"))
        	    user.put()
        	except:
        	    logging.error('Unable to add user to notify group')
        	    #values = { 'error' : 'Failed to add user to notification list' }
        elif "remove_user" in arguments:
        	logging.error(self.request.get("remove_user"))
        else:
        	logging.error(str(arguments))
        self.redirect('/administration/advanced/')
        
class SanitizeHandler(webapp2.RequestHandler):
    def get(self):
        pass
    
    def post(self):
        pass
                
app = webapp2.WSGIApplication([('/upload', UploadHandler2),  
                               ('/serve/([^/]+)?', ServeHandler),                             
                               ('/administration/users/.*', ManageUsersHandler),
                               ('/administration/modules/.*', ManageModulesHandler),
                               ('/administration/terms/.*', ManageTermsHandler),
                               ('/administration/prezis/.*', ManagePrezisHandler),
                               ('/administration/news/.*', ManageNewsHandler),
                               ('/administration/wikiwords/.*', ManageWikiWordsHandler),
                               ('/administration/support/.*', SupportHandler),
                               ('/administration/advanced/.*', AdvancedHandler),
                               ('/administration/pending/.*', PendingHandler),
                               ('/administration/upload/.*', UploadHandler),
                               ('/administration', PendingHandler),
                               ('/administration/.*', PendingHandler)],
                              debug=True)
	
