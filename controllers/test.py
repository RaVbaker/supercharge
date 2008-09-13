#!/usr/bin/env python
# encoding: utf-8
"""
test.py

Created by Rafał Piekarski on 2008-09-12.
Copyright (c) 2008 . All rights reserved.
"""
from supercharge import Controller

from google.appengine.api import users

class Test(Controller):

  def index(self):
    self.view = ""
    user = users.get_current_user()
    if user:
      self.render('Hello '+user.nickname())
    else:
      self.loginUser()
  
  def testParams(self):
    self.render(self.getParams())
  
  def logout(self):
      user = users.get_current_user()
      if user:
        self.logoutUser()
      else:
        self.redirect('/')
  
  def tested(self):
    pass
  

