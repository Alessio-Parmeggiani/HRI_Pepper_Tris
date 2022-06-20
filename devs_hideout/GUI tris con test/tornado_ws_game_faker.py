def go(ws_server):
    while ws_server.alive:
        try:
            string = raw_input("What to send? ")
            if not ws_server.alive:
                return
            ws_server.send(string)
        except:
            print "Exception in GameFaker, maybe the connection is dead or something"
