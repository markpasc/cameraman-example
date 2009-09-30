#!/usr/bin/env python

import wsgiref.handlers

from google.appengine.ext import webapp


class MainHandler(webapp.RequestHandler):

    def get(self):
        self.response.out.write('Hello world!')


urls = {
    '/': MainHandler,
}


def main():
    application = webapp.WSGIApplication(urls.items(), debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
