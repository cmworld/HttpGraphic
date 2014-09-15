#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import web
#import Graphic
from setting import *
import Image

urls = (
    '/(.*)/', 'redirect /',
    '/image/resize', 'Graphic'
)

app = web.application(urls, globals())

def app_processor_start():
    pass

def app_processor_end():
    pass

def header_html():
    web.header('Content-Type', 'text/html; charset=UTF-8')

def notfound():
    web.ctx.status = '404 Not Found'
    return web.notfound('404 Not Found')

def internalerror():
    web.ctx.status = '500 Internal Server Error'
    return web.internalerror('500 Internal Server Error')

def handle_validate(func):
    def Function(*args):
        #todo 验证请求合法性

        return func(*args)
    return Function

app.add_processor(web.loadhook(app_processor_start))
app.add_processor(web.unloadhook(app_processor_end))

class Graphic:
    @handle_validate
    def GET(self):
        #web.header('Content-Type', 'text/html; charset=UTF-8')
        req = web.input(filename=None,w=0,h=0)
        
        size = int(req.w), int(req.h)

        dirname = os.path.dirname(req.filename)
        filename = os.path.basename(req.filename)

        original_file = "%s/%s" % (
            UPLOAD_PATH,
            req.filename
        )

        if not os.path.isfile(original_file):
            raise web.seeother('/')

        #thumbing start
        target_file = "%s/%s/%s_%s_%s%s" % (
            UPLOAD_PATH,
            dirname,
            os.path.splitext(filename)[0],
            size[0],
            size[1],
            os.path.splitext(filename)[1]
        )

        if not os.path.isfile(target_file):
            try:
                old_img = Image.open(original_file)
                old_w,old_h=old_img.size

                if old_img.mode !='RGBA':
                    img_format='JPEG'
                else:
                    img_format='PNG'        

                if size[1] is 0:
                    imgswap=old_img.resize((size[0],(old_h*size[0])/old_w),Image.ANTIALIAS)
                else:
                    imgswap=old_img.resize(size,Image.ANTIALIAS)

                imgswap.save(target_file,img_format,quality=60)


                stream = open(target_file)

            except IOError:
                print "cannot create thumbnail for", target_file
        else:
            stream = open(target_file)

        web.header('Content-Type', 'image/jpeg; charset=UTF-8')
        res = stream.read()
        stream.close()
        return res

if __name__ == "__main__":
    web.config.debug = True if DEBUG else False
    app.notfound = notfound
    app.internalerror = web.debugerror if DEBUG else internalerror

    app.run() 