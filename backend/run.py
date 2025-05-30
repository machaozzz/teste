from app import create_app, get_socketio

app = create_app()
socketio = get_socketio()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)