import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    url = urlparse(DATABASE_URL)
    db_config = {
        "host": url.hostname,
        "user": url.username,
        "password": url.password,
        "database": url.path[1:],  # remove leading '/'
        "port": url.port or 3306
    }
else:
    # Local fallback for development
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "Riju",
        "database": "student_management_2",
        "port": 3306
    }
