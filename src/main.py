#main.py
#Wikitheoria Project

from libmain import doRender, sendFeedbackEmail
from libuser import getCurrentUserInfo
 
import webapp2
import logging


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
        doRender(self, 'feedback.html', values)

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
        note = self.request.get("note")
        aSubject = name + " would like to become a member of Wikitheoria -- Needs Authorization"
        aBody = "name: " + name + "\nEmail: " + email + "\n\n" + note
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
        values['css'] = ['/static/css/jquery-impromptu.css','/static/css/jquery.orgchart.css']
        values['javascript'] = ['/static/js/jquery-impromptu.min.js',
                                '/static/js/jquery.orgchart.min.js',
                                '/static/js/index/index.js',
                                ]
        
        doRender(self, 'index2.html', values)
        
app = webapp2.WSGIApplication([
                                          ('/help.*', HelpHandler),
                                          ('/about.*', AboutHandler),
                                          ('/contribute.*', ContributeHandler),
                                          ('/feedback.*', FeedbackHandler),
                                          ('/contact.*', ContactHandler),
                                          ('/join.*', JoinHandler),
                                          ('/main', MainPageRedirecter),
                                          ('/.*', MainPageHandler2)
                                          ],debug = True)
    

