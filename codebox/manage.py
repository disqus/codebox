#!/usr/bin/env python
# -*- encoding:utf-8 -*-
"""
codebox.manage
~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from flaskext.actions import Manager

from codebox.app import create_app

app = create_app()
manager = Manager(app)

if __name__ == "__main__":
    manager.run()