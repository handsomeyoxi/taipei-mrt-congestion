#!/bin/bash

# Install dependencies
npm ci

# Build the React app
npm run build

# Ensure build directory exists and has content
if [ ! -d "build" ] || [ -z "$(ls -A build)" ]; then
  echo "Error: Build directory is empty or missing"
  exit 1
fi

echo "Build completed successfully"
