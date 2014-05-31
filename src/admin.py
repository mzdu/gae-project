from libmain import doRender
import logging
import datamodel

import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import db
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
                values['link1'] = '<' + preziObj.link_1
                
                values['title2'] = preziObj.title_2
                values['link2'] = '<' + preziObj.link_2
                
                values['title3'] = preziObj.title_3
                values['link3'] = '<' + preziObj.link_3
                
                values['title4'] = preziObj.title_4
                values['link4'] = '<' + preziObj.link_4
            
            doRender2(self, 'ManagePrezis.html', values)
        else:
            self.redirect('/')
        
        
    def post(self):
        
        title1 = self.request.get("title1")
        link1 = self.request.get("link1")
        if link1[0] == '<':
            link1 = link1[1:]
        else:
            pass
        
        title2 = self.request.get("title2")
        link2 = self.request.get("link2")
        if link2[0] == '<':
            link2 = link2[1:]
        else:
            pass
        
        title3 = self.request.get("title3")
        link3 = self.request.get("link3")
        if link3[0] == '<':
            link3 = link3[1:]
        else:
            pass
        
        title4 = self.request.get("title4")
        link4 = self.request.get("link4")
        if link4[0] == '<':
            link4 = link4[1:]
        else:
            pass
        
        cKey = db.Query(datamodel.Prezis).filter('current_tag =', True).get().key()
        datamodel.Prezis(key=cKey, title_1=title1, link_1=link1, title_2=title2, link_2=link2, title_3=title3, link_3=link3, title_4=title4, link_4=link4, current_tag=True).put()
        
        self.redirect('/administration/')
        
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
        
class SanitizeHandler(webapp2.RequestHandler):
    def get(self):
        pass
    
    def post(self):
        pass
                
app = webapp2.WSGIApplication([                               
                               ('/administration/users/.*', ManageUsersHandler),
                               ('/administration/modules/.*', ManageModulesHandler),
                               ('/administration/terms/.*', ManageTermsHandler),
                               ('/administration/prezis/.*', ManagePrezisHandler),
                               ('/administration/support/.*', SupportHandler),
                               ('/administration/advanced/sanitize/', SanitizeHandler),
                               ('/administration/advanced/.*', AdvancedHandler),
                               ('/administration', SupportHandler),
                               ('/administration/.*', SupportHandler)],
                              debug=True)
	