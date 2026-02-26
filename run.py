"""
Copyright (c) 2025 Afedia Glory & Awani Caleb
All Rights Reserved.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
