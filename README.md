# Wholesale data analytics

## Installation
1. Install Docker on your local environment (https://docs.docker.com/docker-for-windows/install/)
2. Install Docker compose (No need for Windows users)
3. Copy the following content to `docker-compose.yml` file anywhere (pre: `c:\`)

```
---
version: '3.1'
services:
  saitech_p1:
    image: belazy/saitech_p1:main
    container_name: saitech_p1
    restart: unless-stopped
    ports:
    - 8000:8000
```

4. Goto terminal and

```
cd c:\
docker-compose up -d
```

5. Thats it.... Goto http://localhost:8000

