import datamodel
import logging
import math
from libmain import doRender, getUrlResourceList 
import webapp2
    
from google.appengine.ext import db

# class DefineTermHandler(webapp2.RequestHandler):
#     def get(self):
#         urlList = getUrlResourceList(self)
#         try:
#             slug = str(path[2])
#             logging.error(slug)
#         except:
#             doRender(self, 'error.html', {'error' : 'Not a valid term to define'})
#             return None
#         
#         values = {'slug' : slug, 'term' : slug.replace('-',' ')}
#         doRender(self, 'newDefinition.html', values)
         
#     def post(self):
#         from libterm import newDefinition
#         slug = self.request.get('slug').strip().lower()
#         definition = self.request.get('definition').strip()
#         newDefinition(slug, definition)
#         self.redirect('/terms/'+slug, False)

    
class NewTermHandler(webapp2.RequestHandler):
    def get(self):
        doRender(self, 'newTerm.html')
    
    def post(self):
        term = self.request.get('term').strip().lower()
        term = str(term)
        definition = self.request.get('definition').strip()
        definition = str(definition)
        slug = term.replace(' ', '-')
        from libterm import newTerm
        try:
            termKey = newTerm(term, slug, definition)
        except:
            logging.error('termKey error')
        
        if not termKey:
            self.redirect('/terms')
        else:
            self.redirect('/')
            
            
class GetTermHandler(webapp2.RequestHandler):
    def get(self):
        pathList = getUrlResourceList(self)
        pathList.append('')
        pathList.append('')
        slug = pathList[1]
         
        from libterm import getTerm, getTermCount
        from libuser import isContributingUser
        values = getTerm(slug)
        values['terms_count'] = getTermCount()
        values['contributing_user'] = isContributingUser()
        values['javascript'] = ['/static/js/terms/newDef.js']
        doRender(self, 'term.html', values)
    
    def post(self):
        newDefinition = self.request.get('definition')
        slug = self.request.get('slug')
        term = slug.replace('-', ' ')
        from libterm import newTerm, getTerm
        newTerm(term, slug, newDefinition)
        
        if getTerm(slug):
            self.redirect('/contribute/term', permanent=False)
 
# display the list of terms         
class TermHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        urlList = getUrlResourceList(self)
        urlList.append('')
        urlList.append('')
        
        from libmain import RepresentsInt
        from libterm import getTermCount
           
        termCount = float(getTermCount())
 
        pageLimit = 10
        pageNumber = urlList[2]
        pageMax = math.ceil(termCount/pageLimit)
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
   
        pageList = []
        for pageN in range(pageMax):
            pageList.append(str(pageN+1))
               
        from libuser import isContributingUser
        if isContributingUser() is True:
            values['can_contribute'] = 'True'
               
        terms = db.Query(datamodel.Term).order('-date_submitted').fetch(limit=pageLimit, offset=(pageNumber-1)*pageLimit)
        values['terms_general'] = terms
        values['terms_page'] = pageList
        values['terms_count'] = int(termCount)
           
        values['javascript'] = ['/static/js/jquery.js', '/static/js/plugins/autocomplete/jquery.autocomplete.min.js', '/static/js/terms/termDefaultPage.js']
        values['css'] = ['/static/js/plugins/autocomplete/styles.css']
        doRender(self, 'termDefault.html', values)

app = webapp2.WSGIApplication([
                                ('/contribute/term.*', NewTermHandler),
#                                ('/contribute/definition.*', DefineTermHandler),
                                ('/terms/page/.*', TermHandler),
                                ('/terms/', TermHandler),
                                ('/terms/.*', GetTermHandler),
                                ('/.*', TermHandler)
                               ],debug = True)
    
