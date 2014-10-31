from libmain import doRender, createNewUID, decrementCounter
import datamodel
import logging
import json
from libuser import isContributingUser, isAdministratorUser
import webapp2
from google.appengine.ext import db
from google.appengine.api import search
from google.appengine.ext.db import Key


def getTermDefinitions(self):
    self.response.headers['Content-Type'] = 'application/json'
    term = self.request.get('term')
    
    try:
        termObject = db.Query(datamodel.Term).filter('word =', term).get()
    except:
        jsonData = {'error': 'Datastore error, try again later.', 'stat' : 'fail'}
        return jsonData
    
    if termObject:
        jsonData = {'term': term,
                    "stat": "ok",
                    'definitions' : [],
                    'uid': termObject.uid
                    }
        for item in termObject.termdefinition_set:
            jsonData["definitions"].append({'definition' : item.definition, 'uid' : item.uid})
    else:
        jsonData = {'error': 'Term not found', 'stat' : 'fail'}

    self.response.out.write(json.dumps(jsonData))
   

def getModules(self,content):
    self.response.headers['Content-Type'] = 'application/json'
    
    index = search.Index(name="modIdx")
    querystring = content.strip()
    doc_limit = 30
    
    try:
        search_query = search.Query(
                                    query_string = querystring,
                                    options = search.QueryOptions(
                                        limit = doc_limit,
                                        snippeted_fields=["metatheory", "terms", "propositions"],
                                        returned_fields=["title","keywords"]
                                                      ))
        results = index.search(search_query)

    except search.Error:
        logging.exception('search failed')
    
    
    if results:
        
        num_results = len(results.results)
        jsonData = dict()
        jsonList = []
        # get document from results
        for doc in results:
            
            jsonData["docID"] = doc.doc_id
            # get snippet of metatheory, terms and propositions
            # expr.name, expr.value
            for expr in doc.expressions:
                jsonData[expr.name] = expr.value
            
            # get title and keywords
            # field.name, field.value
            for field in doc.fields:
                jsonData[field.name] = field.value
                
            jsonList.append(jsonData)
            
    else:
        num_results = 0
        jsonList = []

    if results:
        jsonData = {'results': jsonList,
                    'num_results': num_results,
                    "stat": "ok",
                    }
    else:
        jsonData = {'error': 'Document Search Error', 'stat' : 'fail'}
 
    return json.dumps(jsonData)


def getSuggestions(self):
    self.response.headers['Content-Type'] = 'application/json'
    if self.request.get('query'):
        query = self.request.get('query')
        try:
            termObject = db.Query(datamodel.Term).order("word").fetch(1000, 0)
        except:
            jsonData = {'query': query, 'suggestions' : [], 'stat' : 'fail'}
            self.response.out.write(json.dumps(jsonData))
            return
        if termObject:
            jsonData = {'query': query, 'suggestions' : [], 'stat' : 'ok'}
            for item in termObject:
                if item.word.startswith(query):
                    jsonData['suggestions'].append(item.word)
            self.response.out.write(json.dumps(jsonData))
    else:
        jsonData = {'error': 'Argument: query(required)', 'stat' : 'fail'}
        self.response.out.write(json.dumps(jsonData))

#getTermDefinitions helper
def getAllTermDefinitions(term):
    try:
        termObject = db.Query(datamodel.Term).filter('word =', term).get()
    except:
        jsonData = {'error': 'Datastore error, try again later.', 'stat' : 'fail'}
        return jsonData
    if termObject:
        jsonData = {'term': term,
                    "stat": "ok",
                    'definitions' : [],
                    'uid': termObject.uid
                    }
        for item in termObject.termdefinition_set:
            jsonData["definitions"].append({'func' : item.function, 'definition' : item.definition, 'uid' : item.uid})
            #jsonData[definitions][item][definition] = item.definition
        return jsonData
    else:
        jsonData = {'error': 'Term not found', 'stat' : 'fail'}
        return jsonData

#getTermDefinitions helper
def getFilteredTermDefinitions(term, function):
    try:
        termObject = db.Query(datamodel.Term).filter('word =', term).get()
    except:
        jsonData = {'error': 'Datastore error, try again later.', 'stat' : 'fail'}
        return jsonData
    if termObject:
        functions = function + 's'
        jsonData = {'term': term, 'definitions' : {functions : []}, "stat": "ok" }
        for item in termObject.termdefinition_set:
            if item.function == function:
                jsonData['definitions'][functions].append(item.definition)
        return jsonData
    else:
        jsonData = {'error': 'Term not found', 'stat' : 'fail'}
        return jsonData


