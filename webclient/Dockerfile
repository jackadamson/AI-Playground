# base image
FROM node:12.2.0-alpine as build

# set working directory
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
# install and cache app dependencies
COPY package.json /app/package.json
RUN yarn install --silent
COPY . /app
RUN npm run build

CMD ["npm", "start"]


# production environment
FROM nginx:1.16.0-alpine
COPY --from=build /app/build /usr/share/nginx/html
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
