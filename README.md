# quizme

## Installing Docker
```
sudo apt update
```
```
sudo apt upgrade
```
```
apt list --upgradable
```
```
sudo apt install <name of apt>
```
```
sudo apt update
```
```
sudo apt install -y ca-certificates curl gnupg lsb-release
```
```
sudo mkdir -p /etc/apt/keyrings
```
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
```
sudo apt update
```
```
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
```
sudo systemctl status docker
```

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
      test: ["CMD-SHELL", "pg_isready -U quizme-admin -d quizme-data"]
      interval: 10s
      timeout: 5s
      retries: 5

  web-app:
    image: ghcr.io/ewsmyth/quizme:latest
    ports:
      - "6678:6678"
    environment:
      - SECRET_KEY=aabbccddeeffgghhiijjkkllmmnnoopp00112233445566778899
      - DATABASE_URL=postgresql://quizme-admin:password@db:5432/quizme-data
    depends_on:
      - db

volumes:
  postgres-data:
```