FROM node as builder
WORKDIR /app

COPY ui .
RUN yarn install
RUN yarn build

FROM nginx

COPY --from=builder /app/build /usr/share/nginx/html/ui
COPY nginx /etc/nginx
