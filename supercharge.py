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
  """ Handle an exception for none existing page
      
      self.data contains the controller based object
  """
  def __init__(self, data):
    self.data = data
  
  def __str__(self):
    return str(self.data)

class View:
  def __init__(self, controller_name, view_name):
    """ Initialize class and sets main path for view response"""
    self.__setLayoutPath(controller_name)
    self.__setPath(controller_name, view_name)
    
  def output(self, variables):
    """returns an output content from view"""
    output = self.__getView(self.path)
    
    # sets content to layout
    output = self.__setVariables({'yield': output}, self.__getLayout())
    # sets variables to site
    output = self.__setVariables(variables, output)
    
    return output
    
  def __getLayout(self):
    layout = self.__getView(self.layout_path)
    if layout == '':
      layout = '{{yield}}'
    return layout
    
  def __setVariables(self, variables_dict, content):
    """sets variables to content specified by {{variable_name}} dict"""
    for pattern in variables_dict:
        content = content.replace("{{%s}}"%pattern, str(variables_dict[pattern]))
    return content
    
  def __getView(self, path):
    """Returns view fetched from file in /views folder"""

    if(os.path.exists(path)):
      f= file(path)
      return "".join(f.readlines())
    return ''
  
  def __setPath(self, controller_name, view_name):
    """Sets a path for tempalate file"""
    self.path = "./views/%s/%s.html" % (controller_name, view_name)
  
  def __setLayoutPath(self, controller_name):
    """Sets a path for layout file"""
    layout = 'application'
    if controller_name:
      layout = controller_name
    self.layout_path = "./views/%s.html" % layout


class Controller:
  
  output_vars = {}
  
  def __init__(self, dispatch):
    """Initialize Controller class with setting base dispatcher data to self.p and view for response using View class"""
    self.p = dispatch
    self.view = dispatch.action
  
  def handleAction(self, action):
    """This method handles calling valid action method in Controller based child class"""
    #check thats this page had remaining method and is not in internal Controller methods list
    if 0 == dir(self).count(action) or 1  == dir(Controller).count(action):
      raise PageNotFoundError(self)
    
    self.beforeExecute()
    exec("self.%s()" % action)
    self.afterExecute()
    self.__show()
  
  def render(self, content, type='html'):
    """Renders specific content based on type from second argument and a dictionary Types, which 
    contains allowed one. Defauld render the 'html' response"""
    Types = {
      'html': 'text/html',
      'text': 'text/plain'
    }
    self.p.response.headers['Content-Type'] = Types[type]
    self.p.response.out.write(content)
  
  def redirect(self, url, status_code = 200):
    """Redirects to specific page with Status Code from argument, default is 200 as OK code"""
    self.p.set_status_code(status_code)
    self.p.redirect(url)
  
  def getParam(self, id):
    """Return parameter by specific identifier from self.p.params dictionary"""
    return self.p.params[id]
  
  def getParams(self):
    """Returns all params from current request as a dictionary"""
    return self.p.params
    
  def getRequest(self):
    """It's only a port from Google's Webapp framework request"""
    return self.p.request
  
  def getResponse(self):
    """It's only a port from Google's Webapp framework response"""
    return self.p.response
    
  def loginUser(self):
    """Makes a redirect to user login page and goes back"""
    self.redirect(users.create_login_url(self.p.request.uri))
    
  def logoutUser(self):
    """Makes a redirect to user logout page and goes back"""
    self.redirect(users.create_logout_url(self.p.request.uri))
  
  def set(self, varName, varValue):
    self.output_vars[varName] = varValue
  
  def get(self,varName):
    return self.output_vars[varName]
    
  def __show(self):
    """Shows selected view. If you want to disable view, please set 'view' to empty string"""
    code = ''
    if(self.view):
      self.viewObj = View(self.p.controller, self.view)
      code = self.viewObj.output(self.output_vars)
    
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
