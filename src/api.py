from libmain import doRender, createNewUID, decrementCounter
import datamodel
import logging
import json
from libuser import isContributingUser, isAdministratorUser
import webapp2
from google.appengine.ext import db


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
   



class ApiHandler(webapp2.RequestHandler):
    def get(self):

        if self.request.get('method') == 'getTermDefinitions':
            getTermDefinitions(self)
            return
        
        else:
            pass


class MarkdownHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()



app = webapp2.WSGIApplication(
                                         [('/api/markdown.*', MarkdownHandler),
                                          ('/api.*', ApiHandler)],
                                          debug=True)