def getTermDefinition(self):
    self.response.headers['Content-Type'] = 'application/json'
    if self.request.get('function') and self.request.get('term'):
        jsonData = getFilteredTermDefinitions(self.request.get('term'), self.request.get('function'))
        self.response.out.write(json.dumps(jsonData))
    elif self.request.get('term'):
        jsonData = getAllTermDefinitions(self.request.get('term'))
        self.response.out.write(json.dumps(jsonData))
    else:
        jsonData = {'error': 'Argument: term(required)', 'stat' : 'fail'}
        self.response.out.write(json.dumps(jsonData))



def getCurrentModules(self):
    try:
        current_modules = db.Query(datamodel.Module).filter("current",True).order("-date_submitted")
    except:
        jsonData = {'stat':'failed','message':'failed to load modules'}
    try:
        jsonData = {'stat':'ok','uid':[],'title':[],'date_submitted':[],'last_update':[],'current_version':[],'published':[]}
        for module in current_modules:
            jsonData['uid'].append(module.uid)
            jsonData['title'].append(module.title)
            jsonData['date_submitted'].append('%02d/%02d/%04d' % (module.date_submitted.month, module.date_submitted.day, module.date_submitted.year))
            jsonData['last_update'].append('%02d/%02d/%04d' % (module.last_update.month, module.last_update.day, module.last_update.year))
            jsonData['current_version'].append(module.version)
    except:
        jsonData = {'stat':'fail','message':'failed to find all data'}
    return json.dumps(jsonData)

def getPastModules(self, module):
    try:
        pending_modules = db.Query(datamodel.Module).filter("published",False).order("-date_submitted")
    except:
        jsonData = {'stat':'failed','message':'failed to load pending modules'}
    try:
        jsonData = {'stat':'ok','uid':[],'title':[],'date_submitted':[],'version':[]}
        for module in pending_modules:
            jsonData['uid'].append(module.uid)
            jsonData['title'].append(module.title)
            jsonData['date_submitted'].append('%02d/%02d/%04d' % (module.date_submitted.month, module.date_submitted.day, module.date_submitted.year))
            jsonData['version'].append(module.version)
    except:
        jsonData = {'stat':'fail','message':'failed to find all data'}
    return json.dumps(jsonData)

def getPendingModules(self):
    try:
        # get pending modules
        pending_modules = db.Query(datamodel.Module).filter("published",False).order("-date_submitted")
    except:
        jsonData = {'stat':'failed','message':'failed to find pending module'}
        
    try:
        jsonData = {'stat':'ok','uid':[],'title':[],'date_submitted':[],'last_update':[],'current_version':[],'published':[],'key':[],'status':[]}
        for module in pending_modules:
            jsonData['uid'].append(module.uid)
            jsonData['title'].append(module.title)
            jsonData['date_submitted'].append('%02d/%02d/%04d' % (module.date_submitted.month, module.date_submitted.day, module.date_submitted.year))
            jsonData['last_update'].append('%02d/%02d/%04d' % (module.last_update.month, module.last_update.day, module.last_update.year))
            jsonData['current_version'].append(module.version)
            jsonData['key'].append(str(module.key()))
            jsonData['status'].append(module.status)

    except:
        jsonData = {'stat':'fail','message':'failed to find all data'}
    return json.dumps(jsonData)

def removeModule(self, module_uid):
    try:
        admin = isAdministratorUser()
    except:
        admin = False
    if admin is True:
        try:
            modules = db.Query(datamodel.Module).filter("uid",int(module_uid))
            temp = db.Query(datamodel.Module).filter("uid", int(module_uid)).filter("current", True).get()
            #module_terms = db.Query(datamodel.ModuleTerms).filter("module", temp)
        except:
            jsonData = {'stat' : 'fail' , 'message' : 'no module found'}
            return json.dumps(jsonData)
        try:
            for module in modules:
                module.delete()
            decrementCounter("modules")
            #for term in module_terms:
            #    term.delete()
            jsonData = {'stat' : 'ok'}
        except:
            jsonData = {'stat' : 'fail' , 'message' : 'unable to delete module'}
        return json.dumps(jsonData)
    else:
        return json.dumps({'stat' : 'fail', 'message' : 'must be an administrator'})

def removeModuleByKey(self, module_key):
    try:
        admin = isAdministratorUser()
    except:
        admin = False
    if admin is True:
        try:
            module_key = Key(module_key)
            
            module = db.Query(datamodel.Module).filter("__key__ =", module_key).get() 
        except:
            jsonData = {'stat' : 'fail' , 'message' : 'no module found'}
            return json.dumps(jsonData)
        try:
            module.delete()
            jsonData = {'stat' : 'ok'}
        except:
            jsonData = {'stat' : 'fail' , 'message' : 'unable to delete module'}
        return json.dumps(jsonData)
    else:
        return json.dumps({'stat' : 'fail', 'message' : 'must be an administrator'})


