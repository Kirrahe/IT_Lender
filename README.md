# IT_Lender

A small Flask application for tracking items in an IT lending library. It lets you list items, see reservations and request a checkout.

## Requirements

- Python 3.11+
- Flask
- pytest (for running the tests)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the application

```bash
python app.py
```

The application uses a local SQLite database file `library.db` in the project directory. It will be created automatically on first run.

## Running tests

```bash
pytest
```
