#from main import getUrlResourceList, doRender, getCurrentUserEntity, createNewUID
from libmain import doRender, getUrlResourceList
from libmodule import newModule, updateModule, getUnpublishedModules, getModuleVersion, getModuleVersionCount
from libuser import isContributingUser, isAdministratorUser

import webapp2
import math
import datamodel
import logging

from google.appengine.ext import db
from google.appengine.ext.db import Key


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
            
            if isAdministratorUser() is True:
                values['is_administrator'] = True
            else:
                values['is_administrator'] = False
            
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
        key_uid = newModule(title, keywords, markdown, scopeList, propositionList, derivationList, evidence, publishBool)
        ##################################################################         
        #terms related processing
        terms = self.request.get_all("terms[]")
        definitions = self.request.get_all("definitions[]")
        termList = [str(term) for term in terms]
        definitionList = [str(definition) for definition in definitions]
       
        #adhere term and definition together and combine, then append to termString
        termDef = []
        from libterm import newTerm
        while termList:
            term = termList.pop().lower()
            slug = term.replace(' ', '-')
            definition = definitionList.pop()
            #termDef for search document
            termDef.append(term + ': ' + definition + '; ')     
                   
                   
            # find existed term
            termKey = db.Query(datamodel.Term).filter("word = ", term).get()
            
            # exisited term
            if termKey:
                # find existed definition
                defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
                
                # new definition
                if not defKey:
                    keys = newTerm(term, slug, definition)
                    datamodel.ModuleTerm(module=key_uid[0], term=keys[0], definition=keys[1]).put()
                # existed definition
                else:
                    # attach existed term with this module
                    datamodel.ModuleTerm(module=key_uid[0], term=termKey, definition=defKey).put()
                
            # new term
            else:
                keys = newTerm(term, slug, definition)
                datamodel.ModuleTerm(module=key_uid[0], term=keys[0], definition=keys[1]).put()

     
        if key_uid[0] != -1:
            uid = str(key_uid[1])
            self.response.out.write(uid)
        else:
            values = {'error' : 'Failed to update module. Please try again later.'}
            doRender(self, 'error.html', values)        


# edit a selected module        
class EditModuleHandler(webapp2.RequestHandler):
    def get(self):
        if isContributingUser() is True:
            values = dict()
            url = getUrlResourceList(self)
            
            if len(url) == 5:
                from libmodule import getModuleByKey
                keyStr = url[4]
                values = getModuleByKey(keyStr)
            else:    
                # get all values of a module
                values = getModuleVersion(url[2],url[3])
                
                
            values['javascript'] = ['/static/js/jquery-1.9.1.js', 
                                    '/static/js/jquery-ui.js',
                                    '/static/js/modules/newModule.js',
                                    '/static/js/plugins/wmd_stackOverflow/wmd.js', 
                                    '/static/js/plugins/wmd_stackOverflow/showdown.js']
            values['css'] = ['/static/js/jquery-ui.css',
                             '/static/css/modules.css', 
                             '/static/js/plugins/wmd_stackOverflow/wmd.css']
            
            if isAdministratorUser() is True:
                values['is_administrator'] = True
            else:
                values['is_administrator'] = False     
                       
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
        
        # nVersion is the currently published newest module version
        nVer = self.request.get("nVersion")
        # mVersion states the version of current editing module 
        mVer = self.request.get("mVersion")

        scopeList = [str(scope) for scope in scopes]
        propositionList = [str(prop) for prop in propositions]
        derivationList = [str(drv) for drv in derivations]
          
        modKey = updateModule(uid, title, keywords, markdown, scopeList, propositionList, derivationList, evidence, publishBool, nVer, mVer)

        ############################################################                                
        #terms related processing
        terms = self.request.get_all("terms[]")
        definitions = self.request.get_all("definitions[]")
        termList = [term for term in terms]
        definitionList = [definition for definition in definitions]

        #adhere term and definition together and combine, then append to termString
#         termDef = []


        # remove the old term list from datastore then append new list to module
        moduleTerms = db.Query(datamodel.ModuleTerm).filter('module =', modKey).fetch(limit=None,offset=0)
        for moduleTerm in moduleTerms:
            moduleTerm.delete()


        from libterm import newTerm
        
        while termList:
            term = termList.pop().lower()
            definition = definitionList.pop()
            slug = term.replace(' ', '-')