def setCurrentVersion(self, uid, version):
    try:
        old_module = db.Query(datamodel.Module).filter("module",int(uid)).filter("current",True).get()
        new_module = db.Query(datamodel.Module).filter("module",int(uid)).filter("version",int(version)).get()
    except:
        jsonData = {'stat':'failed','message':'could not load module'}
    try:
        old_module.current = False
        old_module.put()
        new_module.current = True
        new_module.put()
        jsonData = {'stat':'ok'}
    except:
        jsonData = {'stat':'failed','message':'could not update current version'}
    return json.dumps(jsonData)


def publishCurrentVersion(self, uKey):
    # self, uKey
    
    from libmodule import versionIncrement,getModuleVersionCount,updateSearchDocument
    
    try:
        current_module = db.Query(datamodel.Module).filter("__key__ =", Key(uKey)).get()
    except:
        jsonData = {'stat':'failed','message':'could not load module'}
    
    try:
        # if its version == 0, then it is a newly created and never published module    
        if current_module.version == 0:
            current_module.current = True
            current_module.published = True    
            current_module.version = 1 
            current_module.put()
            
            # update the search index
            updateSearchDocument(current_module.uid)
            versionIncrement(current_module.uid)
            jsonData = {'stat':'ok'}
            
        # we need to pull out the uid of old_module, find the current version, set the old version current to False
        # set the new_module    
        else:
            module_id = current_module.uid
            old_module = db.Query(datamodel.Module).filter("uid =", module_id).filter("current =",True).get()
            old_module.current = False
            old_module.put()
            
            current_module.current = True
            current_module.published = True
            current_module.put()
            
            # Once we publish the newest copy of this version, we will archive other copies.
            archived_version = getModuleVersionCount(module_id) + 1
            other_modules = db.Query(datamodel.Module).filter("uid =", module_id).filter("__key__ !=", Key(uKey)).filter("version =", archived_version).fetch(limit=None)
            for module in other_modules:
                module.status = "archived"
                module.put()
            # update the search index
            updateSearchDocument(module_id)
            versionIncrement(module_id)
            jsonData = {'stat':'ok'}
            
            
        
    except:
        jsonData = {'stat':'failed','message':'could not update current version'}
        
    return json.dumps(jsonData)    

def getModule(self, uKey):
    try:
        current_module = db.Query(datamodel.Module).filter("__key__ =", Key(uKey)).get()
    
        jsonData ={'email': current_module.contributor.email}
        jsonData['title1'] = current_module.title  
        jsonData['modKey'] = uKey  
        
    except:
        jsonData = {'stat':'failed','message':'could not load module'} 
        
    return json.dumps(jsonData)
        
def browseModules(self):
    discipline = self.request.get('discipline')
    sort = self.request.get('sort')
    if not discipline:
        discipline = "Sociology"
    if not self.request.get('limit'):
        limit = 10
    else:
        limit = int(self.request.get('limit'))
    if not self.request.get('offset'):
        offset = 0
    else:
        offset = int(self.request.get('offset'))
    try:
        if sort == "newest":
            modules = db.Query(datamodel.Module).filter("discipline",discipline).filter("published",True).filter("current",True).order('date_submitted').fetch(limit,offset=offset)
        elif sort == "oldest":
            modules = db.Query(datamodel.Module).filter("discipline",discipline).filter("published",True).filter("current",True).order('-date_submitted').fetch(limit,offset=offset)
        elif sort == "contributorAsc":
            modules = db.Query(datamodel.Module).filter("discipline",discipline).filter("published",True).filter("current",True).order('contributor').fetch(limit,offset=offset)
        elif sort == "contributorDesc":
            modules = db.Query(datamodel.Module).filter("discipline",discipline).filter("published",True).filter("current",True).order('-contributor').fetch(limit,offset=offset)
        elif sort == "titleAsc":
            modules = db.Query(datamodel.Module).filter("discipline",discipline).filter("published",True).filter("current",True).order('title').fetch(limit,offset=offset)
        elif sort == "titleDesc":
            modules = db.Query(datamodel.Module).filter("discipline",discipline).filter("published",True).filter("current",True).order('-title').fetch(limit,offset=offset)     
        else:
            modules = db.Query(datamodel.Module).filter("discipline",discipline).filter("published",True).filter("current",True).order('date_submitted').fetch(limit,offset=offset)
        
        count = db.Query(datamodel.Counter).filter("name","modules").get()
    except:
        jsonData = {'stat':'failed','message':'could not load modules'}
        
    if modules:
            jsonData = {'stat':'ok','total':count.count,'uid':[],'title':[],'date_submitted':[],'version':[], 'contributor':[],'discipline':[]}
            for module in modules:
                jsonData['uid'].append(module.uid)
                jsonData['title'].append(module.title)
                jsonData['date_submitted'].append('%02d/%02d/%04d' % (module.date_submitted.month, module.date_submitted.day, module.date_submitted.year))
                jsonData['version'].append(module.version)
                jsonData['contributor'].append(module.contributor.alias)
                jsonData['discipline'].append(module.discipline)
    else:
        jsonData = {'stat':'failed','message':'could not load modules'}
    return json.dumps(jsonData)

