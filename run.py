from DublinBikes.FlaskApp import app
from DublinBikes.Utils.params import DISABLE_LOGGING
import argparse


if not DISABLE_LOGGING:
    from DublinBikes.Utils.logger_setup import setup_logging
    setup_logging()  # This initializes logging for the entire app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Flask application.")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host address to bind (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", default=5000, type=int, help="Port to bind (default: 5000)"
    )
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=True)
