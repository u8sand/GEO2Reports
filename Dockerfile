FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
ADD node_modules/kysely-codegen/dist/db.d.ts ./node_modules/kysely-codegen/dist/db.d.ts 
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
