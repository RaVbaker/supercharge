#!/usr/bin/env python
#
# AppEngine with SuperCharge - The MVC framework for Google AppEngine
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




# framework: Webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp
import re

# Google AppEngine APIs
from google.appengine.api import users

from sc_cfg import *

class Dispatcher(webapp.RequestHandler):
  
  def post(self, uri):
    self.__setRequestData(uri)
    self.__executeRequest()
  
  def get(self, uri):
    
    self.__setRequestData(uri)
    self.__executeRequest()
    self.__showDebugBar()
  
  def __showDebugBar(self):
    self.response.out.write("<div style='border: 3px solid #999;background-color: #f0f0f0;'><u><strong>DEBUG:</strong></u> URL: <strong>%s</strong> \t controller: <strong>%s</strong> \t action: <strong>%s</strong></div>\n"%(self.request.uri, self.controller, self.action))
  
  def __executeRequest(self):
    exec("from controllers.%s import %s" % (self.controller,self.className))
    exec("page = %s(self)" % (self.className))  
    
    #check thats this page has remaining method
    if 0 == dir(page).count(self.action):
      self.redirect("/%s" % self.controller)
      return
      
    exec("page.%s()" % self.action)
    page.after_execute()
    page.show()
  
  def __setRequestData(self, uri):
    
    path = self.__getRequestPath(uri)
    
    self.controller, self.action = path[0], path[1]
    self.className = self.controller.capitalize()
    self.params = path[2:]
  
  def __getRequestPath(self, uri):
    path = uri.split('/')
    
    if '' == uri:
      path = [Root_empty_controller]
    elif self.__matchInRoutes(uri):
      path = self.matched_path

    if 1 == len(path) or path[1] == '':
      path.insert(1,'index')
      
    return path
    
  def __matchInRoutes(self, uri):
    for route in Routes:
      rule, base_path = route
      matched = re.match(rule, uri)
      if matched:
        self.matched_path = base_path+list(matched.groups())
        return True


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
    self.before_execute()
  
  def renderHTML(self, html):
    self.p.response.headers['Content-Type'] = 'text/html'
    self.render(html)
  
  def renderText(self, text):
    self.p.response.headers['Content-Type'] = 'text/plain'
    self.render(text)
  
  def redirect(self, url):
    self.p.redirect(url)
  
  def render(self, content):
    self.p.response.out.write(content)
  
  def getParam(self, id):
    return self.p.params[id]
  
  def getParams(self):
    return self.p.params
    
  def getRequest(self):
    return self.p.request
  
  def getResponse(self):
    return self.p.response
    
  def login_user(self):
    self.redirect(users.create_login_url(self.p.request.uri))
    
  def logout_user(self):
    self.redirect(users.create_logout_url(self.p.request.uri))
    
  def show(self):
    """Shows selected view. If you want to disable view, please set 'view' to empty string"""
    code = ''
    if(self.view):
      self.viewObj = View(self.p.controller, self.view)
      code = self.viewObj.output()
    
    self.renderHTML(code)
  
  def before_execute(self):
    """It executed before whole request. Great for setting variables available in whole controller"""
    pass
  
  def after_execute(self):
    """It executed after whole request. Great for sending some data"""
    pass



def main():
  application = webapp.WSGIApplication([(r'/(.*)', Dispatcher)],debug=True)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
