FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY nginx.conf /etc/nginx/sites-available/sasha-artsoul
RUN ln -s /etc/nginx/sites-available/sasha-artsoul /etc/nginx/sites-enabled
