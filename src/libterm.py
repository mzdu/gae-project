import datamodel

import logging
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

def getTermCount():
    countObject = db.Query(datamodel.Counter).filter("name = ", "terms").get()
    if countObject:
        return countObject.count
    else:
        return 0

def newDefinition(slug, definition):
    
    from libuser import getCurrentUserEntity
    from libmain import createNewUID
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
    
    from libuser import getCurrentUserEntity
    from libmain import createNewUID
    
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
 