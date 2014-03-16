import datamodel
 
import jinja2
import os
import logging

from google.appengine.ext import db
from google.appengine.api import mail

################ Render a Page with Jinja2 Template #########################

jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'))

def doRender(handler, tname = 'index.html', values = {}):
    
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

############################# Markdown Module #############################

def parseMarkdown(x):
    import markdown
 
    html = markdown.markdown(x)
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
    
    