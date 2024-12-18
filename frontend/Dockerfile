FROM node:16-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy project files
COPY . .

# Build the app
RUN npm run build --legacy-peer-deps

# Install serve to run the application
RUN npm install -g serve

EXPOSE 3000

# Serve the app
CMD ["serve", "-s", "build", "-l", "3000"]
