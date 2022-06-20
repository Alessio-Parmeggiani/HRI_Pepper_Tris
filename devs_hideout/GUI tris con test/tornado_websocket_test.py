import threading
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado_ws_game_faker import go

# Game handler. In the real project this will start the agent and all the stuff.
class GameFakerThread(threading.Thread):
    def __init__(self, ws_server):
        threading.Thread.__init__(self)
        self.ws_server = ws_server

    def run(self):
        go(self.ws_server)
        print "Thread dead"



# Websocket server handler

class WebSocketServer(tornado.websocket.WebSocketHandler):

    def open(self):
        self.alive = True
        print 'New connection'
        self.send("Hi planet")
        GameFakerThread(self).start()

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

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
