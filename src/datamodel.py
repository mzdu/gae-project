#Database models used in Wikitheoria
#Note: Organization of these classes is important for ReferenceProperty() to function

#TODO: add (indexed=False) to a lot of these.

from google.appengine.ext import db

class Counter(db.Model):
    name = db.StringProperty()
    count = db.IntegerProperty()

#defines a WikiUser object for the datastore
class WikiUser(db.Model):
    alias = db.StringProperty(required=True)
    user_name = db.StringProperty(required=True)
    email = db.EmailProperty()
    real_name = db.StringProperty()
    location = db.StringProperty()
    admin = db.BooleanProperty()
    organization = db.StringProperty()
    birthday = db.DateTimeProperty()
    about = db.StringProperty()
    user_id = db.StringProperty()
    user_object = db.UserProperty(auto_current_user=True)
    join_date = db.DateProperty(auto_now_add=True)
    uid = db.IntegerProperty(required=True)
    
class Module(db.Model):
    title = db.StringProperty()
    keywords = db.StringProperty()
    theoryMarkdown = db.TextProperty()
    theoryHtml = db.TextProperty()
    uid = db.IntegerProperty()
    version = db.IntegerProperty()
    scope = db.StringListProperty()
    propositions = db.StringListProperty()
    derivations = db.StringListProperty()
    evidence = db.TextProperty()

    date_submitted = db.DateTimeProperty(auto_now_add=True)
    last_update = db.DateTimeProperty(auto_now=True)
    
    
    contributor = db.ReferenceProperty(WikiUser)
    editors = db.ListProperty(db.Key)
    
    published = db.BooleanProperty()
    current = db.BooleanProperty()
    
    
 
class VersionCounter(db.Model):
    module = db.IntegerProperty()
    count = db.IntegerProperty()
 
# class ModuleVersion(db.Model):
#     module = db.ReferenceProperty(Module)
#     version = db.IntegerProperty()
#     meta_theory = db.TextProperty()
#     scope = db.StringListProperty()
#     propositions = db.StringListProperty()
#     # no need for version 150
# #    discipline = db.StringProperty(choices = ('Sociology', 'Psychology', 'Political Science'))
#     date_submitted = db.DateTimeProperty(auto_now_add=True)
#     title = db.StringProperty()
#     contributor = db.ReferenceProperty(WikiUser)
#     
#     # extended module attributes for version 150
#     keywords = db.StringProperty()
#     derivations = db.StringListProperty()
#     evidence = db.StringListProperty()
# 
# #One Term to many TermDefinitions
# class Term(db.Model):
#     word = db.StringProperty(required=True)
#     slug = db.StringProperty(required=True)
#     popularity = db.IntegerProperty()
#     date_submitted = db.DateTimeProperty(auto_now_add=True)
#     contributor = db.ReferenceProperty(WikiUser)
#     uid = db.IntegerProperty()
#     
# #Many TermDefinitions to one Term
# class TermDefinition(db.Model):
#     term = db.ReferenceProperty(Term)
#     definition = db.StringProperty()
#     
#     # no need for version150
# #    function = db.StringProperty(choices = ('noun', 'verb', 'pronoun', 'adjective', 'adverb', 'preposition', 'conjunction', 'interjection', 'nounPhrase', 'verbPhrase', 'prepositionalPhase', 'adjectivalPhrase', 'adverbialPhrase'))
#     popularity = db.IntegerProperty()
#     discipline = db.StringProperty()
#     date_defined = db.DateTimeProperty(auto_now_add=True)
#     contributor = db.ReferenceProperty(WikiUser)
#     uid = db.IntegerProperty()
#     
# #Describes the terms for particular modules
# class ModuleTerm(db.Model):
#     module = db.ReferenceProperty(Module)
#     term = db.ReferenceProperty(Term)
#     definition = db.ReferenceProperty(TermDefinition)
#     abbreviation = db.StringProperty()
# 
# class ModuleComment(db.Model):
#     uid = db.IntegerProperty()
#     user = db.ReferenceProperty(WikiUser)
#     module = db.ReferenceProperty(Module)
#     comment = db.TextProperty()
#     comment_date = db.DateTimeProperty(auto_now_add=True)
# 
# class NotifyFeedbackUser(db.Model):
#     user = db.StringProperty()
#     email = db.StringProperty()
# 
# class FeaturedModule(db.Model):
#     module = db.ReferenceProperty(Module)
#     featured_date = db.DateTimeProperty(auto_now_add=True)
 
class AdministratorUser(db.Model):
    user = db.ReferenceProperty(WikiUser)
     
class ContributingUser(db.Model):
    user = db.ReferenceProperty(WikiUser)
#     
# class ApiKey(db.Model):
#     hash = db.StringProperty()
#     creationTime = db.TimeProperty()
#     user = db.ReferenceProperty(WikiUser)
#     nonce = db.IntegerProperty()
#     locked = db.BooleanProperty()
#     
# class ApiHitTimer(db.Model):
#     apiKey = db.ReferenceProperty(ApiKey)
#     count = db.IntegerProperty()
#     timeStamp = db.TimeProperty()
    