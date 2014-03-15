from libmain import createNewUID
from libuser import getCurrentUserEntity
import datamodel
import logging
from google.appengine.ext import db

#insert the data into datastore
def newModule(title, keywords, markdown, tscope, propositions, derivations, tevidence, publish):
    ''' @summary: Creates a new module entity 
        @param title, keywords, markdown, scope, propositions, derivations, evidence, publish
        @type String
        @return: Returns the uid if successful, else -1
        @rtype: integer
    '''
    from libmain import parseMarkdown
     
    uid = createNewUID("modulesUID")
    if uid == 0:
        return -1
    else:
        # getCurrentUserEntity() is loaded from libmain
        user = getCurrentUserEntity()   
         
        try:
            if publish == "false": 
                module = datamodel.Module(title = title, 
                                          keywords = keywords, 
                                          theoryMarkdown = markdown,
                                          theoryHtml = parseMarkdown(markdown),
                                          uid = uid, version = 0, 
                                          scope = tscope, 
                                          propositions = propositions,
                                          derivations = derivations,
                                          evidence = tevidence,
                                          contributor = user,
                                          published = False, current = True)
            else:
                module = datamodel.Module(title = title, 
                                          keywords = keywords, 
                                          theoryMarkdown = markdown,
                                          theoryHtml = parseMarkdown(markdown),
                                          uid = uid, version = 1, 
                                          scope = tscope, 
                                          propositions = propositions,
                                          derivations = derivations,
                                          evidence = tevidence,
                                          contributor = user,
                                          published = True, current = True)
                createNewUID("modules") #increments the overall module counter once the module is published
            modKey = module.put()
            return modKey
        except:
            logging.error('Failed to create module. Module number uid:' + str(uid))
            return -1


def getUnpublishedModules():
    user = getCurrentUserEntity()
    modules = db.Query(datamodel.Module).filter('contributor  =', user).filter('published =', False).fetch(20)
    return modules

def publishModule(uid):
    module = db.Query(datamodel.Module).filter('uid  =', uid).get()
    module.published = True
    db.put(module)
