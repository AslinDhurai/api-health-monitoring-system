API Health Monitoring System
===========================

DevOps Internship Assignment – 2026

📌 Overview
-----------

This project is a self-hosted, cloud-native API Health Monitoring System designed to periodically monitor the health of user-defined API endpoints and notify when their health status changes.

The system is built with a strong focus on:

- Scalability
- Reliability
- Operational simplicity
- Infrastructure as Code (IaC)

No third-party or managed monitoring services are used.

🎯 Problem Statement
--------------------

Design and build a system that:

- Monitors the health of user-defined APIs
- Evaluates health using configurable rules
- Detects meaningful health state changes
- Notifies users when changes occur
- Scales reliably for large numbers of endpoints

🏗️ High-Level Architecture
--------------------------

The system follows a decoupled, event-driven architecture.

**Core Components**

- API Service (FastAPI) – Endpoint management
- Scheduler (Local Python App) – Periodic job producer
- Worker Service (ECS Fargate) – Health check executor
- Amazon SQS – Job queue
- Amazon DynamoDB – Configuration & state storage
- Application Load Balancer – API exposure
- Amazon ECR – Container registry
- Terraform – Infrastructure as Code

📂 Project Structure
--------------------

```
api-health-monitor/
├── api/          # FastAPI application
├── scheduler/    # Local scheduler job producer
├── worker/       # Health check worker service
├── notifier/     # Alerting / notification logic (extensible)
├── shared/       # Shared utilities and models
├── docker/       # Dockerfiles for API and worker
├── terraform/    # Terraform IaC for AWS resources
├── docs/         # Architecture diagrams & documentation
├── docker-compose.yml
├── README.md
├── .gitignore
├── .dockerignore
```

⚙️ System Workflow
------------------

1. User registers an API endpoint via the API Service  
2. Scheduler fetches endpoints periodically  
3. Scheduler pushes health check jobs to Amazon SQS  
4. Worker services consume jobs from SQS  
5. Workers perform HTTP health checks  
6. Health state is stored in DynamoDB  
7. Alerts are triggered on meaningful state transitions  

🩺 Health Check Logic
---------------------

**Supported States**

- UNKNOWN
- HEALTHY
- UNHEALTHY
- RECOVERED

**State Transitions**

- UNKNOWN → HEALTHY (first success)
- HEALTHY → UNHEALTHY (after failure threshold)
- UNHEALTHY → RECOVERED (on recovery)

Alerts are generated only on state changes, avoiding alert fatigue.

🧱 Infrastructure (Terraform)
-----------------------------

All AWS resources are provisioned using Terraform.

**Provisioned Resources**

- VPC & networking
- ECS Cluster (Fargate)
- API & Worker services
- Application Load Balancer
- Amazon SQS + DLQ
- DynamoDB tables
- IAM roles (least privilege)
- Amazon ECR repositories
- CloudWatch Logs

🔐 Security Considerations
-------------------------

- No AWS credentials are stored in the repository
- Local execution uses AWS CLI credential chain
- ECS services use IAM task roles
- Secrets are excluded via `.gitignore` and `.dockerignore`

📋 Requirements
---------------

**Local Machine**

- Python 3.9+
- Docker
- AWS CLI
- Terraform
- Git

**AWS Account**

- Permissions to create ECS, SQS, DynamoDB, ALB, IAM, ECR

▶️ How to Run the Project
-------------------------

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/AslinDhurai/api-health-monitoring-system
cd api-health-monitor
```

### 2️⃣ Configure AWS Credentials (Local Only)
```bash
aws configure
```
⚠️ Credentials are never committed to GitHub.

### 3️⃣ Deploy Infrastructure Using Terraform
```bash
cd terraform
terraform init
terraform plan
terraform apply
```
This will provision all AWS resources.

### 4️⃣ Build & Push Docker Images

Authenticate Docker with **Amazon ECR** before pushing images.

#### Authenticate Docker to Amazon ECR

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
```

#### Build and Push API Service

```bash
docker build -t api-health-api -f docker/api.Dockerfile .
docker tag api-health-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/api-health-api:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/api-health-api:latest
```

#### Build and Push Worker Service

```bash
docker build -t api-health-worker -f docker/worker.Dockerfile .
docker tag api-health-worker:latest <account-id>.dkr.ecr.<region>.amazonaws.com/api-health-worker:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/api-health-worker:latest
```

### 5️⃣ Access the API
Open in browser:

```
http://<ALB_DNS>/docs
```

Use Swagger UI to:
- Create endpoints
- List endpoints

### 6️⃣ Run the Scheduler (Local)
```bash
python scheduler/scheduler.py
```
The scheduler will enqueue health check jobs into SQS.

### 7️⃣ Monitor Worker Logs
Check CloudWatch logs for:
- Health check execution
- State transitions
- Alert logs

Example:
```
[ALERT] Endpoint abc changed from HEALTHY → UNHEALTHY
```

🧪 Testing Scenarios
--------------------

- Healthy API → UNKNOWN → HEALTHY
- Failing API → HEALTHY → UNHEALTHY
- Recovered API → UNHEALTHY → RECOVERED

🧹 Cleanup (Important)
----------------------

To avoid AWS charges:
```bash
cd terraform
terraform destroy
```
ECR repositories are deleted using `force_delete = true`.

📈 Scalability & Reliability
---------------------------

- Stateless workers enable horizontal scaling
- SQS decouples scheduling from execution
- DynamoDB provides scalable state storage
- ECS auto-restarts failed tasks
- DLQ captures failed jobs

🧠 Design Decisions & Trade-offs
--------------------------------

- ECS chosen over Kubernetes for lower operational overhead
- Scheduler run locally for simplicity and faster iteration
- Alerts implemented via logs to avoid managed monitoring tools
- DynamoDB chosen over RDS for scalability and simplicity

🏁 Conclusion
-------------

This project demonstrates:

- Real-world DevOps system design
- Event-driven architecture
- Scalable and reliable monitoring
- Infrastructure as Code best practices
- End-to-end ownership (build → deploy → destroy)

The focus is on design thinking and operational correctness, not just feature completeness.

👤 Author
---------

Aslin Dhurai  
DevOps Internship Candidate – 2026

