import datamodel

import logging
from libuser import getCurrentUserEntity
from libmain import createNewUID
from google.appengine.ext import db

def newTerm(term, slug, definition):
    values = dict()
    user = getCurrentUserEntity()   
    # check if a term is pre-defined
    termList = db.Query(datamodel.Term).filter('slug =', slug).fetch(limit=None)
    listLen = len(termList)
    
    if listLen == 0:
        termid = createNewUID("terms")
        termkey = datamodel.Term(word = term, slug = slug, contributor = user, uid = termid).put()
    elif listLen == 1:
        termkey = db.Query(datamodel.Term).filter('slug =', slug).get()
    else:
        values['error'] = 'there are duplicate entities in Term table'
        return values
    
    definitionid = createNewUID("definitions")
    datamodel.TermDefinition(term = termkey, definition = definition, contributor = user, uid = definitionid).put()
    
    return values

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
            defList.append((item.definition, item.date_defined))
        
        defList.sort(key=lambda item: item[1])
        
        outputList = [x[0] for x in defList]
            
        values['definitions'] = outputList
        return values
    else:
        values['error'] = 'Term not found.'
        return values
 

def getTermCount():
    """ returns the count of terms
    """
    termSet = db.Query(datamodel.Term).fetch(limit=None)
    
    if termSet:
        return len(termSet)
    else:
        return 0
    
    
def getAllTerm():
    """returns the list of terms in json format"""
    termSet = db.Query(datamodel.Term).fetch(limit=None)
    termList = []
    if termSet:
        for termObj in termSet:
            termList.append(termObj.word)
            return termList
    else:
        return ['']