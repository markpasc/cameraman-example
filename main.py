#!/usr/bin/env python

from os.path import join, dirname
from random import choice
import string
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


PATH_CHARS = string.letters + string.digits + string.digits


class Image(db.Model):

    path = db.StringProperty(required=True)
    owner = db.StringProperty(required=True)
    content = db.BlobProperty(required=True)
    content_type = db.BlobProperty(required=True)
    expire_at = db.DateTimeProperty(required=True)

    def put(self):
        if not self.path:
            self.path = ''.join(choice(PATH_CHARS) for x in xrange(1, 30))

        if not self.expire_at:
            self.expire_at = datetime.now() + timedelta(minutes=10)

        return super(db.Model, self).put()


class RequestHandler(webapp.RequestHandler):

    def respond(self, content, content_type="text/html; charset='utf-8'", status=200):
        self.response.set_status(status)
        self.response.headers['content-type'] = content_type
        self.response.out.write(content)


class IndexHandler(RequestHandler):

    def get(self):
        try:
            owner = self.request.cookies['owner']
        except KeyError:
            owner = ''.join(choice(PATH_CHARS) for x in xrange(1, 30))
            self.response.headers['Set-Cookie'] = 'owner=%s' % owner

        filename = join(dirname(__file__), 'index.html')
        html = template.render(filename, {})
        self.respond(html)


class UploadHandler(RequestHandler):

    def post(self):
        # get my owner string
        try:
            owner = self.request.cookies['owner']
        except KeyError:
            return self.respond('Cannot upload without an "owner" cookie',
                content_type='text/plain', status=403)

        # save a new image
        im = Image()
        im.owner = owner
        im.content = self.request.body
        im.content_type = self.request.headers['content-type']
        im.put()

        # "redirect" me to it
        image_url = self.request.relative_url('/image/%s' % im.path)
        self.response(image_url, content_type='text/plain')


class ImageHandler(RequestHandler):

    def get(self, path):
        not_found = lambda: self.respond('No such image %r' % path,
            content_type='text/plain', status=404)

        try:
            owner = self.request.cookies['owner']
        except KeyError:
            return not_found()

        try:
            (im,) = Image.all().filter('path =', path).filter('owner =', owner).fetch(1)
        except ValueError:
            return not_found()

        if im.expire_at <= datetime.now():
            return not_found()

        self.respond(im.content, content_type=im.content_type)


urls = (
    (r'/', IndexHandler),
    (r'/upload', UploadHandler),
    (r'/image/(?P<path>.*)', ImageHandler),
)


def main():
    application = webapp.WSGIApplication(urls, debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
