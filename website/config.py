import os

# Secret key (environment variable takes precedence)
SECRET_KEY = os.getenv("SECRET_KEY", "aabbccddeeffgghhiijjkkllmmnnoopp112233445566778899")

# Database URI
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://quizme-admin:password@192.168.2.160:5432/quizme-data")

# Disable SQLAlchemy event system to improve performance
SQLALCHEMY_TRACK_MODIFICATIONS = False