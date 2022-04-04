#!/bin/env python3

from website import create_app

socketio, app = create_app()
socketio.run(app, debug=True, log_output=False)