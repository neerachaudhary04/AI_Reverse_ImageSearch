FROM node:18-alpine AS deps
WORKDIR /app

# Install dependencies exactly as locked
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:18-alpine
WORKDIR /app
ENV NODE_ENV=production

# Reuse node_modules from the deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy package manifest for npm scripts
COPY package*.json ./

# Copy static assets and server
COPY public ./public
COPY server.js .

EXPOSE 3000
CMD ["npm", "start"]
