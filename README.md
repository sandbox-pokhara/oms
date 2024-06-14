# Order Management System

### 👋 Introduction
The minimal open-source selfhosted order management system. It takes about 2 minutes to deploy. For most people this ends up being the best value option because of how much time it saves.

### Prerequisites
- Docker 

### 🚀 Deployment

```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/sandbox-pokhara/oms/main/docker-compose.yml
curl -o .env https://raw.githubusercontent.com/sandbox-pokhara/oms/main/.env.sample # update the env file
docker compose up

# or 

git clone https://github.com/sandbox-pokhara/oms.git
cd oms
cat .env.sample > .env # update the env file
docker compose up
```

### 🛠 Tech Stack
- Django 
- Postgres


### 🙌 Contributing
Contributions are what makes the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
