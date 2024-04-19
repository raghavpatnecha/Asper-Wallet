import os

class Config:
    """Base configuration class with default settings."""
    #SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///wallet.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

class DevelopmentConfig(Config):
    """Development configuration class with specific settings."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration class with specific settings."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite database for tests

class ProductionConfig(Config):
    """Production configuration class with specific settings."""
    DEBUG = False
    #SECRET_KEY = os.environ.get('SECRET_KEY')  # Ensure this is set in the production environment

def get_config(env):
    """Factory method to retrieve the appropriate configuration based on environment."""
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
