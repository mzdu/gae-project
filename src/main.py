#main.py
#Wikitheoria Project
#@author: Jonathan Mayhak & Jason Rikard

import os
import datamodel
import logging

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from django.template.defaultfilters import slugify 
from google.appengine.api import mail

def getContributionCount():
    ''' @summary: Returns the count of articles, modules, and module versions
        @return: an integer representing total contributions to wikitheoria
        @rtype: integer
    '''
    from articles import getArticleCount
    from modules import getModuleCount #, getModuleVersionCount
    count = 0
    count += getArticleCount()
    count += getModuleCount()
    #count += getModuleVersionCount()
    return count


def sendFeedbackEmail(aSender, aSubject, aBody):
    ''' @summary: Sends an email to all authorized users of a feedback response
        @param aSender: the email address of the sender
        @type aSender: email property
        @param aSubject: the subject of the email
        @type aSubject: string
        @param aBody: the body of the email
        @type aBody: string
        @return: status of definition (-1: fail, >1: number of send messages)
        @rtype: integer
    '''
    num = 0
    try:
        users = db.Query(datamodel.NotifyFeedbackUser).fetch(20)
        for user in users:
            mail.send_mail(sender=aSender,
                           to=user.user + " <" + user.email + ">",
                           subject=aSubject,
                           body=""+ aBody + "")
            num = num + 1
    except:
        logging.error('Unable to send email: ' + aSender + " " + user.email + " " + aSubject + " " + aBody)
        num = -1
    return num

def autoIncrement(key):
    ''' @summary: Increments a particular counter entity specified by the key
        @param key: The unique key that describes the Counter entity to be incremented
        @type key: key object from datastore
        @return: returns the current count + 1 
        @rtype: integer
    '''
    counter = db.get(key)
    counter.count += 1
    counter.put()
    return counter.count

def autoDecrement(key):
    ''' @summary: Decrements a particular counter entity specified by the key
        @param key: The unique key that describes the Counter entity to be decremented
        @type key: key object from datastore
        @return: returns the current count - 1
        @rtype: integer
    '''
    counter = db.get(key)
    counter.count -= 1
    counter.put()
    return counter.count

def createNewUID(name):
    ''' @summary: Attempts to create a uid for particular entity type. The entity type is identified by the name.
        @param name: The name of the entity to be counted
        @type name:  String
        @return: Returns an integer if the transaction is successful. Returns -1 if failed
        @rtype: integer
    '''
    #get the key for user counter
    counter = db.Query(datamodel.Counter).filter('name =', name).get()
    #If entity doesn't exist in the Counter entity group, create it.
    if not counter:
        counterKey = datamodel.Counter(name = name, count = 0).put()
    else:
        counterKey = counter.key()
    try:
        uid = db.run_in_transaction(autoIncrement, counterKey)
        return uid
    except db.TransactionFailedError:
        logging.error('Failed to get auto increment value during transaction and retries')
        return -1
    
def decrementCounter(name):
    ''' @summary: Similar to createNewUID(); Attempts to decrement the counter for a particular entity type. The entity type is identified by the name.
        @param name: The name of the entity to be counted
        @type name:  String
        @return: Returns an integer if the transaction is successful. Returns -1 if failed
        @rtype: integer
    '''
    #get the key for user counter
    counter = db.Query(datamodel.Counter).filter('name =', name).get()
    #If entity doesn't exist in the Counter entity group, create it.
    if not counter:
        counterKey = datamodel.Counter(name = name, count = 0).put()
    else:
        counterKey = counter.key()
    try:
        uid = db.run_in_transaction(autoDecrement, counterKey)
        return uid
    except db.TransactionFailedError:
        logging.error('Failed to get auto decrement during transaction and retries')
        return -1
  
#handle logged in users status and information. If there is a current user, call getUserInfo()
def buildUserMenu():
    ''' @summary: Returns values that are used by the _base Django template relating to the user
        @rtype: Dictionary
    '''
    user = getGoogleUserObject()
    userInfo = dict()
    
    if user:
        userInfo = getCurrentUserInfo()
        #If this is the first time logging in, firtTimeLogin() is called to create a new entity
        if userInfo['isUser'] == 'False':
            firstTimeLogin(user)
            userInfo = getCurrentUserInfo()
    else:
        userInfo['login_url'] =  getLoginUrl()
    return userInfo
    

def doRender(handler, tname = 'index.html', values = {}):
    ''' @summary: Renders a page using Django templates
        @param handler: Pointer to calling handler
        @type callingUserName:  String
        @param tname: Template file name
        @type callingUserName:  String
        @param values: Variables to be passed into the Django template
        @type values:  Dictionary
        @return: Return True if template file exists, else false;
        @rtype: Boolean
    '''
    from users import getUserCount
    from articles import getArticleCount
    from modules import getModuleCount
    
    temp = os.path.join(os.path.dirname(__file__), 'templates/' + tname)
    if not os.path.isfile(temp):
        return False
    
    userMenuValues = buildUserMenu()
    for key in userMenuValues:
        values[key] = userMenuValues[key]
    
    values["num_users"] = getUserCount()
    values["num_articles"] = getArticleCount()
    values["num_modules"] = getModuleCount()
    values["num_contributions"] = getContributionCount()

    outstr = template.render(temp, values)
    handler.response.out.write(outstr)
    return True

