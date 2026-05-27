#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
