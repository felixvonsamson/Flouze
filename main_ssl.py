#!/bin/env python3

from website import create_app

socketio, app = create_app()
socketio.run(app, 
             debug=True, 
             log_output=False, 
             host="0.0.0.0", 
             keyfile="server_privatekey.pem", 
             certfile="server_cert.pem")
