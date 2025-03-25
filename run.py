from DublinBikes.FlaskApp import app
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Flask application.')
    parser.add_argument('--host', default='127.0.0.1', help='Host address to bind (default: 127.0.0.1)')
    parser.add_argument('--port', default=5000, type=int, help='Port to bind (default: 5000)')
    args = parser.parse_args()
    
    app.run(host=args.host, port=args.port, debug=True)
