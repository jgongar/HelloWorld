# Use a small official image that serves static files
FROM nginx:alpine

# Remove default nginx content and copy our app
RUN rm -rf /usr/share/nginx/html/*
COPY index.html style.css /usr/share/nginx/html/

# nginx listens on port 80 by default
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
