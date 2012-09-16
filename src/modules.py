#modules.py
from main import getUrlResourceList, doRender, getCurrentUserEntity, createNewUID
import datamodel
import logging
import webapp2
#from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db


def versionIncrement(uid):
    counter = db.Query(datamodel.VersionCounter).filter('module =', uid).get()

    if not counter:
        counterKey = datamodel.VersionCounter(module = uid, count = 1).put()
    else:
        counterKey = counter.key()
    try:
        from main import autoIncrement
        uid = db.run_in_transaction(autoIncrement, counterKey)
        return uid
    except db.TransactionFailedError:
        logging.error('Failed to get auto increment(version increment) value during transaction and retries')
        return -1


def getModuleCount():
    countObject = db.Query(datamodel.Counter).filter("name = ", "modules").get()
    if countObject:
        return countObject.count
    else:
        return 0

def getModuleVersionCount(uid):
    countObject = db.Query(datamodel.VersionCounter).filter("module = ", uid).get()
    if countObject:
        return countObject.count
    else:
        return 0

def getModuleVersions(uid):
    if getModuleEntity(uid) is not None:
        module = getModuleEntity(uid)
        que = db.Query(datamodel.ModuleVersion)
        que.filter('module = ', module)
        versions = que.order('date_submitted')
        return versions

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

def getFeaturedModule():
    ''' @summary: Populates a dictionary with the featured modules's values from the datastore for use in a Django template
        @return: Returns a dictionary containing module entity data
        @rtype: dictionary
    '''
    values = dict()
    que = db.Query(datamodel.FeaturedModule)
    que.order('-featured_date')
    moduleObject = que.get()
    if moduleObject:
        values['module_title_general'] = moduleObject.module.title
        values['module_contrubutor_general'] = moduleObject.module.contributor.alias
        values['module_last_update_general'] = '%02d/%02d/%04d' % (moduleObject.module.last_update.month, moduleObject.module.last_update.day, moduleObject.module.last_update.year)
        values['module_scope_general'] = moduleObject.module.scope
        values['module_propositions_general'] = moduleObject.module.propositions
        values['module_url'] = '/modules/' + str(moduleObject.module.uid) + '/' + str(moduleObject.module.version) + '/'+ moduleObject.module.title
        values['module_meta_theory_general'] = moduleObject.module.meta_theory[0:500] + "<a href=" + values['module_url'] + ">Read More...</a>"
        values['module_version'] = str(moduleObject.module.version)
        terms = []
        for item in moduleObject.module.moduleterm_set:
            terms.append({'term':item.term, 'definition':item.definition})
        values['terms'] = terms
    else:
        values['error'] = 'Featured module does not exist'
    return values

def getModules():
    ''' @summary: Returns all Modules from the datastore ordered by date published
        @return: Returns an Module object containing all articles  
        @rtype: Module
    '''
    que = db.Query(datamodel.Module).filter('current =', True)
    modules = que.order('-date_submitted')
    return modules

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
        values['module_contrubutor_general'] = moduleObject.contributor
        values['module_last_update_general'] = '%02d/%02d/%04d' % (moduleObject.last_update.month, moduleObject.last_update.day, moduleObject.last_update.year)
        values['module_meta_theory_general'] = moduleObject.meta_theory
        values['module_scope_general'] = moduleObject.scope
        values['module_propositions_general'] = moduleObject.propositions
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
    if version == 0:
        #since the optional param 'version' wasn't specified, pull the current versions of the requested module
        moduleObject = db.Query(datamodel.Module).filter('uid =', uid).filter('current =', True).filter('published =', True).get()
    else:
        try:
            #check to see if the version is a slug or a version number.
            version = int(version)
            moduleObject = db.Query(datamodel.Module).filter('uid =', uid).filter('version =', version).filter('published =', True).get()
        except:
            moduleObject = db.Query(datamodel.Module).filter('uid =', uid).filter('current =', True).filter('published =', True).get()
    
    if moduleObject:
        values['module_title_general'] = moduleObject.title
        values['module_contrubutor_general'] = moduleObject.contributor
        values['module_last_update_general'] = '%02d/%02d/%04d' % (moduleObject.date_submitted.month, moduleObject.date_submitted.day, moduleObject.date_submitted.year)
        values['module_meta_theory_general'] = moduleObject.meta_theory
        values['module_scope_general'] = moduleObject.scope
        values['module_propositions_general'] = moduleObject.propositions
        values['module_uid'] = moduleObject.uid
        values['module_edit_url'] = '/module/edit/' + str(moduleObject.uid) + '/' + moduleObject.title
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

