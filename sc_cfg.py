#!/usr/bin/env python
# encoding: utf-8
#
# AppEngine with SuperCharge - The light MVC framework for Google AppEngine
#
# Copyright 2008 Rafal "RaVbaker" Piekarski
#
"""
sc_cfg.py

Configuration file

Created by Rafał Piekarski on 2008-09-13.
Copyright (c) 2008 . All rights reserved.
"""

# name of controller which is execute for uri path: `/`
Root_empty_controller = 'index'

# set optional routes for page
Routes = [

  ('s/ciezka', ['test', 'testParams']),
  ('sc\d', ['test', 'index']),
  ('e(.{3})(\d*)', ['test', 'testParams']),

]

