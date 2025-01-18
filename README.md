# quizme
 
## Docker Compose file
```
version: '3.8'

services:
  quizme:
    image: ghcr.io/ewsmyth/quizme:latest
    ports:
      - "6678:6678"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```