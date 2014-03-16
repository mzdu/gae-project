from libmain import doRender, isCurrentUser, getUserInfo,getUrlResourceList
import logging
import datamodel

import webapp2
from google.appengine.ext import db

def getUserCount():
    countObject = db.Query(datamodel.Counter).filter("name = ", "users").get()
    if countObject:
        return countObject.count
    else:
        return 0

def newAdministratorUser(user):
    ''' @summary: Adds a WikiUser to the Administrator role
        @param user: A WikiUser Type
        @type user: WikiUser 
        @return: The newly created object in the AdministratorUser entity
        @rtype: AdministratorUser
    '''
    admin_user = datamodel.AdministratorUser(user = user)
    admin_user.put()
    return admin_user
    
def newContributingUser(user):
    ''' @summary: Adds a WikiUser to the Contributing role
        @param user: A WikiUser Type
        @type user: WikiUser 
        @return: The newly created object in the ContributingUser entity
        @rtype: ContributingUser
    '''
    contributing_user = datamodel.ContributingUser(user = user)
    contributing_user.put()
    return contributing_user

def isAdministratorUserByUID(uid):
    ''' @summary: Returns True or False if user is an administrator
        @param uid: String that is later typcasted to an int
        @type user: String 
        @return: True or False depending on user's rights
        @rtype: Boolean
    '''
    try:
        user = getUserEntity(uid)
        user_check = db.Query(datamodel.AdministratorUser).filter('user = ', user).get()
        if user_check:
            return True
        else:
            return False
    except:
        return False

def isContributingUserByUID(uid):
    ''' @summary: Returns True or False if user is a contributing user
        @param uid: String that is later typcasted to an int
        @type user: String 
        @return: True or False depending on user's rights
        @rtype: Boolean
    '''
    try:
        user = getUserEntity(uid)
        user_check = db.Query(datamodel.ContributingUser).filter('user = ', user).get()
        if user_check:
            return True
        else:
            return False
    except:
        return False

def isAdministratorUser():
    ''' @summary: Returns True or False depending on the current users rights
        @return: True or False if user is administrator
        @rtype: Boolean
    '''
    from main import getCurrentUserInfo
    user_info = getCurrentUserInfo()
    user_uid = int(user_info['uid'])
    user = getUserEntity(user_uid)
    try:
        user_check = db.Query(datamodel.AdministratorUser).filter('user =', user).get()
        if user_check:
            return True
        else:
            return False
    except:
        return False
    
def isContributingUser():
    ''' @summary: Returns True or False depending on the current users rights
        @return: True or False if user is a contributing user
        @rtype: Boolean
    '''
    from main import getCurrentUserInfo
    user_info = getCurrentUserInfo()
    try:
        user_uid = int(user_info['uid'])
        user = getUserEntity(user_uid)
        user_check = db.Query(datamodel.ContributingUser).filter('user =', user).get()
        if user_check:
            return True
        else:
            return False
    except:
        return False    

def getUserEntity(uid):
    ''' @summary: Returns the User object referenced by the uid
        @param uid: Pointer to current handler(self)
        @type uid: String 
        @return: A User object from the datastore
        @rtype: User
    '''
    try:
        uid = int(uid)
    except:
        return None
    user = db.Query(datamodel.WikiUser).filter('uid =', uid).get()
    if user:
        return user
    else: 
        return -1


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
        from main import getLoginUrl
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

