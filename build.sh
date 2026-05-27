#!/usr/bin/env bash
# exit on error
set -o errexit

# Change to the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate
