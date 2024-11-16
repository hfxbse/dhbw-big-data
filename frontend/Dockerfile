FROM node:20-alpine

RUN mkdir /app
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

ENTRYPOINT ["npm", "run", "start"]