def updateModule(uid, title, meta_theory, markdown, scope, propositions, discipline, publish):
    ''' @summary: Updates a module entity 
        @param uid, title, meta_theory, scope, propositions, discipline
        @type String
        @return: Returns the uid if successful, else -1
        @rtype: integer
    '''
    from main import parseMarkdown
    oldModule = getModuleEntity(uid)
    #this if is for when module has been published previously
    if publish == "true" and oldModule.version > 0:
        user = getCurrentUserEntity()
        oldModule.current = False
        oldModule.published = True
        db.put(oldModule)
        try:
            uid = int(uid)
        except:
            return -1   
        
        #create uid for module version
        revision_uid = versionIncrement(uid)
        if revision_uid == -1:
            return -1
        else:
            try:
                moduleRevision = datamodel.Module(uid = uid,
                                                 version = revision_uid,
                                                 meta_theory = meta_theory,
                                                 theoryMarkdown = markdown,
                                                 theoryHtml = parseMarkdown(markdown),
                                                 scope = scope,
                                                 propositions = propositions,
                                                 discipline = discipline,
                                                 title = title,
                                                 contributor = user,
                                                 current = True, published = True)
                moduleRevision.put()
                return moduleRevision
            except:
                logging.error('Failed to create module. Module number uid:' + str(uid))
                return -1
    #when this is the first time being published
    elif publish == "true" and oldModule.version == 0:
        module = oldModule
        module.title = title
        module.meta_theory = meta_theory
        module.theoryMarkdown = markdown
        module.theoryHtml = parseMarkdown(markdown)
        module.scope = scope
        module.propositions = propositions
        module.discipline = discipline
        module.title = title
        module.published = True
        module.version = 1
        key = db.put(module)
        createNewUID("modules") #increments the overall module counter once the module is published
        return key
    else:
        module = oldModule
        module.title = title
        module.meta_theory = meta_theory
        module.theoryHtml = parseMarkdown(markdown)
        module.theoryMarkdown = markdown
        module.scope = scope
        module.propositions = propositions
        module.discipline = discipline
        module.title = title
        module.version = 0
        key = db.put(module)
        return key

