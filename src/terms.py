import datamodel
import logging
from libmain import doRender, getUrlResourceList, createNewUID 
from libuser import getCurrentUserEntity
import webapp2

from google.appengine.ext import db

def getTerm(slug):
    values = dict()    
    try:
        slug = str(slug)
    except:
        values['error'] = 'Not a valid term. Please check the term in the URL.'
        return values
    term = db.Query(datamodel.Term).filter('slug =', slug).get()
    if term:
        values['slug'] = slug
        values['term'] = term.word
        defList = list()
        for item in term.termdefinition_set:
            defList.append(item.definition)
        values['definitions'] = defList
        return values
    else:
        values['error'] = 'Term not found.'
        return values

def newDefinition(slug, definition):
    try:
        termObject = db.Query(datamodel.Term).filter('slug =', slug).get()
    except:
        return False
    if termObject:
        user = getCurrentUserEntity() 
        uid = createNewUID("definitions")
        if uid == -1:
            return False
        try:
            defKey = datamodel.TermDefinition(term = termObject, definition = definition, popularity = 0, contributor = user, uid = uid).put()
            return defKey
        except:
            logging.error('Failed to add definition. Term:' + termObject.word)
            return False
        return True
    else:
        return False
 
def newTerm(term, slug, definition):
    values = dict()
    try:
        existingTerm = db.Query(datamodel.Term).filter('slug =', slug).get()
    except:
        values['error'] = 'Could not create a new term'
        return values
    if existingTerm:
        if not newDefinition(slug, definition):
            values['error'] = 'The term already exists and failed to save the definition.'
            return values
        else:
            values['error'] = 'Term already exists. The definition was added to the existing term.'
            return values
    else:
        try:
            user = getCurrentUserEntity() 
            uid = createNewUID("terms")
            if uid == -1:
                values['error'] = 'Could not create a new term!'
                return values
            datamodel.Term(word = term, slug = slug, contributor = user, uid = uid).put()
        except:
            values['error'] = 'Could not create a new term!'
            return values
        if not newDefinition(slug, definition):
            values['error'] = 'The term was created but failed to save the definition.'
            return values
        else:
            return {'error' : ''}
    
class DefineTermHandler(webapp2.RequestHandler):
    def get(self):
        path = getUrlResourceList(self)
        try:
            slug = str(path[2])
        except:
            doRender(self, 'error.html', {'error' : 'Not a valid term to define'})
            return None
        values = {'slug' : slug, 'term' : slug.replace('-', ' ')}
        doRender(self, 'newDefinition.html', values)
        
    def post(self):
        slug = self.request.get('slug').strip().lower()
        definition = self.request.get('definition').strip()
        newDefinition(slug, definition)
        self.redirect('/terms/'+slug, False)
    
class NewTermHandler(webapp2.RequestHandler):
    def get(self):
        doRender(self, 'newTerm.html')
    
    def post(self):
        term = self.request.get('term').strip().lower()
        definition = self.request.get('definition').strip()
        #slug = term
        slug = term.replace(' ', '-')
        values = newTerm(term, slug, definition)
        if not values['error'] == '':
            doRender(self, 'error.html', values)
            return None
        else:
            self.redirect('/terms/'+slug, False)
        
class TermHandler(webapp2.RequestHandler):
    def get(self):
        pathList = getUrlResourceList(self)
        values = dict()
        from users import isContributingUser
        if isContributingUser() is True:
            values['can_contribute'] = 'True'
        terms = db.Query(datamodel.Term).order('-date_submitted').fetch(10)
        values["ten_newest_terms"] = terms
        if len(pathList) == 1 or pathList[1] == '':
            values['javascript'] = ['/static/js/jquery.js', '/static/js/plugins/autocomplete/jquery.autocomplete.min.js', '/static/js/terms/termDefaultPage.js']
            values['css'] = ['/static/js/plugins/autocomplete/styles.css']
            doRender(self, 'termDefault.html', values)
        else:
            slug = pathList[1]
            values = getTerm(slug)
            doRender(self, 'term.html', values)

app = webapp2.WSGIApplication(
                                         [('/contribute/term.*', NewTermHandler),
                                          ('/contribute/definition.*', DefineTermHandler),
                                          ('/.*', TermHandler)],
                                          debug = True)
    
