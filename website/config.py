import os

# Secret key (environment variable takes precedence)
SECRET_KEY = os.getenv("SECRET_KEY", "aabbccddeeffgghhiijjkkllmmnnoopp112233445566778899")

# Database URI (environment variable takes precedence)
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://admin:changeme@192.168.1.10:5432/quizme")
