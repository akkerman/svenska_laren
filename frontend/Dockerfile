FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Update vite config to use internal Docker backend URL
RUN sed -i "s|'http://localhost:8003'|'http://backend:8000'|" vite.config.ts

# Run Vite dev server
CMD ["npm", "run", "dev", "--", "--host"]
