#from main import getUrlResourceList, doRender, getCurrentUserEntity, createNewUID
from libmain import doRender, getUrlResourceList
from libmodule import newModule, getUnpublishedModules, getModuleVersion, getModuleVersionCount
from libuser import isContributingUser

import webapp2

import datamodel
import logging
from google.appengine.ext import db


# create a new module
class NewModuleHandler(webapp2.RequestHandler):
    def get(self):

        values = dict()
        # test if the currentUser is a contributing user.
        if isContributingUser() is True:
            values['javascript'] = ['/static/js/jquery.js', 
                                    '/static/js/plugins/autocomplete/jquery.autocomplete.min.js', 
                                    '/static/js/modules/newModule.js',
                                    '/static/js/plugins/wmd_stackOverflow/wmd.js', 
                                    '/static/js/plugins/wmd_stackOverflow/showdown.js']
            values['css'] = ['/static/js/plugins/autocomplete/styles.css', 
                             '/static/css/modules.css', 
                             '/static/js/plugins/wmd_stackOverflow/wmd.css']
             
            doRender(self, 'newModule.html',values)
             
        else:
            doRender(self, 'join.html',values)
   
    def post(self):
        title = self.request.get("title")
        keywords = self.request.get("keywords")
        scopeList = self.request.get_all("scopes")
        propositionList = self.request.get_all("propositions")
        derivationList =  self.request.get_all("derivations")
        evidence = self.request.get("evidence")
        markdown = self.request.get("markdown")
        publishBool = self.request.get("published")
         
        #using newModule in libmodule.py
        modKey = newModule(title, keywords, markdown, scopeList, propositionList, derivationList, evidence, publishBool)
         
        #terms related processing
#         terms = self.request.get_all("terms")
#         definitions = self.request.get_all("definitions")
#          
#         while terms:
#             term = terms.pop().lower()
#             definition = definitions.pop()
#              
#             termKey = db.Query(datamodel.Term).filter('word =', term).get()
#             if termKey:
#                 defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
#                 if not defKey:
#                     from terms import newDefinition
#                     defKey = newDefinition(termKey.slug, definition)
#             else:
#                 from terms import newTerm
#                 newTerm(term, term, definition)
#                 termKey = db.Query(datamodel.Term).filter('word =', term).get()
#                 defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
#              
#             datamodel.ModuleTerm(module = modKey, term = termKey, definition = defKey).put()
        
        if modKey != -1:
            self.redirect("/modules/", True)
        else:
            values = {'error' : 'Failed to create module. Please try again later.'}
            doRender(self, 'error.html', values)
        
# class EditModuleHandler(webapp2.RequestHandler):
#     def get(self):
#         from libuser import isContributingUser
#         if isContributingUser() is True:
#             values = dict()
#             url = getUrlResourceList(self)
#             values = getModule(url[2])
#             values['javascript'] = ['/static/js/jquery.js', '/static/js/plugins/autocomplete/jquery.autocomplete.min.js', '/static/js/modules/newModule.js',
#                                     '/static/js/plugins/wmd_stackOverflow/wmd.js', '/static/js/plugins/wmd_stackOverflow/showdown.js']
#             values['css'] = ['/static/js/plugins/autocomplete/styles.css', '/static/css/modules.css', '/static/js/plugins/wmd_stackOverflow/wmd.css']
#             doRender(self, 'editModule.html', values)
#         else:
#             self.redirect('/modules/')
#              
#     def post(self):
#         title = self.request.get("title")
#         metaTheory = self.request.get("meta_theory")
#         scopeList = self.request.get_all("scopes")
#         propositionList = self.request.get_all("propositions")
#         markdown = self.request.get("markdown")
#         discipline = self.request.get("discipline")
#         publishBool = self.request.get("published")
#         uid = int(self.request.get("uid"))
#          
#          
#         modKey = updateModule(uid, title, metaTheory, markdown, scopeList, propositionList, discipline, publishBool)
#                                
#         #terms
#         terms = self.request.get_all("terms")
#         definitions = self.request.get_all("definitions")
#         functions = self.request.get_all("functions")
#          
#         while terms:
#             term = terms.pop().lower()
#             definition = definitions.pop()
#             function = functions.pop()
#              
#             termKey = db.Query(datamodel.Term).filter('word =', term).get()
#             if termKey:
#                 defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
#                 if not defKey:
#                     from terms import newDefinition
#                     defKey = newDefinition(termKey.slug, function, definition)
#             else:
#                 from terms import newTerm
#                 newTerm(term, term, function, definition)
#                 termKey = db.Query(datamodel.Term).filter('word =', term).get()
#                 defKey = db.Query(datamodel.TermDefinition).filter('definition =', definition).filter('term =', termKey).get()
#              
#             datamodel.ModuleTerm(module = modKey, term = termKey, definition = defKey).put()
#              
#         if modKey != -1:
#             self.redirect("/modules", True)
#         else:
#             values = {'error' : 'Failed to update module. Please try again later.'}
#             doRender(self, 'error.html', values)


#display specified module 
class ModuleHandler(webapp2.RequestHandler):
    def get(self):
        #convert a url to a list of segmented elements like ['modules','']
        pathList = getUrlResourceList(self)
        
        values = dict()
        
        if len(pathList) == 1:
            values['error'] = "url does not contain any module number"
            doRender(self, 'moduleDefault.html', values)
        
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
        if isContributingUser() is True:
            values['can_contribute'] = 'True'
            unpublishedModules = getUnpublishedModules()
            values['unpublished_modules'] = unpublishedModules
        modules = db.Query(datamodel.Module).filter('current =', True).filter('published =', True).order('-date_submitted').fetch(10)
        values["ten_newest_modules"] = modules

        values['javascript'] = ['/static/js/jquery.js', '/static/js/modules/moduleDefault.js']
             
        doRender(self, 'moduleDefault.html', values)
        
app = webapp2.WSGIApplication([
#                                ('/module/edit.*', EditModuleHandler),
                               ('/module/new.*', NewModuleHandler),
                               ('/modules/?', MainPageHandler),
                               ('/modules/.*', ModuleHandler)
                                ],debug=True)

