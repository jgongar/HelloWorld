# =============================================================================
# DOCKERFILE - Instructions to build a "Docker image" of your app
# =============================================================================
# Docker runs your app in a small, isolated environment (a "container").
# This file tells Docker: start from a base image, add our files, run a server.
# Each line is a step. When you run "docker build", Docker runs these steps.
# =============================================================================

# FROM = which base image to start from (we use nginx, a popular web server)
# nginx:alpine = small, secure version of nginx (alpine = minimal Linux)
FROM nginx:alpine

# RUN = run a command inside the image (we delete nginx's default demo page)
RUN rm -rf /usr/share/nginx/html/*

# COPY = copy files from your computer INTO the image
# We put index.html and style.css where nginx looks for web files
COPY index.html style.css /usr/share/nginx/html/

# EXPOSE = document that this container listens on port 80 (HTTP)
# (Doesn't open the port by itself; "docker run -p 8080:80" maps it.)
EXPOSE 80

# CMD = command to run when the container starts
# "nginx -g daemon off;" = start nginx in the foreground (so the container stays running)
CMD ["nginx", "-g", "daemon off;"]
