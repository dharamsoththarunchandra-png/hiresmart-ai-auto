# HireSmart Backend

This backend provides a Flask-based REST API for the HireSmart recruitment platform.

Structure:
- `app.py`: application factory and entrypoint
- `config.py`: environment-based configuration
- `database/`: SQLAlchemy initialization
- `models/`: database models
- `routes/`: API route blueprints
- `services/`: resume parsing and AI matching logic
- `utils/`: helper utilities
- `ml/`: optional scoring modules

Use `python -m pip install -r requirements.txt` and run with `python app.py`.