def firstTimeLogin(user):
    ''' @summary: On the first login, create a newWikiUser entity
        @param user: Current user object
        @type user:  Object
        @return: Return True if creating a new user is successful
        @rtype: Boolean
    '''
    uid = createNewUID('users')
        
    alias = user.nickname()
    #if alias is an email, remove @example.com
    if alias.find('@'):
        temp = alias.split('@')
        alias = temp[0]
    try:
        newWikiUser(user.user_id(), alias, user.email(), uid)
        return True
    except:
        logging.error('FirstTimeLogin failed to create a new user')
        return False

def isCurrentUser(uid):
    ''' @summary: Compare current logged in user with callingUserName; Verify user credentials
        @param callingUserName: UserName to compare against
        @type callingUserName:  String
        @return: Return True if the current logged in user is equal to callingUserName
        @rtype: Boolean
    '''
    userInfo = getCurrentUserInfo()
    if userInfo['isUser'] == 'True':
        if userInfo['uid'] == uid:
            return True
    else:
        return False
    
def isLoggedIn():
    ''' @summary: Checks for an authenticated user bases on the Google User API
        @return: Return True if there is a current authenticated user
        @rtype: Boolean
    '''
    if getGoogleUserObject():
        return True
    else:
        return False

def getCurrentUserInfo():
    ''' @summary: Returns logged in user information used for building the user navigation. If user is not found in datastore, returns false
        @return: If user exists: A dictionary of strings (alias, user_name, logout_url, user_profile_url, isUser = true)
        @return: If user doesn't exists: A dictionary(isUser = False) 
        @rtype: Dictionary
    '''
    user = getGoogleUserObject()
    currentUserDict = dict();
    if not user:
        currentUserDict['isUser'] = 'False'
        return currentUserDict
    userID = user.user_id()
    
    que = db.Query(datamodel.WikiUser)
    que = que.filter('user_id =', userID)
    userInfo = que.get()
    
    #If user is found in datastore return info, else create new user
    if userInfo:
        currentUserDict['alias'] = userInfo.alias
        currentUserDict['alias_slug'] = slugify(userInfo.alias)
        currentUserDict['uid'] = userInfo.uid
        currentUserDict['user_name'] = userInfo.user_name
        currentUserDict['logout_url'] = getLogoutUrl()
        currentUserDict['email'] = userInfo.email
        currentUserDict['user_profile_url'] = '/users/' + str(currentUserDict['uid']) + '/' + slugify(userInfo.alias)
        currentUserDict['isUser'] = 'True'
        return currentUserDict
    else:
        currentUserDict['isUser'] = 'False'
        return currentUserDict
    
def getGoogleUserObject():
    ''' @summary: Returns current Google User Object
        @rtype: Google User Object
    '''
    user = users.get_current_user()
    if user:
        return user
    else:
        return False
    
def getLoginUrl():
    ''' @summary: Returns URL to be used for logging in
        @rtype: String
    '''
    return users.create_login_url("/")

def getLogoutUrl():
    ''' @summary: Returns URL to be used for logging out
        @rtype: String
    '''
    return users.create_logout_url("/")

def getCurrentUserEntity():
    ''' @summary: Finds and returns the currently logged in user's user entity from the datastore
        @rtype: userEntity Object
    '''
    user = getGoogleUserObject()
    que = db.Query(datamodel.WikiUser)
    que = que.filter('user_id =', user.user_id())
    userEntity = que.get()
    return userEntity
    
def getUrlResource(handler):
    ''' @summary: Takes the current handler and manipulates the path to return the last resource of a URL; http://example.com/users/jason. Returns jason (string)
        @param handler: Pointer to current handler(self)
        @return: Return string of last resource in a URL
        @rtype: String
    '''
    from urlparse import urlparse
    from posixpath import basename
    url = handler.request.path
    parse_object = urlparse(url)
    resource = basename(parse_object.path)
    return resource

def getUrlResourceList(handler):
    ''' @summary: Takes the current handler and manipulates the path to return a list of all the resources after the .com
        @param handler: Pointer to current handler(self)
        @return: Return a list of resource strings found in a URL
        @rtype: list
    '''
    from urlparse import urlparse
    url = handler.request.path
    parse_object = urlparse(url)
    resourceList = parse_object.path.split('/')
    resourceList.pop(0) #Remove empty list item
    return resourceList

