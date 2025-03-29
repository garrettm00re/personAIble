from personAIble import create_app
from personAIble.extensions import socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, port=5000) 