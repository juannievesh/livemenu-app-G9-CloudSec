FROM node:20-alpine AS build-stage

WORKDIR /app

# Copiar configuración de dependencias
COPY package*.json ./

RUN npm ci

# Copiar el código fuente y compilar
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS production-stage

RUN apk update && apk upgrade --no-cache

# Eliminar la configuración por defecto de Nginx para evitar brechas
RUN rm /etc/nginx/conf.d/default.conf

# Copiar la configuración segura
COPY nginx.conf /etc/nginx/conf.d/

# Copiar los assets estáticos compilados desde la fase de Build
COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]