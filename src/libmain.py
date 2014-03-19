import datamodel
 
import jinja2
import os
import logging

from markdown import markdown

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import mail

################ Render a Page with Jinja2 Template #########################

jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'))

def doRender(handler, tname = 'index.html', values = {}):
    
    userMenuValues = buildUserMenu()
    
    for key in userMenuValues:
        values[key] = userMenuValues[key]
    
    from libuser import isContributingUser
    values['is_contributing_user'] = isContributingUser()
    temp = jinja_environment.get_template(tname)
    handler.response.out.write(temp.render(values))
    return True

########################### Key Related ########################################

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
  
############################# Markdown Module #############################

def parseMarkdown(x):
 
    html = markdown(x)
    if html:
        return html
    else:
        return 'none'

############################### URL Related ##################################

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
    # Remove the possible empty elements from both sides
    if resourceList[0] == '':
        resourceList.pop(0)
    if resourceList[-1] == '':
        resourceList.pop()
        
    return resourceList
    


####################### Send Email ##########################################
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

#################################################################################

    
def buildUserMenu():
    ''' @summary: Returns values that are used by the _base Django template relating to the user
        @rtype: Dictionary
    '''
    from libuser import getGoogleUserObject, getCurrentUserInfo, getLoginUrl, firstTimeLogin
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
    
    
    
    ################################# Some Toolkit ########################
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
    
    
    
    
    
    
    
        