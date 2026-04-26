# Use an official Node.js image as the base
FROM node:16

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 3000 to the host
EXPOSE 3000

# Start the React app in development mode
CMD ["npm", "start"]
