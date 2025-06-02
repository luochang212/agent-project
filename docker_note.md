# Docker 服务

使用 Docker 提供以下服务：

1. [PostgreSQL](https://www.postgresql.org/)
2. [Ollama](https://ollama.com/)
  - [bge-m3](https://huggingface.co/BAAI/bge-m3)

<!-- - [LangChain](https://github.com/langchain-ai/langchain)
- [Chroma](https://github.com/chroma-core/chroma)
- [Redis](https://github.com/redis/redis) -->

## 一、PostgreSQL

```bash
# 下载镜像
docker pull postgres:17

# 启动容器
docker run \
  --name postgres-container \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  -d postgres:17

# 启动容器（自定义数据库和用户）
docker run --name postgres-container \
  -e POSTGRES_DB=mydatabase \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  -d postgres:17

# 进入容器
docker exec -it postgres-container psql -U postgres
```

## 二、Ollama

```bash
# 下载镜像
docker pull ollama/ollama:latest

# 启动容器
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# 进入容器
docker exec -it ollama /bin/bash

# 进入容器后运行以下命令下载 bge-m3
# ollama pull bge-m3
```
