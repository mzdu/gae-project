#from main import getUrlResourceList, doRender, getCurrentUserEntity, createNewUID
from libmain import doRender, getUrlResourceList
from libmodule import newModule, getModule, updateModule, getUnpublishedModules, getModuleVersion, getModuleVersionCount
from libuser import isContributingUser

import webapp2
import math
import datamodel
import logging
from google.appengine.ext import db


# create a new module
class NewModuleHandler(webapp2.RequestHandler):
    def get(self):
        
        values = dict()
        # test if the currentUser is a contributing user.
        if isContributingUser() is True:
            
            values['javascript'] = ['/static/js/jquery-1.9.1.js',
                                    '/static/js/jquery-ui.js',
                                    '/static/js/modules/newModule.js',
                                    '/static/js/plugins/wmd_stackOverflow/wmd.js', 
                                    '/static/js/plugins/wmd_stackOverflow/showdown.js']
            values['css'] = ['/static/js/jquery-ui.css',
                             '/static/css/modules.css', 
                             '/static/js/plugins/wmd_stackOverflow/wmd.css']
            
            doRender(self, 'newModule.html',values)
             
        else:
            doRender(self, 'join.html',values)
   
    def post(self):
        title = self.request.get("title")
        keywords = self.request.get("keywords")
        scopes = self.request.get_all("scopes[]")
        propositions = self.request.get_all("propositions[]")
        derivations =  self.request.get_all("derivations[]")
        evidence = self.request.get("evidence")
        markdown = self.request.get("markdown")
        publishBool = self.request.get("published")
        
        scopeList = [str(scope) for scope in scopes]
        propositionList = [str(prop) for prop in propositions]
        derivationList = [str(drv) for drv in derivations]
        
        #using newModule in libmodule.py
        modKey = newModule(title, keywords, markdown, scopeList, propositionList, derivationList, evidence, publishBool)
         
##################################################################         
        #terms related processing
        terms = self.request.get_all("terms[]")
        definitions = self.request.get_all("definitions[]")
        termList = [str(term) for term in terms]
        definitionList = [str(definition) for definition in definitions]
       
        while termList:
            term = termList.pop().lower()
            definition = definitionList.pop()
            slug = term.replace(' ', '-')
               
            from libterm import newTerm
            keys = newTerm(term, slug, definition)
         
            datamodel.ModuleTerm(module=modKey, term=keys[0], definition=keys[1]).put()
        
        
        
        
        if modKey != -1:
            self.redirect("/modules", True)
        else:
            values = {'error' : 'Failed to update module. Please try again later.'}
            doRender(self, 'error.html', values)        


# edit a selected module        
class EditModuleHandler(webapp2.RequestHandler):
    def get(self):
        if isContributingUser() is True:
            values = dict()
            url = getUrlResourceList(self)
            # get all values of a module
            values = getModule(url[2])
            values['javascript'] = ['/static/js/jquery-1.9.1.js', 
                                    '/static/js/jquery-ui.js',
                                    '/static/js/modules/newModule.js',
                                    '/static/js/plugins/wmd_stackOverflow/wmd.js', 
                                    '/static/js/plugins/wmd_stackOverflow/showdown.js']
            values['css'] = ['/static/js/jquery-ui.css',
                             '/static/css/modules.css', 
                             '/static/js/plugins/wmd_stackOverflow/wmd.css']
            
            doRender(self, 'editModule.html', values)
        else:
            self.redirect('/modules')
              
    def post(self):
        title = self.request.get("title")
        keywords = self.request.get("keywords")
        scopes = self.request.get_all("scopes[]")
        propositions = self.request.get_all("propositions[]")
        derivations =  self.request.get_all("derivations[]")
        evidence = self.request.get("evidence")
        markdown = self.request.get("markdown")
        publishBool = self.request.get("published")
        uid = int(self.request.get("uid"))

        scopeList = [str(scope) for scope in scopes]
        propositionList = [str(prop) for prop in propositions]
        derivationList = [str(drv) for drv in derivations]
          
        modKey = updateModule(uid, title, keywords, markdown, scopeList, propositionList, derivationList, evidence, publishBool)
                                
        #terms
        terms = self.request.get_all("terms[]")
        definitions = self.request.get_all("definitions[]")
        termList = [str(term) for term in terms]
        definitionList = [str(definition) for definition in definitions]
       
        while termList:
            term = termList.pop().lower()
            definition = definitionList.pop()
            slug = term.replace(' ', '-')
               
            from libterm import newTerm
            keys = newTerm(term, slug, definition)
         
            datamodel.ModuleTerm(module=modKey, term=keys[0], definition=keys[1]).put()      
              
        if modKey != -1:
            self.redirect("/modules", True)
        else:
            values = {'error' : 'Failed to update module. Please try again later.'}
            doRender(self, 'error.html', values)


# display a selected module 
class ModuleHandler(webapp2.RequestHandler):
    def get(self):
        #convert a url to a list of segmented elements like ['modules','']
        pathList = getUrlResourceList(self)
        
        values = dict()
        from libmain import RepresentsInt
        
        if len(pathList) == 1 or not RepresentsInt(pathList[1]):
            self.redirect('/modules/')
        
        # case ['modules','10'], which indicates the newest version   
        elif len(pathList) == 2:
            
            # get module info from datastore and stack them into values dictionary
            values = getModuleVersion(pathList[1])
            
            # get the count of version of a module
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


#display the list of modules         
class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        
        from libmain import RepresentsInt
        from libmodule import getModuleCount
         
        moduleCount = float(getModuleCount()) 
         
        urlList = getUrlResourceList(self)
        urlList.append('')
        urlList.append('')
        
        #setup pageLimit here 
        pageLimit = 15 
        pageNumber = urlList[2]
         
        pageMax = math.ceil(moduleCount/pageLimit)
        pageMax = int(pageMax) 
        if pageNumber == '' or pageNumber == '1':
            pageNumber = 1
              
        elif RepresentsInt(pageNumber):
            pageNumber = int(pageNumber)
            if pageNumber > pageMax:
                pageNumber = 1
            else:
                pass
          
        else:
            pageNumber = 1
            
        
        if isContributingUser() is True:
            values['can_contribute'] = 'True'
            unpublishedModules = getUnpublishedModules()
            values['unpublished_modules'] = unpublishedModules
        else:
            pass
        
        pageList = []
        for pageN in range(pageMax):
            pageList.append(str(pageN+1))
            
        modules = db.Query(datamodel.Module).filter('current =', True).filter('published =', True).order('-date_submitted').fetch(limit=pageLimit, offset=((pageNumber-1)*pageLimit))
        values['modules_general'] = modules
        values['modules_page'] = pageList
        values['modules_count'] = int(moduleCount)
        values['javascript'] = ['/static/js/jquery-1.9.1.js', '/static/js/modules/moduleDefault.js']
             
        doRender(self, 'moduleDefault.html', values)
        
app = webapp2.WSGIApplication([
                               ('/module/edit.*', EditModuleHandler),
                               ('/module/new.*', NewModuleHandler),
                               ('/modules/page.*', MainPageHandler),
                               ('/modules/?', MainPageHandler),
                               ('/modules/.*', ModuleHandler)
                                ],debug=True)

