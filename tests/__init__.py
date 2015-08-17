#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pyparsecom.core import Parse


def init_parse():
    Parse.initialize(os.environ.get('PARSE_APPLICATION_ID'), os.environ.get('PARSE_REST_KEY'))