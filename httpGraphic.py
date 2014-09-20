#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import web
import Image,ImageDraw
from cStringIO import StringIO
from setting import *

urls = (
    '/(.*)/', 'redirect /$1',
    '/notfound','notfoundCrl',
    '/graphic/(\w+)', 'serverCrl'
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
        #todo 验证请求

        return func(*args)
    return Function

app.add_processor(web.loadhook(app_processor_start))
app.add_processor(web.unloadhook(app_processor_end))


class Graphic:

    _stream = None
    _org = None
    _format = None
    _org_w = 0
    _org_h = 0
    _quality = 60


    def __init__(self,original_file):
        if not os.path.isfile(original_file):
            raise "no original_file found"
        
        self._org = Image.open(original_file)
        self._org_w,self._org_h = self._org.size

        if self._org.mode !='RGBA':
            self._format='JPEG'
        else:
            self._format='PNG'

        self._stream = StringIO()

    def resize(self,size):
        if size[1] is 0:
            tmp=self._org.resize((size[0],(self._org_h*size[0])/self._org_w),Image.ANTIALIAS)
        elif size[0] is 0:
            tmp=self._org.resize(((self._org_w * size[1])/self._org_h,size[1]),Image.ANTIALIAS)     
        else:
            tmp=self._org.resize(size,Image.ANTIALIAS)
        
        tmp.save(self._stream,self._format,quality=self._quality)

    def cut(self):
        pass


    def mark(self):
        pass

    def getDate(self):
        return self._stream.getvalue()

#造一张默认图片
def notfoundImage(w,h):
    if w is 0 or h is 0:
        w = h = 200
    elif w is 0:
        w = h
    elif h is 0:
        h = w

    output = StringIO()

    img = Image.new('RGBA', (w,h), (240,240,240,0))
    img.save(output,'JPEG')
    return output.getvalue()

def mkTargetFile(action,filename,size):
    global filename_template
    dirname = os.path.dirname(filename)
    filename = os.path.basename(filename)

    name,ext = os.path.splitext(filename)

    if size[0] is 0:
        tpl = filename_template.get(action+"_h")
    elif size[1] is 0:
        tpl = filename_template.get(action+"_w")
    else:
        tpl = filename_template.get(action+"_wh")

    return ''.join([UPLOAD_PATH,dirname,'/',tpl.format(name=name, width=size[0],height=size[1],ext=ext)])

class notfoundCrl:
    def GET(self):
        req = web.input(w=0,h=0)

        output = notfoundImage(int(req.w), int(req.h))

        web.header('Content-Type', 'image/jpeg; charset=UTF-8')
        return output

class serverCrl:
    @handle_validate
    def GET(self,action):

        #web.header('Content-Type', 'text/html; charset=UTF-8')
        req = web.input(filename=None,w=0,h=0)

        size = int(req.w), int(req.h)

        target_file = mkTargetFile(action,req.filename,size)

        if os.path.isfile(target_file):
            fs = open(target_file)
            stream = fs.read()
        else:

            original_file = "%s/%s" % (
                UPLOAD_PATH,
                req.filename
            )

            stream = None
            try:
                gc = Graphic(original_file)
                
                if action == "resize":
                    gc.resize(size)
                elif action is "cut":
                    gc.cut()

                stream = gc.getDate()

                if LOCALSTORAGE:
                    fs = open(target_file, 'wb')
                    fs.write(stream)
                    fs.close()

            except IOError:
                #todo logger
                #request_uri = web.ctx.env.get('REQUEST_URI', '/')
                stream = notfoundImage(size[0],size[1])

        web.header('Content-Type', 'image/jpeg; charset=UTF-8')
        return stream


if __name__ == "__main__":
    web.config.debug = True if DEBUG else False
    app.notfound = notfound
    app.internalerror = web.debugerror if DEBUG else internalerror

    app.run() 