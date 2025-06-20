# Build stage
FROM node:20-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps && \
    npm install -g react-scripts ajv@8.12.0 ajv-keywords@5.1.0 schema-utils@4.2.0

# Copy the rest of the application
COPY . .

# Build the application
RUN CI=false npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install serve
RUN npm install -g serve

# Copy build files from build stage
COPY --from=build /app/build ./build

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["serve", "-s", "build", "-l", "3000"] 