#             #termDef for search document
#             termDef.append(term + ':' + definition + ';')
        
            # find existed term
            termKey = db.Query(datamodel.Term).filter("word = ", term).get()
            
            # exisited term
            if termKey:
                # find existed definition
                defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
                
                # new definition
                if not defKey:
                    keys = newTerm(term, slug, definition)
                    datamodel.ModuleTerm(module=modKey, term=keys[0], definition=keys[1]).put()
                # existed definition
                else:
                    # attach existed term with this module
                    datamodel.ModuleTerm(module=modKey, term=termKey, definition=defKey).put()
            # new term
            else:
                keys = newTerm(term, slug, definition)
                datamodel.ModuleTerm(module=modKey, term=keys[0], definition=keys[1]).put()
                  


        modKey = str(modKey)
        self.response.out.write(modKey)
        
#         if modKey != -1:
#             values = {'error' : 'Edit Module, all passed.'}
#             doRender(self, 'error.html', values)
#         else:
#             values = {'error' : 'Failed to update module. Please try again later.'}
#             doRender(self, 'error.html', values)
        

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
            
            for obj in values['terms']:
                logging.info('term obj: ' + str(obj.term))
            
            
            
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
            
            values['css'] = ['/static/css/jquery-impromptu.css']    
            values['javascript'] = ['/static/js/jquery-impromptu.min.js','/static/js/modules/newModule.js']    
            
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
                versions.insert(0,str(i))
                i += 1
            values['versions'] = versions
            if isContributingUser() is True:
                values["contributing_user"] = "True"
            values['css'] = ['/static/css/jquery-impromptu.css']        
            values['javascript'] = ['/static/js/jquery-impromptu.min.js','/static/js/modules/newModule.js'] 
            doRender(self, 'module.html', values)
            
            
    def post(self):
        version = self.request.get("version")
        uid = self.request.get("module_version_uid")
        self.redirect('/modules/' + uid + '/' + version)

# class CompareModuleHandler(webapp2.RequestHandler):
#     """ compare a module with its previous version"""
#     def get(self):
#         if isAdministratorUser:
#             #convert a url to a list of segmented elements like ['preview','']
#             pathList = getUrlResourceList(self)
#              
#             Values = dict()
#             preValues = dict()
#             from libmodule import getModuleByKey
#              
#             
#             logging.error(pathList)
#             
#             
#             if len(pathList) < 2:
#                 logging.info('jump to the 1 branch')
#              
#             # case ['preview','keyxxxx'], which indicates the newest version   
#             elif len(pathList) == 2 and pathList[0] == 'preview':
#                 key = pathList[1]
#                 values = getModuleByKey(key)
#                 preValues = getModule(values['module_uid'])
#                 
#                 # Compare texts side by side and highlight the difference
#                 # How?
#                 if isContributingUser() is True:
#                     values["contributing_user"] = "True"
#     
#                 values['css'] = ['/static/css/jquery-impromptu.css']        
#                 values['javascript'] = ['/static/js/jquery-impromptu.min.js','/static/js/modules/newModule.js']
#                 doRender(self, 'module.html', values)
#                  
#             else:
#                 logging.info('jump to the 3 branch')
#         else:
#             logging.info('Failed to compare modules')
#     
#     def post(self):
#         pass        
        
class PreviewModuleHandler(webapp2.RequestHandler):
    """ Preview a editing module by its entity key"""
    def get(self):
        
        #convert a url to a list of segmented elements like ['preview','']
        pathList = getUrlResourceList(self)
         
        values = dict()
        from libmodule import getModuleByKey
        
        if len(pathList) < 2:
            logging.info('jump to the 1 branch')
         
        # case ['preview','keyxxxx'], which indicates the newest version   
        elif len(pathList) == 2 and pathList[0] == 'preview':
            key = pathList[1]
            values = getModuleByKey(key)
            
            if isContributingUser() is True:
                values["contributing_user"] = "True"

            values['css'] = ['/static/css/jquery-impromptu.css']        
            values['javascript'] = ['/static/js/jquery-impromptu.min.js','/static/js/modules/newModule.js']
            doRender(self, 'module.html', values)
             
        else:
            logging.info('jump to the 3 branch')
    
    
    def post(self):
        pass        
        


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
#                                ('/module/compare.*', CompareModuleHandler),
                               ('/preview/.*', PreviewModuleHandler),
                               ('/modules/page.*', MainPageHandler),
                               ('/modules', MainPageHandler),
                               ('/modules/.*', ModuleHandler)
                                ],debug=True)