def newModule(title, meta_theory, markdown, scope, propositions, discipline, publish):
    ''' @summary: Creates a new module entity 
        @param title, meta_theory, scope, propositions, discipline
        @type String
        @return: Returns the uid if successful, else -1
        @rtype: integer
    '''
    from main import parseMarkdown
    uid = createNewUID("modulesUID")
    if uid == 0:
        return -1
    else:
        user = getCurrentUserEntity()   
        
        try:
            if publish == "false": 
                module = datamodel.Module(title = title, 
                                          discipline = discipline, 
                                          meta_theory = meta_theory, 
                                          theoryMarkdown = markdown,
                                          theoryHtml = parseMarkdown(markdown),
                                          uid = uid, version = 0, 
                                          scope = scope, 
                                          contributor = user,
                                          propositions = propositions,
                                          published = False, current = True)
            else:
                module = datamodel.Module(title = title, 
                                          discipline = discipline, 
                                          meta_theory = meta_theory, 
                                          theoryMarkdown = markdown,
                                          theoryHtml = parseMarkdown(markdown),
                                          uid = uid, version = 1, 
                                          scope = scope, 
                                          contributor = user,
                                          propositions = propositions,
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


class NewModuleHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        from users import isContributingUser
        if isContributingUser() is True:
            values['javascript'] = ['/static/js/jquery.js', '/static/js/plugins/autocomplete/jquery.autocomplete.min.js', '/static/js/modules/newModule.js',
                                    '/static/js/plugins/wmd_stackOverflow/wmd.js', '/static/js/plugins/wmd_stackOverflow/showdown.js']
            values['css'] = ['/static/js/plugins/autocomplete/styles.css', '/static/css/modules.css', '/static/js/plugins/wmd_stackOverflow/wmd.css']
            doRender(self, 'newModule.html',values)
        else:
            doRender(self, 'join.html',values)
  
    def post(self):
        title = self.request.get("title")
        metaTheory = self.request.get("meta_theory")
        scopeList = self.request.get_all("scopes")
        propositionList = self.request.get_all("propositions")
        markdown = self.request.get("markdown")
        discipline = self.request.get("discipline")
        publishBool = self.request.get("published")
        
        modKey = newModule(title, metaTheory, markdown, scopeList, propositionList, discipline, publishBool)
        
        #terms
        terms = self.request.get_all("terms")
        definitions = self.request.get_all("definitions")
        functions = self.request.get_all("functions")
        while terms:
            term = terms.pop().lower()
            definition = definitions.pop()
            function = functions.pop()
            
            termKey = db.Query(datamodel.Term).filter('word =', term).get()
            if termKey:
                defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
                if not defKey:
                    from terms import newDefinition
                    defKey = newDefinition(termKey.slug, function, definition)
            else:
                from terms import newTerm
                newTerm(term, term, function, definition)
                termKey = db.Query(datamodel.Term).filter('word =', term).get()
                defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
            
            datamodel.ModuleTerm(module = modKey, term = termKey, definition = defKey).put()
        
        if modKey != -1:
            self.redirect("/modules/", True)
        else:
            values = {'error' : 'Failed to create module. Please try again later.'}
            doRender(self, 'error.html', values)
        

class EditModuleHandler(webapp2.RequestHandler):
    def get(self):
        from users import isContributingUser
        if isContributingUser() is True:
            values = dict()
            url = getUrlResourceList(self)
            values = getModule(url[2])
            values['javascript'] = ['/static/js/jquery.js', '/static/js/plugins/autocomplete/jquery.autocomplete.min.js', '/static/js/modules/newModule.js',
                                    '/static/js/plugins/wmd_stackOverflow/wmd.js', '/static/js/plugins/wmd_stackOverflow/showdown.js']
            values['css'] = ['/static/js/plugins/autocomplete/styles.css', '/static/css/modules.css', '/static/js/plugins/wmd_stackOverflow/wmd.css']
            doRender(self, 'editModule.html', values)
        else:
            self.redirect('/modules/')
            
    def post(self):
        title = self.request.get("title")
        metaTheory = self.request.get("meta_theory")
        scopeList = self.request.get_all("scopes")
        propositionList = self.request.get_all("propositions")
        markdown = self.request.get("markdown")
        discipline = self.request.get("discipline")
        publishBool = self.request.get("published")
        uid = int(self.request.get("uid"))
        
        
        modKey = updateModule(uid, title, metaTheory, markdown, scopeList, propositionList, discipline, publishBool)
                              
        #terms
        terms = self.request.get_all("terms")
        definitions = self.request.get_all("definitions")
        functions = self.request.get_all("functions")
        
        while terms:
            term = terms.pop().lower()
            definition = definitions.pop()
            function = functions.pop()
            
            termKey = db.Query(datamodel.Term).filter('word =', term).get()
            if termKey:
                defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
                if not defKey:
                    from terms import newDefinition
                    defKey = newDefinition(termKey.slug, function, definition)
            else:
                from terms import newTerm
                newTerm(term, term, function, definition)
                termKey = db.Query(datamodel.Term).filter('word =', term).get()
                defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
            
            datamodel.ModuleTerm(module = modKey, term = termKey, definition = defKey).put()
            
        if modKey != -1:
            self.redirect("/modules", True)
        else:
            values = {'error' : 'Failed to update module. Please try again later.'}
            doRender(self, 'error.html', values)

class ModuleHandler(webapp2.RequestHandler):
    def get(self):
        from users import isContributingUser
        pathList = getUrlResourceList(self)
        values = dict()
        if len(pathList) == 1 or pathList[1] == '':
            doRender(self, 'moduleDefault.html', values)
        elif len(pathList) == 2 or pathList[2] == '':
            values = getModuleVersion(pathList[1])
            count = getModuleVersionCount(int(pathList[1]))+1
            #workaround for list of versions
            versions = []
            i = 1
            while i < count:
                versions.append(str(i))
                i += 1
            values['versions'] = versions
            if isContributingUser() is True:
                values["contributing_user"] = "True"
            doRender(self, 'module.html', values)
        else:
            try:
            #check to see if the version is a slug or a version number.
                uid = int(pathList[1])
            except:
                values['error'] = 'Module id\'s and version numbers are numeric. Please check the URL. Example wikitheoria.appspot.com/1 or wikitheoria.appspot.com/1/2'
                doRender(self, 'module.html', values)
                return
            values = getModuleVersion(uid, pathList[2])
            count = getModuleVersionCount(uid)+1
            #workaround for list of versions
            versions = []
            i = 1
            while i < count:
                versions.append(str(i))
                i += 1
            values['versions'] = versions
            if isContributingUser() is True:
                values["contributing_user"] = "True"
            doRender(self, 'module.html', values)
    def post(self):
        version = self.request.get("version")
        uid = self.request.get("module_version_uid")
        self.redirect('/modules/' + uid + '/' + version)
        
class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        from users import isContributingUser
        if isContributingUser() is True:
            values['can_contribute'] = 'True'
            unpublishedModules = getUnpublishedModules()
            values['unpublished_modules'] = unpublishedModules
        featuredModule = getFeaturedModule()
        modules = db.Query(datamodel.Module).filter('current =', True).filter('published =', True).order('-date_submitted').fetch(10)
        
        values["ten_newest_modules"] = modules
        if featuredModule.has_key('error'):
            values['module_error'] = 'No module currently featured'
        else:
            for key in featuredModule:
                values[key] = featuredModule[key]
        values['javascript'] = ['/static/js/jquery.js', '/static/js/modules/moduleDefault.js']
            
        doRender(self, 'moduleDefault.html', values)
        
app = webapp2.WSGIApplication(
                                         [('/module/edit.*', EditModuleHandler),
                                          ('/module/new.*', NewModuleHandler),
                                          ('/modules/?', MainPageHandler),
                                          ('/modules/.*', ModuleHandler)],
                                          debug=True)

