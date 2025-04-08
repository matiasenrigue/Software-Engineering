# Dublin Bikes – Flask Application

## Overview

The **FlaskApp** folder contains the web application for the Dublin Bikes project. This application provides an interactive
interface for users to view bike station data, real-time weather updates, and make ride predictions. It also supports user
registration, login, and profile management.

## Folder Structure

```
FlaskApp/
├── __init__.py         # Initializes the Flask application and sets up configuration.
├── routes.py           # Defines the route handlers for web pages and API endpoints.
├── static/
│   ├── js/             # JavaScript modules for maps, bikes, weather, and ride prediction functionalities.
│   ├── pics/           # Image assets (logos, icons, etc.) used in the web interface.
│   └── styles.css      # Custom CSS styles for the application.
└── templates/
    ├── base.html       # Base HTML template with common layout (header, footer, etc.).
    ├── home.html       # Home page template displaying the map and bike station information.
    ├── about.html      # About page template.
    ├── login.html       # User login page template.
    ├── register.html    # User registration page template.
    ├── edit_profile.html # User profile editing page template.
    └── station.html    # Detailed station view template with availability trends.
```

## Key Components

- **`__init__.py`**  
  Initializes the Flask app, sets up configurations, and ensures the application is ready to handle requests.

- **`routes.py`**  
  Contains all the URL route handlers for:
  - Rendering the home, about, and station details pages.
  - Serving API endpoints for current weather, forecast weather, bike availability, and ride prediction.
  - Managing user registration, login, logout, and profile editing.
  
- **Static Files (JS, CSS, Images)**  
  - **JavaScript (in `static/js/`):** Modules to handle map interactions, data fetching from API endpoints, and dynamic UI updates.
  - **CSS (in `static/styles.css`):** Styles the application’s HTML elements.
  - **Images (in `static/pics/`):** Provides visual assets such as logos and icons used across the application.

- **Templates**  
  HTML templates used to render pages dynamically based on data passed from Flask route handlers.

## Getting Started

1. **Installation:**  
   Ensure that all required packages (e.g., Flask) are installed. Maintain the provided directory structure.

2. **Running the Application:**  
   Set the `FLASK_APP` environment variable and start the server:
   ```bash
   export FLASK_APP=FlaskApp
   flask run
   ```
   Alternatively, use a WSGI server to deploy the application.

3. **Configuration:**  
   Verify that API keys and other settings in the `DublinBikes/Utils/params.py` file are correctly configured.

## Notes

- The application integrates with external APIs to fetch real-time bike and weather data.
- User session management is used to allow personalization (e.g., setting a default bike station).
- API endpoints provide JSON responses to support AJAX calls and dynamic front-end updates.
