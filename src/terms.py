import datamodel
import logging
import math
from libmain import doRender, getUrlResourceList 
import webapp2
    
from google.appengine.ext import db

class CleanTermHandler(webapp2.RequestHandler):
    def get(self):
        pass
        
    def post(self):
        pass  

class NewTermHandler(webapp2.RequestHandler):
    def get(self):
        doRender(self, 'newTerm.html')
    
    def post(self):
        values = dict()
        term = self.request.get('term').strip().lower()
        term = str(term)
        definition = self.request.get('definition').strip()
        definition = str(definition)
        
        logging.info("########"+ term + "########" + definition + "######")
        
        if term == '' or definition == '':
            values['errors'] = 'term and definition cannot be empty.'
            doRender(self, 'newTerm.html', values)
        else:
            slug = term.replace(' ', '-')
            from libterm import newTerm
            try:
                termKey = newTerm(term, slug, definition)
            except:
                logging.error('termKey error')
        
            if termKey:
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

class GetTermListHandler(webapp2.RequestHandler):
    def get(self):
        termSet = db.Query(datamodel.Term).fetch(limit=None)
        termList = []
        if termSet:
            for termObj in termSet:
                termList.append(termObj.word)
            
        termdict = {"termlist": termList}
        import json
        jsonObj = json.dumps(termdict)    
            
        self.response.out.write(jsonObj)
        
    
    def post(self):
        pass
 
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
           
        values['javascript'] = ['/static/js/jquery-1.9.1.js', 
                                '/static/js/jquery-ui.js',
                                '/static/js/terms/termDefaultPage.js']
        values['css'] = ['/static/js/jquery-ui.css']
        doRender(self, 'termDefault.html', values)

app = webapp2.WSGIApplication([
                                ('/contribute/term.*', NewTermHandler),
                                ('/terms/page/.*', TermHandler),
                                ('/terms/', TermHandler),
                                ('/terms/get', GetTermListHandler),
                                ('/terms/clean', CleanTermHandler),
                                ('/terms/.*', GetTermHandler),
                                ('/.*', TermHandler)
                               ],debug = True)
    
