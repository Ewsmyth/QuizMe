# quizme
 
## Docker Compose file
```
version: '3.8'

services:
  db:
    image: postgres:latest
    environment:
      - POSTGRES_DB=quizme-data
      - POSTGRES_USER=quizme-admin
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U quizme-admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  quizme:
    image: ghcr.io/ewsmyth/quizme:latest
    ports:
      - "6678:6678"
    environment:
      - DATABASE_URI=postgresql://quizme-admin:password@db:5432/quizme-data
      - SECRET_KEY=aabbccddeeffgghhiijjkkllmmnnoopp00112233445566778899
    depends_on:
      - db

volumes:
  postgres-data:

```