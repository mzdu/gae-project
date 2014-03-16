from libmain import doRender, getUrlResourceList
from libuser import isCurrentUser, isContributingUser, getUserInfo, getUserEntity
import logging
import datamodel

import webapp2
from google.appengine.ext import db


class EditUserHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        path = getUrlResourceList(self)
        try:
            uid = int(path[2])
        except:
            values['error'] = 'Invalid character after /user/'
            doRender(self, 'user.html', values) 
            return
        # values['user_name_general'] = userName
        if isCurrentUser(uid):
            userInfo = getUserInfo(uid)
            for key in userInfo:
                values[key] = userInfo[key] 
            doRender(self, 'editUser.html', values)   
        else:
            doRender(self, 'user.html', values) 
 
           
    def post(self):
        path = getUrlResourceList(self)
        values = dict()
        try:
            uid = int(path[2])
        except:
            values['error'] = 'Invalid character after /user/'
            doRender(self, 'user.html', values) 
            return
        
        values['user_name_general'] = self.request.get("alias")
        values['alias_general'] = self.request.get("alias")
        values['real_name_general'] = self.request.get("real_name")
        values['organization_general'] = self.request.get("organization")
        values['location_general'] = self.request.get("location")
        values['email_general'] = self.request.get("email")
        values['about_general'] = self.request.get("about")
        if isCurrentUser(uid):  
            from datetime import datetime
            from datamodel import WikiUser
            que = db.Query(WikiUser)
            que = que.filter('uid =', uid)
            userObject = que.get()

            if userObject:
                userObject.alias = values['alias_general']
                userObject.real_name = values['real_name_general']
                userObject.organization = values['organization_general']
                userObject.location = values['location_general']
                userObject.email = values['email_general']
                userObject.about = values['about_general']
               
                if not self.request.get("birthday") == '':
                    values['birthday_general'] = self.request.get("birthday")
                    try:
                        date_object = datetime.strptime(values['birthday_general'], '%m/%d/%Y')
                        userObject.birthday = date_object
                    except:
                        values['error'] = "Birthday was not formatted correctly"
                    
                try:
                    db.put(userObject)
                except:
                    logging.error('Failed to update user profile' + str(uid))
            else:
                logging.error('No user found')
            doRender(self, 'user.html', values) 
           
    
    
    
#user handler
class UserHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        path = getUrlResourceList(self)
        try:
            uid = int(path[1])
        except:
            values['error'] = 'Invalid character after /user/'
            doRender(self, 'user.html', values) 
            return
        
        if isCurrentUser(uid):
            values['is_current_user'] = 'True'
            userObject = getUserEntity(uid)
            values['contributed_modules'] = db.Query(datamodel.Module).filter('contributor =', userObject)
        
        userInfo = getUserInfo(uid)
        for key in userInfo:
            values[key] = userInfo[key]
        doRender(self, 'user.html', values)       
        
class DefaultUserHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        from libuser import getLoginUrl
        if isContributingUser() is True:
            values['can_contribute'] = 'True'
        values["login_url"] = getLoginUrl()
        users = db.Query(datamodel.WikiUser).order('-join_date').fetch(10)
        values["ten_newest_users"] = users
        doRender(self, 'userDefault.html', values)    
    
app = webapp2.WSGIApplication(
                                         [('/users/edit/.*', EditUserHandler),
                                          ('/users', DefaultUserHandler),
                                          ('/users/', DefaultUserHandler),
                                          ('/users/.*', UserHandler)],
                                          debug=True)

