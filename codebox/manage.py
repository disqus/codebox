#!/usr/bin/env python
# manage.py
# -*- encoding:utf-8 -*-

from flaskext.actions import Manager

from codebox.app import create_app

app = create_app()
manager = Manager(app)

if __name__ == "__main__":
    manager.run()