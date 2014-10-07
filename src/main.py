#main.py
#Wikitheoria Project

from libmain import doRender, sendFeedbackEmail
from libuser import getCurrentUserInfo
 
import webapp2
import datamodel
import logging

from google.appengine.ext import db
from google.appengine.ext.db import Key

class HelpHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, 'help.html', values)
        
class AboutHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, 'about.html', values)

class ContributeHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, 'contribute.html', values)

class ContactHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, 'contact.html', values)

class FeedbackHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        doRender(self, 'feedback.html', values)
    def post(self):
        userInfo = getCurrentUserInfo()
        aSubject = userInfo['user_name'] + " left feedback for The Wikitheoria Project development site"
        aBody = self.request.get("body")
        sendFeedbackEmail(userInfo["email"], aSubject, aBody)
        self.redirect('/')

class NotifyHandler(webapp2.RequestHandler):
    def post(self):
        title = self.request.get("title")
        message = self.request.get("message")
        modKey = self.request.get("modKey")
        modKey = Key(modKey)
        # change the status of module
        modObj = db.Query(datamodel.Module).filter("__key__ =", modKey).get()
        modObj.status = "flag"
        key = db.put(modObj)
        
        aSubject = "Module " + title + " is waiting for your approval"
        aBody = "Module:" + title + "\nContributor's Proposal Suggestion:" + message
        
        sendFeedbackEmail("wikitheoria.public@gmail.com", aSubject, aBody)

class NotifyHandler2(webapp2.RequestHandler):
    def post(self):
        title = self.request.get("title")
        message = self.request.get("message")
        modKey = self.request.get("modKey")
        modKey = Key(modKey)
        # change the status of module
        modObj = db.Query(datamodel.Module).filter("__key__ =", modKey).get()
        modObj.status = "reviewed"
        key = db.put(modObj)        
        
        email = self.request.get("email")
        aSubject = "Feedback: Module " + title 
        aBody = "Module:" + title + "\nFeedback Suggestion:" + message
        
        from google.appengine.api import mail
        
        mail.send_mail("wikitheoria.public@gmail.com", email, aSubject, aBody)
        

class JoinHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
        userInfo = getCurrentUserInfo()
        if userInfo['isUser'] is 'True':
            values = userInfo
        
        doRender(self, 'join.html', values)
            
    # Test! Create a branch to block non-contributor
    def post(self):
        email = self.request.get("email")
        name = self.request.get("name")
        organization = self.request.get("organization")
        title = self.request.get("title")
        note = self.request.get("note")
        aSubject = name + " would like to become a member of Wikitheoria -- Needs Authorization"
        aBody = "name: " + name + "\nEmail: " + email + "\nOrganization: " + organization + "\nTitle: " + title + "\n\n" + note
        sendFeedbackEmail(email, aSubject, aBody)
        self.redirect('/')

class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        values = dict()
#         from modules import getFeaturedModule
#        from articles import getFeaturedArticle
        from google.appengine.api import memcache
        
#        import markdown
#        logging.error(markdown.markdown("test markdown"))
        
        #########Memcache featured module
        featuredModule = memcache.get("featuredModule") #@UndefinedVariable
        if featuredModule is None:
#             featuredModule = getFeaturedModule()
            if not memcache.add("featuredModule", featuredModule, 60): #@UndefinedVariable
                logging.error("Memcache set failed.")
        #########end Memcache featured module
        
        #########Memcache featured article
#         featuredArticle = memcache.get("featuredArticle") #@UndefinedVariable
#         if featuredArticle is None:
#             featuredArticle = getFeaturedArticle()
#             if not memcache.add("featuredArticle", featuredArticle, 60): #@UndefinedVariable
#                 logging.error("Memcache set failed.")
        #########end Memcache featured article
        
        if featuredModule.has_key('error'):
                values['module_error'] = 'No module currently featured'
        else:
            for key in featuredModule:
                values[key] = featuredModule[key]
                
#         if featuredArticle.has_key('error'):
#             values['article_error'] = 'No article currently featured'
#         else:
#             for key in featuredArticle:
#                 values[key] = featuredArticle[key]
        
        doRender(self, 'index.html', values)

class MainPageRedirecter(webapp2.RequestHandler):
    def get(self):
        user = self.request.get('usr')
        if user == 'newUser':
            self.redirect('/#mainTopContent')
        elif user == 'experienced':
            self.redirect('/#mainMiddleContent')
        else:
            self.redirect('/')
    
    def post(self):
        pass        

class MainPageHandler2(webapp2.RequestHandler):
    def get(self):
        values = dict()
        
        preziObj = db.Query(datamodel.Prezis).filter('current_tag =', True).get()
        if preziObj:
            
            values['title1'] = preziObj.title_1
            values['pic1'] = preziObj.pic_1
            values['link1'] = preziObj.link_1
            
            values['title2'] = preziObj.title_2
            values['pic2'] = preziObj.pic_2
            values['link2'] = preziObj.link_2
            
            values['title3'] = preziObj.title_3
            values['pic3'] = preziObj.pic_3
            values['link3'] = preziObj.link_3
            
            values['title4'] = preziObj.title_4
            values['pic4'] = preziObj.pic_4
            values['link4'] = preziObj.link_4        
        
        else:
            pass
        
        values['css'] = ['/static/css/jquery-impromptu.css','/static/css/jquery.orgchart.css']
        values['javascript'] = ['/static/js/jquery-impromptu.min.js',
                                '/static/js/jquery.orgchart.min.js',
                                '/static/js/index/index.js',
                                ]
        wwObj = db.Query(datamodel.WikiWords).get()
        if wwObj:
            values['html2'] = wwObj.wwHtml
        else:
            values['html2'] = "Wiki in Words coming soon..."
       
        
        newsObj = db.Query(datamodel.News).get()
        if newsObj:
            values['html'] = newsObj.newsHtml
        else:
            values['html'] = "News coming soon..."
        
        doRender(self, 'index2.html', values)
        
app = webapp2.WSGIApplication([
                                          ('/help.*', HelpHandler),
                                          ('/about.*', AboutHandler),
                                          ('/contribute.*', ContributeHandler),
                                          ('/feedback.*', FeedbackHandler),
                                          ('/contact.*', ContactHandler),
                                          ('/notify2.*', NotifyHandler2),
                                          ('/notify.*', NotifyHandler),
                                          ('/join.*', JoinHandler),
                                          ('/main', MainPageRedirecter),
                                          ('/.*', MainPageHandler2)
                                          ],debug = True)
    

