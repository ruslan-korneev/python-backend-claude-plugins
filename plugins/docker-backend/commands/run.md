---
name: docker:run
description: Generate docker run command for a service
allowed_tools:
  - Bash
  - Read
  - AskUserQuestion
arguments:
  - name: service
    description: "Service: postgres, redis, mongodb, rabbitmq, kafka, elasticsearch"
    required: true
  - name: name
    description: Container name (default {service}-dev)
    required: false
---

# Command /docker:run

Generate a `docker run` command for a service.

## Principle

**docker run by default.** Always ask the user:
1. Existing service? (connect)
2. docker run? (recommended)
3. docker-compose? (only if explicitly requested)

## Instructions

### Step 1: Ask the user

Use AskUserQuestion:
- "Connect to an existing service?"
- "Start via docker run?" (recommended)
- "Create docker-compose.yml?"

### Step 2: Generate the command

## docker run Templates

### PostgreSQL

```bash
docker run -d \
  --name postgres-dev \
  -e POSTGRES_USER=app \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=app_db \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  --health-cmd="pg_isready -U app" \
  --health-interval=10s \
  --health-timeout=5s \
  --health-retries=5 \
  postgres:16-alpine
```

**Connection string:**
```
postgresql+asyncpg://app:secret@localhost:5432/app_db
```

### Redis

```bash
docker run -d \
  --name redis-dev \
  -p 6379:6379 \
  -v redis-data:/data \
  --health-cmd="redis-cli ping" \
  --health-interval=10s \
  redis:7-alpine \
  redis-server --appendonly yes
```

**Connection:**
```
redis://localhost:6379/0
```

### MongoDB

```bash
docker run -d \
  --name mongo-dev \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -p 27017:27017 \
  -v mongo-data:/data/db \
  --health-cmd="mongosh --eval 'db.adminCommand(\"ping\")'" \
  --health-interval=10s \
  mongo:7
```

**Connection:**
```
mongodb://admin:secret@localhost:27017
```

### RabbitMQ

```bash
docker run -d \
  --name rabbitmq-dev \
  -e RABBITMQ_DEFAULT_USER=app \
  -e RABBITMQ_DEFAULT_PASS=secret \
  -p 5672:5672 \
  -p 15672:15672 \
  -v rabbitmq-data:/var/lib/rabbitmq \
  --health-cmd="rabbitmq-diagnostics -q ping" \
  --health-interval=10s \
  rabbitmq:3-management-alpine
```

**Management UI:** http://localhost:15672
**Connection:**
```
amqp://app:secret@localhost:5672/
```

### Kafka (with KRaft, without Zookeeper)

```bash
docker run -d \
  --name kafka-dev \
  -e KAFKA_CFG_NODE_ID=1 \
  -e KAFKA_CFG_PROCESS_ROLES=broker,controller \
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -p 9092:9092 \
  -v kafka-data:/bitnami/kafka \
  bitnami/kafka:latest
```

**Bootstrap servers:**
```
localhost:9092
```

### Elasticsearch

```bash
docker run -d \
  --name elasticsearch-dev \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -p 9200:9200 \
  -p 9300:9300 \
  -v elasticsearch-data:/usr/share/elasticsearch/data \
  --health-cmd="curl -f http://localhost:9200/_cluster/health || exit 1" \
  --health-interval=10s \
  elasticsearch:8.11.0
```

**URL:**
```
http://localhost:9200
```

### MinIO (S3-compatible)

```bash
docker run -d \
  --name minio-dev \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -p 9000:9000 \
  -p 9001:9001 \
  -v minio-data:/data \
  --health-cmd="curl -f http://localhost:9000/minio/health/live || exit 1" \
  --health-interval=10s \
  minio/minio:latest \
  server /data --console-address ":9001"
```

**Console:** http://localhost:9001
**Endpoint:**
```
http://localhost:9000
```

## Useful flags

```bash
# Auto-restart
--restart=unless-stopped

# Resource limits
--memory=512m
--cpus=1

# Network
--network=my-network

# Logging
--log-driver=json-file
--log-opt max-size=10m
--log-opt max-file=3
```

## Management

```bash
# Stop
docker stop {{ name }}

# Start
docker start {{ name }}

# Logs
docker logs -f {{ name }}

# Remove (with data)
docker rm -f {{ name }}
docker volume rm {{ name }}-data
```

## Response format

```
## Docker run: {{ service }}

### Command
```bash
docker run -d \
  --name {{ name }} \
  ...
```

### Connection
- **URL:** `...`
- **User:** `...`
- **Password:** `...`

### Management
- Logs: `docker logs -f {{ name }}`
- Stop: `docker stop {{ name }}`
- Remove: `docker rm -f {{ name }}`
```
