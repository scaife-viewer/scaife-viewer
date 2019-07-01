FROM node:11.7-alpine AS static
WORKDIR /opt/scaife-viewer/src/
COPY package.json package-lock.json ./
RUN npm ci
COPY webpack.config.js .babelrc ./
CMD npm run start
