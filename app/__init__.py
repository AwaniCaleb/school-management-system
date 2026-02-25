"""
Copyright (c) 2025 Afedia Glory & Awani Caleb
All Rights Reserved.
"""
import os
from flask import Flask
from app.extensions import db, migrate

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.root_path, '../school_new.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.routes import auth, main, classes, students, exams, fees, attendance, api, settings, student_portal
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(classes.bp)
    app.register_blueprint(students.bp)
    app.register_blueprint(exams.bp)
    app.register_blueprint(fees.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(student_portal.bp)

    return app
