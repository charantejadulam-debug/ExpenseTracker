# Expense Tracker

A Flask-based expense tracker with JSON storage, monthly budget tracking, expense categories, and dashboard charts.

## Run locally

1. Install Python 3.10 or newer.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   python app.py
   ```
4. Open http://127.0.0.1:5000

## Deploy on Render

1. Push this project to a GitHub repository.
2. In Render, create **New + → Web Service** and connect that repository.
3. Use these settings:
   - **Runtime:** Python
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
4. Add an environment variable named `SECRET_KEY` with a long random value.
5. Click **Create Web Service** and wait for the deploy to finish.

## Storage note

This demo stores expenses and the budget in `expenses.json` and `budget.json`. On typical free hosting, local files may be reset when the service restarts or redeploys. Do not use this version for important financial records without configuring persistent storage or a database.

## Features

- Add and delete expenses
- Categorize spending
- Set a monthly budget
- Filter by month
- View category and daily spending charts
