from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path
from datetime import date, datetime
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-dev-only-change-me")

BASE_DIR = Path(__file__).resolve().parent
EXPENSES_FILE = BASE_DIR / "expenses.json"
BUDGET_FILE = BASE_DIR / "budget.json"
CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Health", "Entertainment", "Education", "Other"]


def read_json(path, default):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def write_json(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_expenses():
    data = read_json(EXPENSES_FILE, [])
    return data if isinstance(data, list) else []


def load_budget():
    data = read_json(BUDGET_FILE, {"monthly_budget": 0})
    try:
        return max(0.0, float(data.get("monthly_budget", 0)))
    except (TypeError, ValueError, AttributeError):
        return 0.0


def parse_month(month_value):
    try:
        datetime.strptime(month_value, "%Y-%m")
        return month_value
    except (ValueError, TypeError):
        return date.today().strftime("%Y-%m")


@app.get("/")
def index():
    selected_month = parse_month(request.args.get("month", date.today().strftime("%Y-%m")))
    all_expenses = load_expenses()
    month_expenses = sorted(
        [e for e in all_expenses if str(e.get("date", "")).startswith(selected_month)],
        key=lambda e: (e.get("date", ""), int(e.get("id", 0))),
        reverse=True,
    )
    total = round(sum(float(e.get("amount", 0)) for e in month_expenses), 2)
    budget = load_budget()
    remaining = round(budget - total, 2)
    category_totals = {}
    for expense in month_expenses:
        category = expense.get("category", "Other")
        category_totals[category] = round(category_totals.get(category, 0) + float(expense.get("amount", 0)), 2)

    daily_totals = {}
    for expense in month_expenses:
        day = str(expense.get("date", ""))[-2:]
        daily_totals[day] = round(daily_totals.get(day, 0) + float(expense.get("amount", 0)), 2)

    return render_template(
        "index.html",
        expenses=month_expenses,
        selected_month=selected_month,
        today=date.today().isoformat(),
        total=total,
        budget=budget,
        remaining=remaining,
        category_labels=list(category_totals.keys()),
        category_values=list(category_totals.values()),
        daily_labels=sorted(daily_totals.keys(), key=lambda x: int(x)),
        daily_values=[daily_totals[k] for k in sorted(daily_totals.keys(), key=lambda x: int(x))],
        categories=CATEGORIES,
        budget_percent=min(100, round(total / budget * 100)) if budget > 0 else 0,
    )


@app.post("/add")
def add_expense():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "Other").strip()
    expense_date = request.form.get("date", date.today().isoformat())
    month = parse_month(request.form.get("return_month", expense_date[:7]))
    try:
        amount = round(float(request.form.get("amount", "")), 2)
        datetime.strptime(expense_date, "%Y-%m-%d")
        if not title or amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        flash("Enter a name, a valid date, and an amount greater than zero.", "error")
        return redirect(url_for("index", month=month))

    if category not in CATEGORIES:
        category = "Other"
    expenses = load_expenses()
    new_id = max((int(e.get("id", 0)) for e in expenses), default=0) + 1
    expenses.append({
        "id": new_id,
        "title": title,
        "amount": amount,
        "category": category,
        "date": expense_date,
    })
    write_json(EXPENSES_FILE, expenses)
    flash("Expense added successfully.", "success")
    return redirect(url_for("index", month=expense_date[:7]))


@app.post("/delete/<int:expense_id>")
def delete_expense(expense_id):
    month = parse_month(request.form.get("month", date.today().strftime("%Y-%m")))
    expenses = load_expenses()
    updated = [e for e in expenses if int(e.get("id", -1)) != expense_id]
    if len(updated) == len(expenses):
        flash("Expense not found.", "error")
    else:
        write_json(EXPENSES_FILE, updated)
        flash("Expense deleted.", "success")
    return redirect(url_for("index", month=month))


@app.post("/budget")
def update_budget():
    month = parse_month(request.form.get("month", date.today().strftime("%Y-%m")))
    try:
        budget = round(float(request.form.get("monthly_budget", "")), 2)
        if budget < 0:
            raise ValueError
    except (ValueError, TypeError):
        flash("Enter a valid budget amount (zero or more).", "error")
        return redirect(url_for("index", month=month))
    write_json(BUDGET_FILE, {"monthly_budget": budget})
    flash("Monthly budget updated.", "success")
    return redirect(url_for("index", month=month))


if __name__ == "__main__":
    app.run(debug=False)
