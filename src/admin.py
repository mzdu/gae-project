from main import doRender
import logging
import datamodel

import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from users import isContributingUser, isAdministratorUser
 
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
        from users import getUserEntity, newContributingUser, newAdministratorUser, isAdministratorUserByUID, isContributingUserByUID
        uid = self.request.get("auid")
        if uid is not "":
            if getUserEntity(uid) is not None and isAdministratorUserByUID(uid) is not True:
                admin = newAdministratorUser(getUserEntity(uid))
                admin.put()
        else:
            uid = self.request.get("cuid")
            logging.error(uid)
            if getUserEntity(uid) is not None and isContributingUserByUID(uid) is not True:
                contrib_user = newContributingUser(getUserEntity(uid))
                contrib_user.put()
        self.redirect('/administration/users/')

class ManageModulesHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            values["javascript"] = ["/static/js/jquery.js","/static/js/admin/module.js"]
            doRender(self, 'ManageModules.html', values)
        else:
            self.redirect('/')

class ManageArticlesHandler(webapp2.RequestHandler):
	def get(self):
		if isAdministratorUser() is True:
			values = dict()
			values["javascript"] = ["/static/js/jquery.js","/static/js/admin/AdvancedPage.js"]
			doRender(self, 'ManageArticles.html', values)
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
        
class SupportHandler(webapp2.RequestHandler):
    def get(self):
        if isAdministratorUser() is True:
            values = dict()
            doRender(self, 'Support.html', values)
        else:
            self.redirect('/')
        
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
                
app = webapp2.WSGIApplication([
										('/administration/users/.*', ManageUsersHandler),
										('/administration/modules/.*', ManageModulesHandler),
										('/administration/articles/.*', ManageArticlesHandler),
										('/administration/terms/.*', ManageTermsHandler),
										('/administration/support/.*', SupportHandler),
										('/administration/advanced/.*', AdvancedHandler),
										('/administration', SupportHandler),
										('/administration/.*', SupportHandler)],
										debug=True)
	