def getUserInfo(uid):
    ''' @summary: Returns a dictionary of public values that are used to populate a user profile
        @param uid: Unique identifier in datastore for User object
        @type uid: String 
        @return: A dictionary of values related to the user entity
        @rtype: list
    '''
    profile = dict();
    
    que = db.Query(datamodel.WikiUser)
    que = que.filter('uid =', int(uid))
    userInfo = que.get()
    
    #If user is found in datastore return info, else create new user
    if userInfo:
        profile['alias_general'] = userInfo.alias
        profile['real_name_general'] = userInfo.real_name
        profile['user_id_general'] = userInfo.user_id
        if userInfo.birthday:
            profile['birthday_general'] = userInfo.birthday.strftime('%m/%d/%Y')
        profile['email_general'] = userInfo.email
        profile['join_date_general'] = userInfo.join_date
        profile['location_general'] = userInfo.location
        profile['organization_general'] = userInfo.organization
        profile['user_name_general'] = userInfo.user_name
        profile['about_general'] = userInfo.about
        profile['is_user_general'] = 'True'
        return profile
    else:
        profile['error'] = str(uid) + ' is not a user'
        profile['is_user_general'] = 'False'
        return profile 
    


def newWikiUser(userID, userName, email, uid): 
    ''' @summary: Creates a new WikiUser entity in the datastore
        @param userID: Unique numeric string that Google provides
        @type userID: String 
        @param userName: Unique user name
        @type userName: String
        @param uEmail: User's email address
        @type uEmail: String  
    '''  
    newUser = datamodel.WikiUser(user_name = userName, user_id = userID, alias = userName, email = email, uid = uid)
    try:
		from users import newContributingUser
		user = newUser.put()
    except:
        logging.debug()
        newUser.put()
    if uid == 1:
        # The first user to signup is defaulted as an administrator/contributor
        from users import newAdministratorUser
        newAdministratorUser(user)
        
def parseMarkdown(x):
    import markdown

    html = markdown.markdown(x)
    if html:
        return html
    else:
        return 'none'
        
class HelpHandler(webapp.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, '/support/help.html', values)
        
class AboutHandler(webapp.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, 'about.html', values)

class ContributeHandler(webapp.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, '/contribute.html', values)

class ContactHandler(webapp.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, '/feedback.html', values)

class FeedbackHandler(webapp.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, '/feedback.html', values)
    def post(self):
        userInfo = getCurrentUserInfo()
        aSubject = userInfo['user_name'] + " left feedback for The Wikitheoria Project development site"
        aBody = self.request.get("body")
        sendFeedbackEmail(userInfo["email"], aSubject, aBody)
        self.redirect('/')

class JoinHandler(webapp.RequestHandler):
    def get(self):
        values = dict()
        userInfo = getCurrentUserInfo()
        if userInfo['isUser'] is 'True':
            values = userInfo
        doRender(self, '/join.html', values)
    def post(self):
        email = self.request.get("email")
        name = self.request.get("name")
        note = self.request.get("note")
        aSubject = name + " would like to become a member of Wikitheoria -- Needs Authorization"
        aBody = "name: " + name + "\nEmail: " + email + "\n\n" + note
        sendFeedbackEmail(email, aSubject, aBody)
        self.redirect('/')

class MainPageHandler(webapp.RequestHandler):
    def get(self):
        values = dict()
        from modules import getFeaturedModule
        from articles import getFeaturedArticle
        from google.appengine.api import memcache
        
        #import markdown
        #logging.error(markdown.markdown("blahbalhba"))
        
        #########Memcache featured module
        featuredModule = memcache.get("featuredModule") #@UndefinedVariable
        if featuredModule is None:
            featuredModule = getFeaturedModule()
            if not memcache.add("featuredModule", featuredModule, 60): #@UndefinedVariable
                logging.error("Memcache set failed.")
        #########end Memcache featured module
        
        #########Memcache featured article
        featuredArticle = memcache.get("featuredArticle") #@UndefinedVariable
        if featuredArticle is None:
            featuredArticle = getFeaturedArticle()
            if not memcache.add("featuredArticle", featuredArticle, 60): #@UndefinedVariable
                logging.error("Memcache set failed.")
        #########end Memcache featured article
        
        if featuredModule.has_key('error'):
                values['module_error'] = 'No module currently featured'
        else:
            for key in featuredModule:
                values[key] = featuredModule[key]
                
        if featuredArticle.has_key('error'):
            values['article_error'] = 'No article currently featured'
        else:
            for key in featuredArticle:
                values[key] = featuredArticle[key]
        

        doRender(self, 'index.html', values)
        

def main():
    application = webapp.WSGIApplication([
                                          ('/help.*', HelpHandler),
                                          ('/about.*', AboutHandler),
                                          ('/contribute.*', ContributeHandler),
                                          ('/feedback.*', FeedbackHandler),
                                          ('/contact.*', ContactHandler),
                                          ('/join.*', JoinHandler),
                                          ('/.*', MainPageHandler)
                                          ],debug = True)
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()

