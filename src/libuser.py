import datamodel
import logging

from libmain import createNewUID

from google.appengine.ext import db
from google.appengine.api import users

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


def isContributingUser():
    ''' @summary: Returns True or False depending on the current users rights
        @return: True or False if user is a contributing user
        @rtype: Boolean
    '''
    
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
    

############################################################
# loaded by doRender()
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



def getUserCount():
    countObject = db.Query(datamodel.Counter).filter("name = ", "users").get()
    if countObject:
        return countObject.count
    else:
        return 0

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

###################################################

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
    
def getGoogleUserObject():
    ''' @summary: Returns current Google User Object
        @rtype: Google User Object
    '''
    user = users.get_current_user()
    if user:
        return user
    else:
        return False    
    
def getCurrentUserEntity():
    ''' @summary: Finds and returns the currently logged in user's user entity from the datastore
        @rtype: userEntity Object
    '''
    user = getGoogleUserObject()
    que = db.Query(datamodel.WikiUser)
    que = que.filter('user_id =', user.user_id())
    userEntity = que.get()
    
    logging.info("userEntity is", userEntity)
    
    return userEntity

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
    # not empty, get user info
    if userInfo:
        currentUserDict['alias'] = userInfo.alias
        currentUserDict['alias_slug'] = userInfo.alias
        currentUserDict['uid'] = userInfo.uid
        currentUserDict['user_name'] = userInfo.user_name
        currentUserDict['logout_url'] = getLogoutUrl()
        currentUserDict['email'] = userInfo.email
        currentUserDict['user_profile_url'] = '/users/' + str(currentUserDict['uid']) + '/' + userInfo.alias
        currentUserDict['isUser'] = 'True'
        return currentUserDict
    #empty, isUser=false
    else:
        currentUserDict['isUser'] = 'False'
        return currentUserDict    

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
        user = newUser.put()
    except:
        logging.debug()
        newUser.put()
    if uid == 1:
        # The first user to signup is defaulted as an administrator/contributor
        newAdministratorUser(user)    
        
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


