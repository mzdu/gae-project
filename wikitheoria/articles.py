from main import getUrlResourceList, doRender, getCurrentUserEntity, createNewUID, isLoggedIn
import datamodel
import logging

from django.template.defaultfilters import slugify 
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

def getArticleCount():
    countObject = db.Query(datamodel.Counter).filter("name = ", "articles").get()
    if countObject:
        return countObject.count
    else:
        return 0

def getArticleEntity(uid):
    ''' @summary: Returns an Article object from the datastore
        @param uid: The uid that describes the article to get from the datastore
        @type uid: String (later typecasted to an int)
        @return: Returns an Article object
        @rtype: Article
    '''
    try:
        uid = int(uid)
    except:
        return None
    que = db.Query(datamodel.Article).filter('uid =', uid)
    articleObject = que.get()
    if articleObject:
        return articleObject
    return None

def getFeaturedArticle():
    ''' @summary: Populates a dictionary with the featured article's values from the datastore for use in a Django template
        @return: Returns a dictionary containing article entity data
        @rtype: dictionary
    '''
    values = dict()
    que = db.Query(datamodel.FeaturedArticle)
    que.order('-featured_date')
    articleObject = que.get()
    if articleObject:
        values['article_title_general'] = articleObject.article.title
        values['article_author_general'] = articleObject.article.author.alias
        values['article_date_pub_general'] = '%02d/%02d/%04d' % (articleObject.article.date_pub.month, articleObject.article.date_pub.day, articleObject.article.date_pub.year)
        values['article_url'] = '/articles/' + str(articleObject.article.uid) + '/' + slugify(articleObject.article.title)
        values['article_body_general'] = articleObject.article.body[0:500] + "<a href=" + values['article_url'] + ">Read More...</a>"
        values['article_uid'] = articleObject.article.uid
    else:
        values['error'] = 'Featured article not found'
    return values

def getArticles():
    ''' @summary: Returns all Articles from the datastore ordered by date published
        @return: Returns an Article object containing all articles  
        @rtype: Article
    '''
    que = db.Query(datamodel.Article)
    que.order('-date_pub')
    articles = que.fetch(50)
    return articles

def getArticle(uid):
    ''' @summary: Populates a dictionary with a particular article's values from the datastore for use in a Django template
        @param uid: The uid that describes the article to get from the datastore
        @type uid: String (later typecasted to an int)
        @return: Returns a dictionary containing article entity data
        @rtype: dictionary
    '''
    values = dict()
    try:
        uid = int(uid)
    except:
        values['error'] = 'Article id\'s are numeric. Please check the URL.'
        return values
    que = db.Query(datamodel.Article).filter('uid =', uid)
    articleObject = que.get()
    if articleObject:
        values['article_title_general'] = articleObject.title
        values['article_author_general'] = articleObject.author.alias
        values['article_date_pub_general'] = '%02d/%02d/%04d' % (articleObject.date_pub.month, articleObject.date_pub.day, articleObject.date_pub.year)
        values['article_body_general'] = articleObject.body
        values['article_url'] = '/articles/' + str(articleObject.uid) + '/' + slugify(articleObject.title)
        values['article_uid'] = articleObject.uid
    else:
        values['error'] = 'Article does not exist'
    return values

def newArticle(title, markdown):
    ''' @summary: Creates a new article entity 
        @param title, body
        @type String
        @return: Returns the uid if successful, else -1
        @rtype: integer
    '''
    from main import parseMarkdown
    html = parseMarkdown(markdown)
    uid = createNewUID("articlesUID")
    if uid == -1:
        return -1
    else:
        user = getCurrentUserEntity()    
        try:
            article = datamodel.Article(title = title,uid = uid, version = 1,author = user,body = html, markdown = markdown)
            article.put()
            createNewUID("articles") #increments the overall module counter once the module is published
            return uid
        except:
            logging.error('Failed to create article. Article uid:' + str(uid))
            return -1


class NewArticleHandler(webapp.RequestHandler):
    def get(self):
        values = dict()
        values['javascript'] = ["/static/js/articles/newArticle.js",'/static/js/jquery.js', '/static/js/plugins/wmd_stackOverflow/wmd.js', '/static/js/plugins/wmd_stackOverflow/showdown.js']
        values['css'] = ['/static/js/plugins/wmd_stackOverflow/wmd.css']
        
        doRender(self, 'articles/newArticle.html',values)
        return
  
    def post(self):
        uid = newArticle(self.request.get("title"),
                    self.request.get("body")
                    )
        if uid != -1:
            self.redirect("/articles/" + str(uid), True)
        else:
            values = {'error' : 'Failed to create article. Please try again later.'}
            doRender(self, 'error.html', values)

class ArticleHandler(webapp.RequestHandler):
    def get(self):
        from users import isContributingUser
        pathList = getUrlResourceList(self)
        values = dict()
        if isContributingUser() is True:
            values['can_contribute'] = 'True'
        articles = db.Query(datamodel.Article).order('-date_pub').fetch(10)
        values["ten_newest_articles"] = articles
        if len(pathList) == 1 or pathList[1] == '':
            values['javascript'] = ['/static/js/jquery.js', '/static/js/articles/articleDefault.js']
            doRender(self, 'articles/articleDefault.html', values)
        else:
            values = getArticle(pathList[1])
            if isLoggedIn() is True:
            	values["logged_in"] = "True"
            values["javascript"] = "/static/js/jquery.js","/static/js/articles/main.js", "/static/js/rounded_corners.inc.js"
            doRender(self, 'articles/article.html', values)

class DefaultHandler(webapp.RequestHandler):
    def get(self):
        values = dict()
        articles = db.Query(datamodel.Article).order('-date_pub').fetch(10)
        values["ten_newest_articles"] = articles
        
        doRender(self, 'article/articleDefault.html', values) 
    
def main():
    application = webapp.WSGIApplication(
                                         [('/article/new.*', NewArticleHandler),
                                          ('/articles.*', ArticleHandler)],
                                          debug=True)
    run_wsgi_app(application)


if __name__ == "__main__":
    main()


