#!/bin/env python3

from website import create_app
import argparse

parser = argparse.ArgumentParser(
                    prog = "Flouze", 
                    description = "The best game ever")

parser.add_argument("--lang_id", dest="lang_id", action="store", 
                    choices=[0,1,2], default=0, type=int, nargs="?", 
                    help="Chooses the language of the game.")

args = parser.parse_args()

socketio, app = create_app(lang_id=args.lang_id)

if __name__ == "__main__":
  socketio.run(app, debug=True, log_output=False, host="0.0.0.0")
