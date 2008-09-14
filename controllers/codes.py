#!/usr/bin/env python
# encoding: utf-8
"""
codes.py

Created by Rafał Piekarski on 2008-09-12.
Copyright (c) 2008 . All rights reserved.
"""
from supercharge import Controller


class Codes(Controller):

  def index(self):
    self.render("Code list")
    
  def single_file(self):
    self.set('text', "jeden plik")
