from libmain import createNewUID
from libuser import getCurrentUserEntity
import datamodel
import logging
from google.appengine.ext import db
from google.appengine.ext.db import Key

############################ add, update & get a module ########################################

# add a new module into datastore
def newModule(title, keywords, markdown, tscope, propositions, derivations, tevidence, publish):
    ''' @summary: Creates a new module entity 
        @param title, keywords, markdown, scope, propositions, derivations, evidence, publish
        @type String
        @return: Returns the uid if successful, else -1, returns modkey and uid
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
            return modKey, uid
        except:
            logging.error('Failed to create module. Module number uid:' + str(uid))
            return -1

# update a module
#def updateModule(uid, title, meta_theory, markdown, scope, propositions, discipline, publish):
def updateModule(uid, title, keywords, markdown, tscope, propositions, derivations, tevidence, publish, nVersion=0, mVersion=0):
    ''' @summary: Updates a module entity 
        @param uid, title, meta_theory, scope, propositions, discipline
        @type String
        @return: Returns the uid if successful, else -1
        @rtype: integer
    '''
    from libmain import parseMarkdown
    user = getCurrentUserEntity()
    
    nVersion = int(nVersion)
    mVersion = int(mVersion)
    
    logging.info('nVer is' + str(nVersion) + ' mVer is' + str(mVersion))
    
    if nVersion == mVersion and nVersion == 0:
        logging.info('version 0, unpublished')
        
        oldModule = getModuleEntity(uid)
        module = oldModule
        module.title = title
        module.keywords = keywords
        module.theoryMarkdown = markdown
        module.theoryHtml = parseMarkdown(markdown)
        module.scope = tscope
        module.propositions = propositions
        module.derivations = derivations
        module.evidence = tevidence
 
        # keep the version0 unpublished module have only one copy
        module.published = False
        module.current = True
        module.version = 0
        key = db.put(module)
        return key 


    elif nVersion == mVersion and nVersion > 0:
        logging.info('editing a published current module')
        oldModule = getModuleEntity(uid)
         
         
        if oldModule.version > 0:
            tempVersion = oldModule.version + 1
             
            try:
                uid = int(uid)
            except:
                return -1 
                 
            if tempVersion == -1:
                return -1
            else:
                try:
                    moduleRevision = datamodel.Module(version = tempVersion,
                                                      title = title, 
                                                      keywords = keywords, 
                                                      theoryMarkdown = markdown,
                                                      theoryHtml = parseMarkdown(markdown),
                                                      uid = uid,  
                                                      scope = tscope, 
                                                      propositions = propositions,
                                                      derivations = derivations,
                                                      evidence = tevidence,
                                                      contributor = user,
                                                      current = False, published = False)
                    key = moduleRevision.put()
                    return key
                except:
                    logging.error('Failed to create module. Module number uid:' + str(uid))
                    return -1            
 
        else:
            pass        
        


    elif mVersion - nVersion == 1:
        logging.info('keep on editing an unpublished module')
        
        oldModule = getUnpublishedModuleEntity(uid)
        
        module = oldModule
        module.title = title
        module.keywords = keywords
        module.theoryHtml = parseMarkdown(markdown)
        module.theoryMarkdown = markdown
        module.scope = tscope
        module.propositions = propositions
        module.derivations = derivations
        module.evidence = tevidence
         
        module.published = False
        module.current = False
         
        key = db.put(module)
        return key        
    else:
        logging.info('editing a module')
#
#     
#     # published
#     if publish == "true":
#         # current is true; get a new copy
#         oldModule = getModuleEntity(uid)
#         
#         
#         if oldModule.version > 0:
#             tempVersion = oldModule.version + 1
#             
#             try:
#                 uid = int(uid)
#             except:
#                 return -1 
#                 
#             if tempVersion == -1:
#                 return -1
#             else:
#                 try:
#                     moduleRevision = datamodel.Module(version = tempVersion,
#                                                       title = title, 
#                                                       keywords = keywords, 
#                                                       theoryMarkdown = markdown,
#                                                       theoryHtml = parseMarkdown(markdown),
#                                                       uid = uid,  
#                                                       scope = tscope, 
#                                                       propositions = propositions,
#                                                       derivations = derivations,
#                                                       evidence = tevidence,
#                                                       contributor = user,
#                                                       current = False, published = False)
#                     moduleRevision.put()
#                     return moduleRevision
#                 except:
#                     logging.error('Failed to create module. Module number uid:' + str(uid))
#                     return -1            
# 
#         else:
#             pass

#     # not published; save the data under current user    
#     elif publish == "false":
#         oldModule = getUnpublishedModuleEntity(uid)
#         
#         
#         if oldModule.version == 0:
#             module = oldModule
#             module.title = title
#             module.keywords = keywords
#             module.theoryMarkdown = markdown
#             module.theoryHtml = parseMarkdown(markdown)
#             module.scope = tscope
#             module.propositions = propositions
#             module.derivations = derivations
#             module.evidence = tevidence
#     
#             # keep the version0 unpublished module have only one copy
#             module.published = False
#             module.current = True
#             module.version = 0
#             key = db.put(module)
#             return key            
#         
#         
#         elif oldModule.version > 0:
#             module = oldModule
#             module.title = title
#             module.keywords = keywords
#             module.theoryHtml = parseMarkdown(markdown)
#             module.theoryMarkdown = markdown
#             module.scope = tscope
#             module.propositions = propositions
#             module.derivations = derivations
#             module.evidence = tevidence
#             
#             module.published = False
#             module.current = False
#             
#             key = db.put(module)
#             return key
#         
#         else:
#             pass
  
#     else:
#         pass    


# get a module
def getModule(uid):
    ''' @summary: Populates a dictionary with a particular module's values from the datastore for use in a Django template
        @param uid: The uid that describes the module to get from the datastore
        @type uid: String (later typecasted to an int)
        @return: Returns a dictionary containing module entity data
        @rtype: dictionary
    '''
    values = dict()
    try:
        uid = int(uid)
    except:
        values['error'] = 'Module id\'s are numeric. Please check the URL.'
        return values
    que = db.Query(datamodel.Module).filter('uid =', uid).filter('current =', True)
    moduleObject = que.get()
    if moduleObject:
        values['module_title_general'] = moduleObject.title
        values['module_keywords_general'] = moduleObject.keywords        
        values['module_contrubutor_general'] = moduleObject.contributor
        values['module_last_update_general'] = '%02d/%02d/%04d' % (moduleObject.last_update.month, moduleObject.last_update.day, moduleObject.last_update.year)
        values['module_scope_general'] = moduleObject.scope
        values['module_propositions_general'] = moduleObject.propositions
        values['module_derivations_general'] = moduleObject.derivations
        values['module_evidence_general'] = moduleObject.evidence
        
        values['module_url'] = '/modules/' + str(moduleObject.uid) + '/' + str(moduleObject.version) + '/' + moduleObject.title
        values['module_edit_url'] = '/module/edit/' + str(moduleObject.uid) + '/' + moduleObject.title
        
        
        values['module_uid'] = moduleObject.uid
        
        
        values['module_version'] = 1
        values['module_published'] = moduleObject.published
        values['markdown'] = moduleObject.theoryMarkdown
        values['html'] = moduleObject.theoryHtml
        
        values['terms'] = db.Query(datamodel.ModuleTerm).filter('module =', moduleObject)
    else:
        values['error'] = 'Module does not exist'
    return values

####################################################################################################

def getUnpublishedModules():
    user = getCurrentUserEntity()
    modules = db.Query(datamodel.Module).filter('contributor  =', user).filter('published =', False).order('-last_update').fetch(200)
    return modules

def publishModule(uid):
    module = db.Query(datamodel.Module).filter('uid  =', uid).get()
    module.published = True
    db.put(module)

def getModuleEntity(uid):
    ''' @summary: Returns a Module object from the datastore
        @param uid: The uid that describes the module to get from the datastore
        @type uid: String (later typecasted to an int)
        @return: Returns a Module object
        @rtype: Module
    '''
    try:
        uid = int(uid)
    except:
        return None
    que = db.Query(datamodel.Module).filter('uid =', uid).filter('current =', True)
    moduleObject = que.get()
    if moduleObject:
        return moduleObject
    return None

def getUnpublishedModuleEntity(uid):
    ''' @summary: Returns an unpublished Module object from the datastore
        @param uid: The uid that describes the module to get from the datastore
        @type uid: String (later typecasted to an int)
        @return: Returns a Module object
        @rtype: Module
    '''
    user = getCurrentUserEntity()
    try:
        uid = int(uid)
    except:
        return None
    # One contributor could only have one version of particularly proposed unpublished module
    que = db.Query(datamodel.Module).filter('uid =', uid).filter('contributor =', user).filter('published =', False).filter('current =', False)
    moduleObject = que.get()
    if moduleObject:
        return moduleObject
    return None

def getModuleVersion(uid, version=0):
    ''' @summary: Populates a dictionary with a particular module's values from the datastore for use in a Django template
        @param uid: The uid that describes the module to get from the datastore and the version
        @type uid: String (later typecasted to an int)
        @return: Returns a dictionary containing module entity data
        @rtype: dictionary
    '''
    values = dict()
    try:
        uid = int(uid)
    except:
        values['error'] = 'Module id\'s and version numbers are numeric. Please check the URL. Example wikitheoria.appspot.com/1 or wikitheoria.appspot.com/1/2'
        return values
    
    tempObj = db.Query(datamodel.Module).filter('uid =', uid).filter('current =', True).get()
    nVersion = tempObj.version
    values['module_newest_version'] = nVersion
    
    if version == 0:
        #since the optional param 'version' wasn't specified, pull the current versions of the requested module, no matter it is published or not.
        moduleObject = db.Query(datamodel.Module).filter('uid =', uid).filter('current =', True).get()
    else:
        try:
            #check to see if the version is a slug or a version number.
            version = int(version)
            moduleObject = db.Query(datamodel.Module).filter('uid =', uid).filter('version =', version).get()
        except:
            moduleObject = db.Query(datamodel.Module).filter('uid =', uid).filter('current =', True).filter('published =', True).get()

    if moduleObject:
        # get original contributor
        orgObj = db.Query(datamodel.Module).filter('uid =', uid).filter('version =', 1).get()
        if orgObj:
            values['module_contrubutor_original'] = orgObj.contributor
        else:
            values['module_contrubutor_original'] = moduleObject.contributor
        
        
        values['module_title_general'] = moduleObject.title
        values['module_keywords_general'] = moduleObject.keywords
        values['module_contrubutor_general'] = moduleObject.contributor
        values['module_last_update_general'] = '%02d/%02d/%04d' % (moduleObject.date_submitted.month, moduleObject.date_submitted.day, moduleObject.date_submitted.year)
        values['module_scope_general'] = moduleObject.scope
        values['module_propositions_general'] = moduleObject.propositions
        values['module_key'] = moduleObject.key()
        values['module_derivations_general'] = moduleObject.derivations
        values['module_evidence_general'] = moduleObject.evidence
        
        values['module_uid'] = moduleObject.uid
        values['module_edit_url'] = '/module/edit/' + str(moduleObject.uid) + '/' + str(version)
        values['module_version'] = moduleObject.version
        values['markdown'] = moduleObject.theoryMarkdown
        values['html'] = moduleObject.theoryHtml
        values['terms'] = db.Query(datamodel.ModuleTerm).filter('module =', moduleObject)
        
        if moduleObject.current is True:
            values['module_url'] = '/modules/' + str(moduleObject.uid) + '/' + moduleObject.title
        else:
            values['module_url'] = '/modules/' + str(moduleObject.uid) + '/' + str(version) + '/' + moduleObject.title
    else:
        values['error'] = 'Module does not exist'
    return values


def getModuleByKey(key):
    ''' @summary: Populates a dictionary with a particular module's values from the datastore for use in a Django template
        @param key: The key that describes the module to get from the datastore and the version
        @type key: Key('keyString')
        @return: Returns a dictionary containing module entity data
        @rtype: dictionary
    '''    

    values = dict()
    
    try:
        key = Key(str(key))
    except:
        values['error'] = 'Module \'s keys are not Key type. Please check the URL. '
        return values
    
    try:
        moduleObject = db.Query(datamodel.Module).filter('__key__ =', key).get()
    except:
        values['error'] = 'Cannot get module by key. '
    
    
    values['module_newest_version'] = db.Query(datamodel.Module).filter('uid =', moduleObject.uid).filter('current =', True).get().version
    
    moduleSet = db.Query(datamodel.Module).filter('uid =', moduleObject.uid).filter('version =', moduleObject.version).fetch(limit=None)
    if len(moduleSet) > 1:
        values['show_hint'] = True
    
    orgObj = db.Query(datamodel.Module).filter('uid =', moduleObject.uid).filter('version =', 1).get()
    
    if orgObj:
        values['module_contrubutor_original'] = orgObj.contributor
    else:
        values['module_contrubutor_original'] = moduleObject.contributor
    
    
    
    if moduleObject:
        values['module_title_general'] = moduleObject.title
        values['module_keywords_general'] = moduleObject.keywords
        values['module_contrubutor_general'] = moduleObject.contributor
        
        
        values['module_last_update_general'] = '%02d/%02d/%04d' % (moduleObject.date_submitted.month, moduleObject.date_submitted.day, moduleObject.date_submitted.year)
        values['module_scope_general'] = moduleObject.scope
        values['module_propositions_general'] = moduleObject.propositions
        
        values['module_derivations_general'] = moduleObject.derivations
        values['module_evidence_general'] = moduleObject.evidence
        
        values['module_uid'] = moduleObject.uid
        values['module_key'] = str(key)
        values['module_edit_url'] = '/module/edit/' + str(moduleObject.uid) + '/' + str(moduleObject.version) + '/' + str(key)
        values['module_version'] = moduleObject.version
        values['module_status'] = moduleObject.status
        values['markdown'] = moduleObject.theoryMarkdown
        values['html'] = moduleObject.theoryHtml
        values['terms'] = db.Query(datamodel.ModuleTerm).filter('module =', moduleObject)
        
        if moduleObject.current is True:
            values['module_url'] = '/modules/' + str(moduleObject.uid) + '/' + moduleObject.title
        else:
            values['module_url'] = '/modules/' + str(moduleObject.uid) + '/' + str(moduleObject.version) + '/' + moduleObject.title
    else:
        values['error'] = 'Module does not exist'
    return values

def getModuleVersionCount(uid):
    countObject = db.Query(datamodel.VersionCounter).filter("module =", uid).get()
    if countObject:
        return countObject.count
    else:
        return 0

def getModuleCount():
    moduleList = db.Query(datamodel.Module).filter('current =', True).fetch(limit=None)
    if moduleList:
        return len(moduleList)
    else:
        return 0

def versionIncrement(uid):
    counter = db.Query(datamodel.VersionCounter).filter('module =', uid).get()

    if not counter:
        counterKey = datamodel.VersionCounter(module = uid, count = 1).put()
    else:
        counterKey = counter.key()
        try:
            from libmain import autoIncrement
            uid = db.run_in_transaction(autoIncrement, counterKey)
            return uid
        except db.TransactionFailedError:
            logging.error('Failed to get auto increment(version increment) value during transaction and retries')
            return -1