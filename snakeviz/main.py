#!/usr/bin/env python

import os.path
from pstats import Stats

import tornado.ioloop
import tornado.web

from stats import table_rows, json_stats

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    'debug': True,
    'gzip': True
}

PROFILE_PATH = 'profiles'


class VizHandler(tornado.web.RequestHandler):
    def get(self, profile_name):
        profile_name = os.path.join(PROFILE_PATH, profile_name)
        if os.path.isdir(profile_name):
            self._list_dir(profile_name)
        else:
            try:
                s = Stats(profile_name)
            except:
                raise RuntimeError('Could not read %s.' % profile_name)
            self.render(
                'viz.html', profile_name=profile_name,
                table_rows=table_rows(s), callees=json_stats(s)
            )

    def _list_dir(self, path):
        """
        Show a directory listing.

        """
        entries = os.listdir(path)
        parentpath = os.path.normpath(os.path.join(path, '..'))
        parentlink = os.path.relpath(parentpath, PROFILE_PATH)
        dir_entries = [[['..', str(parentlink)]]]
        for name in entries:
            if name.startswith('.'):
                # skip invisible files/directories
                continue
            fullpath = str(os.path.join(path, name))
            linkpath = os.path.relpath(fullpath, PROFILE_PATH)
            displayname = str(name)
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullpath):
                displayname += '/'
            if os.path.islink(fullpath):
                displayname += '@'
            dir_entries.append([[displayname, linkpath]])
        self.render(
            'dir.html', dir_name=path, dir_entries=dir_entries)

handlers = [(r'/(.*)', VizHandler)]

app = tornado.web.Application(handlers, **settings)

if __name__ == '__main__':
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
