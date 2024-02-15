FROM nginx:1.22.1
COPY nginx.conf /etc/nginx/templates/default.conf.template
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]