from personAIble import create_app
# from personAIble.extensions import socketio
import os 

app = create_app()

env = os.getenv("ENV")
if env != "PRODUCTION":
    if __name__ == '__main__':
        app.run(port=5000, debug=True)