import tornado.ioloop
import tornado.web
import tornado.websocket

the_bb = None

# Websocket server handler

class WebSocketServer(tornado.websocket.WebSocketHandler):

    def open(self):
        global web_main_test
        self.alive = True
        print 'New connection'
        self.send(".........")
        the_bb.the_handler = self   # tell the main thread we have a connection


    def send(self, string):
        print "Sending: " + string
        self.write_message(string)
       
    def on_message(self, message):
        # We only expect to tell the tablet the game state, not to receive anything.
        print "Got a message. Cool."
  
    def on_close(self):
        self.alive = False
        print 'Connection closed'
  
    def on_ping(self, data):
        print 'ping received:'
  
    def on_pong(self, data):
        print 'pong received:'
  
    def check_origin(self, origin):
        #print "-- Request from %s" %(origin)
        return True

class MainHandler(tornado.web.RequestHandler):
    def get(self, fname):
        self.render(fname)

def make_app():
    return tornado.web.Application([
        (r"/(.*\.html)", MainHandler),
        (r"/(.*\.js)", MainHandler),   # warning: MIME type is text/html (I assume shoudln't use self.render). Still effective.
        (r"/(.*\.css)", MainHandler),   # just for completeness. Also same warning.
        (r'/ws', WebSocketServer),
    ])

def go(bb):
    global the_bb
    the_bb = bb
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    print "Server Thread dead"

