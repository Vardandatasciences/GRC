INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this near the top
    # ...other middleware
]

# Allow requests from your frontend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # Or whatever port your frontend is running on
]

# Or allow all origins (not recommended for production)
# CORS_ALLOW_ALL_ORIGINS = True 