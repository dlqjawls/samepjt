FROM node:22

WORKDIR /code

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build

CMD ["npx", "serve", "-s", "build", "-l", "3000"]

#Nginx 통해 배포할 때
# React 빌드
#FROM node:18 AS build
#WORKDIR /app
#COPY package.json package-lock.json ./
#RUN npm install
#COPY . .
#RUN npm run build

# Nginx 설정
#FROM nginx:latest
#COPY --from=build /app/build /usr/share/nginx/html
#EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]


