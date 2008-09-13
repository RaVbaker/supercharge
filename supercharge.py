#!/usr/bin/env python
#
# AppEngine with SuperCharge - The light MVC framework for Google AppEngine
#
# Copyright 2008 Rafal "RaVbaker" Piekarski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#




# framework Webapp libs
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp

# python libs
import re
import os
from os import listdir

# Google AppEngine APIs
from google.appengine.api import users

# framework SuperCharge configuration
from sc_cfg import *

class Dispatcher(webapp.RequestHandler):

  def put(self, uri):
    self.__handleRequest('put', uri)

  def delete(self, uri):
    self.__handleRequest('delete', uri)
      
  def post(self, uri):
    self.__handleRequest('post', uri)
  
  def get(self, uri):
    self.__handleRequest('get', uri)
    
    
  def __handleRequest(self, type, uri):
    self.request_type = type
    self.__setRequestData(uri)
    try:
      self.__checkControllerExistness()
      self.__executeRequest()
    except PageNotFoundError:
      self.__showError404()
    finally:
      self.__showDebugBar()
  
  def __showError404(self):
    self.error(404)
    self.response.out.write("<h1>Error 404</h1><p>Page not found</p>")
  
  def __showDebugBar(self):
    self.response.out.write("<div style='border: 3px solid #999;background-color: #f0f0f0;'><u><strong>DEBUG:</strong></u> URL: <strong>%s</strong> \t controller: <strong>%s</strong> \t action: <strong>%s</strong></div>\n"%(self.request.uri, self.controller, self.action))
  
  def __executeRequest(self):
    
    exec("from controllers.%s import %s" % (self.controller,self.className))
    exec("page = %s(self)" % (self.className))  
    
    page.handleAction(self.action)
  
  def __setRequestData(self, uri):
    
    path = self.__getRequestPath(uri)
    self.controller, self.action = path[0], path[1]
    self.className = self.controller.capitalize()
    
    #sets params dict:
    self.params = dictalize_list(path[2:])
    self.params.update(dict([(k, self.request.get(k)) for k in self.request.arguments()]))
  
  def __getRequestPath(self, uri):
    path = uri.split('/')
    
    if '' == uri:
      path = [Root_empty_controller]
    elif self.__matchInRoutes(uri):
      path = self.matchedPath
      
    if 1 == len(path) or path[1] == '':
      path.insert(1,'index')
      
    return path
    
  def __matchInRoutes(self, uri):
    for route in Routes:
      rule, base_path = route
      matched = re.match(rule, uri)
      if matched:
        self.matchedPath = base_path+list(matched.groups())
        return True
  
  def __checkControllerExistness(self):
    controllers_list = listdir('./controllers')
    controllers_list.remove('__init__.py')
    if 0 == controllers_list.count(self.controller+'.py'):
      raise PageNotFoundError(self)
    
class PageNotFoundError:
  def __init__(self, data):
    self.data = data
  
  def __str__(self):
    return str(self.data)

class View:
  def __init__(self, controller_name, view_name):
    self.__setPath(controller_name, view_name)
    
    
  def output(self):
    self.__getView(self.path)
    return ''
  def __getView(self, path):
    pass
  
  def __setPath(self, controller_name, view_name):
    self.path = "views/%s/%s.html" % (controller_name, view_name)


class Controller:
  
  def __init__(self, dispatch):
    self.p = dispatch
    self.view = dispatch.action
  
  def handleAction(self, action):

    #check thats this page has remaining method and is not in internal Controller methods list
    if action == 'handleAction' or 0 == dir(self).count(action) or 1  == dir(Controller).count(action):
      raise PageNotFoundError(self)
    
    self.beforeExecute()
    exec("self.%s()" % action)
    self.afterExecute()
    self.__show()
  
  def render(self, content, type='html'):
    Types = {
      'html': 'text/html',
      'text': 'text/plain'
    }
    self.p.response.headers['Content-Type'] = Types[type]
    self.p.response.out.write(content)
  
  def redirect(self, url):
    self.p.redirect(url)
  
  def getParam(self, id):
    return self.p.params[id]
  
  def getParams(self):
    return self.p.params
    
  def getRequest(self):
    return self.p.request
  
  def getResponse(self):
    return self.p.response
    
  def loginUser(self):
    self.redirect(users.create_login_url(self.p.request.uri))
    
  def logoutUser(self):
    self.redirect(users.create_logout_url(self.p.request.uri))
    
  def __show(self):
    """Shows selected view. If you want to disable view, please set 'view' to empty string"""
    code = ''
    if(self.view):
      self.viewObj = View(self.p.controller, self.view)
      code = self.viewObj.output()
    
    self.render(code, 'html')
  
  def beforeExecute(self):
    """It executed before whole request. Great for setting variables available in whole controller"""
    pass
  
  def afterExecute(self):
    """It executed after whole request. Great for sending some data"""
    pass



def main():
  application = webapp.WSGIApplication([(r'/(.*)', Dispatcher)],debug=True)
  run_wsgi_app(application)
  
def dictalize_list(l=[]):
  """makes a dictionary from argument l which is a list"""
  return dict([(l.index(i), i) for i in l])


if __name__ == '__main__':
  main()