def getTerms(self):
    try:
        terms = db.Query(datamodel.Term).order("-date_submitted")
    except:
        jsonData = {'stat':'fail', 'message': 'failed to retrieve terms'}
        return json.dumps(jsonData)
    try:
        jsonData = {'stat':'ok', 'word': [], 'slug':[], 'date_submitted':[], 'contributor':[], 'uid':[]}
        for term in terms:
            jsonData['uid'].append(term.uid)
            jsonData['word'].append(term.word)
            jsonData['contributor'].append(term.contributor.alias)
            jsonData['date_submitted'].append('%02d/%02d/%04d' % (term.date_submitted.month, term.date_submitted.day, term.date_submitted.year))
            jsonData['slug'].append(term.slug)
    except:
        jsonData = {'stat':'fail', 'message':'failed to find all data'}
    return json.dumps(jsonData)

def removeTerm(self, term):
    try:
        admin = isAdministratorUser()
    except:
        admin = False
    if admin is True:
        try:
            term = db.Query(datamodel.Term).filter("uid",int(term)).get()
        except:
            jsonData = {'stat':'failed','message':'failed to find term'}
            return json.dumps(jsonData)
        try:
            term.delete()
        except:
            jsonData = {'stat':'failed','message':'failed to delete term'}
            return json.dumps(jsonData)
    else:
        jsonData = {'stat':'failed','message':'must be an administrator'}
        return json.dumps(jsonData)


class ApiHandler(webapp2.RequestHandler):
    def get(self):

        if self.request.get('method') == 'getTermDefinitions':
            getTermDefinitions(self)
            return
        elif self.request.get('method') == 'searchModules':
            content = self.request.get('query')
            json = getModules(self, content)
            self.response.out.write(json)
            return    
            
        elif self.request.get('method') == 'getCurrentModules':
            json = getCurrentModules(self)
            self.response.out.write(json)
            return
        elif self.request.get('method') == 'getPastModules':
            module = self.request.get('module')
            version = self.request.get('version')
            json = getPastModules(module, version)
            self.response.out.write(json)
            return
        elif self.request.get('method') == 'getPendingModules':
            json = getPendingModules(self)
            self.response.out.write(json)
            return        
        
        elif self.request.get('method') == 'setCurrentVersion':
            module = self.request.get('module')
            version = self.request.get('version')
            json = setCurrentVersion(self, module, version)
            self.response.out.write(json)
            return
        elif self.request.get('method') == 'publishCurrentVersion':
            moduleKey = self.request.get('module')
            json = publishCurrentVersion(self, moduleKey)
            self.response.out.write(json)
            return        
        elif self.request.get('method') == 'getModule':
            moduleKey = self.request.get('moduleKey')
            json = getModule(self, moduleKey)
            self.response.out.write(json)
            return        
        elif self.request.get('method') == 'removeModule':
            module = self.request.get('module')
            json = removeModule(self, module)
            self.response.out.write(json)
            return
        elif self.request.get('method') == 'removeModuleByKey':
            moduleKey = self.request.get('moduleKey')
            json = removeModuleByKey(self, moduleKey)
            self.response.out.write(json)
            return
        elif self.request.get('method') == 'browseModules':
            json = browseModules(self)
            self.response.out.write(json)
            return
        elif self.request.get('method') == 'getTerms':
            json = getTerms(self)
            self.response.out.write(json)
            return
        elif self.request.get('method') == 'removeTerm':
            term = self.request.get('term')
            json = removeTerm(self, term)
            self.response.out.write(json)
            return
        else:
            self.response.headers['Content-Type'] = 'application/json'
            jsonData = {'error': 'Unknown method.'}
#             self.response.out.write(json.dumps(jsonData))
            self.redirect("/")
            return        


class MarkdownHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()


app = webapp2.WSGIApplication(
                                         [('/api/markdown.*', MarkdownHandler),
                                          ('/api.*', ApiHandler)],
                                          debug=True)
