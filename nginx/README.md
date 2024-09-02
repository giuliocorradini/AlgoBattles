# nginx

This directory contains nginx configuration files to expose the application, serve its static files (the frontend)
and proxy requests to the API and the admin interface.

The directory is copied by docker build in the nginx image, at `/etc/nginx` path.
