from __future__ import annotations

from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from build_aws_services_book import AS_OF_DATE, CATEGORIES, SOURCES, ServiceEntry


ROOT = Path(r"D:\Notes")
MARKDOWN_PATH = ROOT / "AWS Services Master Architect Handbook.md"
PDF_PATH = ROOT / "AWS Services Master Architect Handbook.pdf"


def all_services() -> list[tuple[str, ServiceEntry]]:
    items: list[tuple[str, ServiceEntry]] = []
    for category in CATEGORIES:
        for service in category.services:
            items.append((category.name, service))
    return items


def analogy_for(name: str, category: str) -> str:
    specific = {
        "Amazon EC2": "EC2 is like renting an empty apartment. AWS gives you the building, electricity, and security gate, but you still choose the furniture, kitchen setup, cleaning schedule, and how the rooms are used.",
        "AWS Lambda": "Lambda is like hiring a skilled technician only when a button is pressed. Nobody sits idle waiting all day. The work starts when an event happens and stops when the task is done.",
        "Amazon ECS": "ECS is like a warehouse floor manager for containers. You decide what each container should do, and ECS decides where to place it, how many should be running, and which unhealthy ones should be replaced.",
        "Amazon EKS": "EKS is like running a large industrial kitchen where Kubernetes is the standard operating model. AWS keeps the control room healthy, while your platform team still decides how the kitchen stations and chefs are organized.",
        "AWS Elastic Beanstalk": "Elastic Beanstalk is like moving into a furnished apartment. You do not control every screw in the wall, but you can start living comfortably much faster.",
        "AWS Batch": "AWS Batch is like a factory shift scheduler. Jobs wait in line, compute workers arrive when needed, work gets processed in order of priority, and the floor scales with demand.",
        "Amazon Lightsail": "Lightsail is like buying a starter home package instead of designing a custom house from raw land and blueprints.",
        "Amazon S3": "S3 is like an infinitely large, extremely durable digital warehouse with labeled boxes. You store objects, retrieve objects, copy objects, and archive objects, but you do not mount the warehouse like a local disk.",
        "Amazon EBS": "EBS is like attaching a private hard drive to a server. The server treats it like a disk, and you are responsible for filesystem choices and how the data on it is organized.",
        "Amazon EFS": "EFS is like a shared office filing room that many Linux machines can open at the same time.",
        "Amazon FSx": "FSx is like choosing a specialist warehouse instead of a general one. You pick the exact file system family that matches the protocol or performance shape your application expects.",
        "Amazon S3 Glacier": "S3 Glacier is like a secure deep archive in a storage bunker. Access is possible, but you do not go there every minute.",
        "AWS Storage Gateway": "Storage Gateway is like a translator standing between an old office and a new cloud warehouse. Old systems keep speaking the old language while the storage backend moves into AWS.",
        "Amazon RDS": "RDS is like hiring a professional building manager for your database apartment block. You still design the rooms and the traffic flow, but routine maintenance is no longer fully manual.",
        "Amazon Aurora": "Aurora is like a modern relational city built with better highways and shared utilities under the road. It still feels like a relational database to developers, but the hidden infrastructure is far more cloud-native.",
        "Amazon DynamoDB": "DynamoDB is like a hyper-efficient warehouse indexed exactly for the pickup patterns you planned in advance. If you know how customers will ask for items, service is incredibly fast.",
        "Amazon ElastiCache": "ElastiCache is like keeping the most frequently needed items on the front desk so the team does not have to walk to the main archive every time.",
        "Amazon Neptune": "Neptune is like a relationship map rather than a filing cabinet. The value is in knowing how one thing connects to another across many hops.",
        "Amazon DocumentDB": "DocumentDB is like storing richly structured folders instead of rigid spreadsheet rows.",
        "Amazon Redshift": "Redshift is like a giant analysis room where data is arranged so analysts can scan and summarize huge volumes quickly.",
        "Amazon VPC": "A VPC is like the fenced land plot on which your cloud buildings are placed. The roads, gates, internal streets, and visitor entry rules all begin there.",
        "Amazon Route 53": "Route 53 is like the internet's smart receptionist. It decides which building a visitor should be sent to based on health, geography, or policy.",
        "Amazon CloudFront": "CloudFront is like placing local mini-warehouses close to customers around the world so they do not always wait for goods from one distant central warehouse.",
        "Elastic Load Balancing": "A load balancer is like a traffic marshal at a busy entrance who decides which healthy counter each customer should visit.",
        "Amazon API Gateway": "API Gateway is like a managed reception desk for APIs. It checks identity, rate limits visitors, and routes valid requests to the right backend.",
        "AWS Direct Connect": "Direct Connect is like a private highway between your office campus and AWS instead of relying only on public roads.",
        "AWS IAM": "IAM is like the master key and permission system for the entire AWS building complex.",
        "Amazon Cognito": "Cognito is like the guest registration desk for your application's end users.",
        "AWS KMS": "KMS is like a high-security key room that controls who can use which cryptographic key and when.",
        "AWS Secrets Manager": "Secrets Manager is like a locked safe whose contents can be rotated without rewriting every employee's memory.",
        "AWS WAF": "WAF is like a web-aware security checkpoint at the front gate.",
        "AWS Shield": "Shield is like riot control protecting the outer perimeter from overwhelming attack traffic.",
        "Amazon GuardDuty": "GuardDuty is like a trained detective monitoring logs, patterns, and unusual activity for warning signs.",
        "Amazon CloudWatch": "CloudWatch is like the control room wall full of gauges, alarms, and logs for your cloud systems.",
        "AWS CloudTrail": "CloudTrail is like the official building visitor and action register that says who touched what and when.",
        "AWS Config": "Config is like a photographic history of how your infrastructure looked over time.",
        "AWS X-Ray": "X-Ray is like a medical scan for request flow through a distributed application.",
        "Amazon SQS": "SQS is like a numbered task tray where work waits until a worker is free.",
        "Amazon SNS": "SNS is like a loudspeaker announcement that many listeners can hear at once.",
        "Amazon EventBridge": "EventBridge is like a central event switchboard that forwards each event to the right departments based on matching rules.",
        "Amazon MQ": "Amazon MQ is like renting a managed version of the broker room your legacy systems already know how to talk to.",
        "Amazon Athena": "Athena is like bringing a SQL magnifying glass to files already stored in S3 without setting up a full analytics cluster.",
        "Amazon EMR": "EMR is like renting a distributed data factory for heavy Spark and Hadoop jobs.",
        "AWS Glue": "Glue is like the librarian and workshop manager of a data lake. It catalogs the books and also runs transformation jobs.",
        "Amazon Kinesis": "Kinesis is like a moving conveyor belt of events instead of a pile of files.",
        "Amazon QuickSight": "QuickSight is like the presentation room where business people actually see and use the numbers.",
        "AWS CodeCommit": "CodeCommit is like a private Git vault hosted inside AWS governance boundaries.",
        "AWS CodeBuild": "CodeBuild is like a disposable workshop that appears, builds your software, and disappears.",
        "AWS CodeDeploy": "CodeDeploy is like a controlled release manager that decides how a new revision reaches production safely.",
        "AWS CodePipeline": "CodePipeline is like the assembly line that coordinates the whole software release journey.",
        "AWS CloudFormation": "CloudFormation is like architectural blueprints that can rebuild the same cloud building repeatedly.",
        "Amazon SageMaker": "SageMaker is like a full machine learning campus with labs, training grounds, model registry shelves, and serving lanes.",
        "Amazon Rekognition": "Rekognition is like a managed visual inspection assistant for images and video.",
        "Amazon Comprehend": "Comprehend is like a language analyst that reads text and highlights meaning, entities, and sentiment.",
        "Amazon Lex": "Lex is like a task-oriented receptionist bot that follows structured conversation paths.",
        "Amazon Polly": "Polly is like a text reader who can convert written words into spoken audio on demand.",
        "Amazon Textract": "Textract is like a document clerk that reads forms and tables instead of only raw text.",
        "AWS Database Migration Service": "DMS is like a moving truck that keeps carrying new boxes even while the old office is still operating.",
        "AWS Application Migration Service": "Application Migration Service is like lifting an old building onto a new plot of land before you renovate it.",
        "AWS DataSync": "DataSync is like a high-speed moving crew for files and storage systems.",
        "AWS Transfer Family": "Transfer Family is like opening a managed SFTP/FTP reception door so partners can keep using the protocol they already understand.",
    }
    return specific.get(name, f"{name} can be understood as a managed {category.lower()} building block that reduces repeated engineering work.")


def problem_before(name: str, category: str) -> str:
    custom = {
        "Amazon EC2": "Before EC2, teams bought servers, waited for hardware, racked machines, and guessed capacity months in advance. Even small experiments required infrastructure planning and up-front capital expense.",
        "AWS Lambda": "Before Lambda, even tiny event-driven tasks often required a full server, a cron machine, or a permanently running worker process. That meant paying for idle capacity and patching machines whose only real job was to wait.",
        "Amazon ECS": "Before ECS, teams either ran containers manually on EC2 or took on a more complex orchestrator earlier than they were ready for. Placement, health replacement, service discovery, and scaling had to be stitched together by hand.",
        "Amazon EKS": "Before EKS, teams wanting Kubernetes on AWS had to run and upgrade the control plane themselves, which meant owning etcd, masters, upgrades, certificates, and cluster failure modes.",
        "Amazon S3": "Before S3, durable object storage often meant running file servers, scaling NAS devices, or inventing custom replication for large blobs and archives.",
        "Amazon DynamoDB": "Before DynamoDB, teams chasing very high scale often had to shard databases manually, fight hot keys, and build custom operational automation for throughput spikes.",
        "Amazon CloudFront": "Before CloudFront, global users pulled every request from a distant origin, which increased latency and put unnecessary load on origin infrastructure.",
        "AWS IAM": "Before IAM matured into today's central model, teams overused root credentials, long-lived access keys, or broad shared accounts that destroyed least privilege.",
        "Amazon CloudWatch": "Before CloudWatch, many teams ran fragmented monitoring stacks or had blind spots between AWS metrics, application metrics, and logs.",
        "Amazon EventBridge": "Before EventBridge, event producers often knew too much about each consumer, or teams used queues and topics for routing logic that became hard to evolve.",
        "AWS CloudFormation": "Before CloudFormation, infrastructure often lived in click-ops, wikis, and individual memory, which made repeatability and disaster recovery weak.",
        "Amazon Textract": "Before Textract, teams often ran raw OCR and still had to build form parsing, table extraction, and validation layers themselves.",
        "AWS Database Migration Service": "Before DMS, low-downtime migration meant hand-built replication, long cutovers, or painful export/import windows.",
    }
    if name in custom:
        return custom[name]
    category_defaults = {
        "Compute": "Before this managed service existed, teams usually assembled the same capability by combining servers, scripts, custom schedulers, or heavy operational runbooks.",
        "Storage": "Before this service, teams often overloaded local disks, NAS devices, or backup products for workloads that needed better durability, elasticity, or simpler access patterns.",
        "Databases": "Before this service, teams either ran databases themselves or stretched the wrong database model across workloads it was never meant to handle.",
        "Networking": "Before this service, teams often hard-coded routes, exposed systems too broadly, or built custom network glue that became fragile as scale increased.",
        "Security": "Before this service, teams relied on manual controls, static secrets, or scattered security tooling that did not scale well with cloud growth.",
        "Monitoring": "Before this service, teams lacked a consistent way to observe behavior, explain failures, or prove what changed over time.",
        "Messaging": "Before this service, applications were more tightly coupled, bursts were harder to absorb, and retry/fan-out logic lived inside business code.",
        "Analytics": "Before this service, teams had to run more infrastructure or write more plumbing just to ask questions of data.",
        "DevOps": "Before this service, release and infrastructure workflows often depended on servers, scripts, and manual human coordination.",
        "AI/ML": "Before this service, teams either built custom AI/ML pipelines from scratch or skipped the capability entirely because the engineering cost was too high.",
        "Migration": "Before this service, moving data and workloads to AWS required more downtime, more custom tooling, or much more manual coordination.",
    }
    return category_defaults.get(category, "Before this service, teams solved the problem in a more manual and less scalable way.")


def beginner_scenario(name: str, category: str) -> str:
    specific = {
        "Amazon EC2": "Imagine a beginner team building an online bookstore. The admin panel, inventory batch jobs, and image resizing worker all run on Linux servers they want to configure fully. EC2 gives them the familiar server model they already understand.",
        "AWS Lambda": "Imagine a small app where a profile picture should be resized every time a user uploads an image. A permanent server waiting for occasional uploads would be wasteful, but Lambda can react instantly when S3 receives the file.",
        "Amazon ECS": "Imagine a startup with three Dockerized services: web API, background worker, and notification service. The team wants containers, load balancing, and autoscaling, but does not want to become a Kubernetes platform team on day one.",
        "Amazon EKS": "Imagine a company with many teams, strong Kubernetes skills, GitOps tooling, and platform engineers who want one standard way to run containers across environments. EKS becomes the managed AWS home for that platform model.",
        "AWS Elastic Beanstalk": "Imagine a beginner team with a simple Spring Boot application that only needs a managed way to deploy, scale, and expose the app without designing every AWS resource from scratch.",
        "AWS Batch": "Imagine a data team generating nightly reports for 50,000 customers. The work is heavy, scheduled, and non-interactive. That is exactly the kind of pipeline Batch handles well.",
        "Amazon Lightsail": "Imagine a student or solo founder who wants to launch a simple website, a small blog, or a prototype backend in one evening and prefers predictable monthly cost.",
        "Amazon S3": "Imagine a learning platform storing course videos, PDF notes, screenshots, and application backups. Those are objects, not database rows or shared mounted files, so S3 fits naturally.",
        "Amazon EBS": "Imagine a PostgreSQL database running on EC2. The server needs a reliable disk for the operating system and database files. EBS is the right persistence layer underneath that VM.",
        "Amazon EFS": "Imagine several application instances that all need access to the same uploaded files directory. Instead of copying files between servers, the team mounts one shared EFS filesystem.",
        "Amazon RDS": "Imagine a beginner team building an e-commerce app with customers, orders, payments, and invoices. They need SQL, transactions, foreign keys, and backups, but they do not want to maintain database servers manually.",
        "Amazon DynamoDB": "Imagine a mobile game storing player profile state, inventory, and session data at massive scale with low latency. Query patterns are known, so DynamoDB becomes very attractive.",
        "Amazon Redshift": "Imagine a company that already has order, payment, and marketing data but now wants dashboards for leadership, finance, and product analytics. That is a warehouse problem, not an OLTP problem.",
        "Amazon VPC": "Imagine building a secure three-tier app: public load balancer, private app servers, and private database subnets. VPC is the network foundation that makes that design possible.",
        "Amazon Route 53": "Imagine a team running a blue environment and a green environment during a release. Route 53 can gradually shift DNS traffic between them.",
        "Amazon CloudFront": "Imagine students downloading PDFs and images from many countries. If every request goes to one region, the experience is slow. CloudFront places cached copies closer to users.",
        "Elastic Load Balancing": "Imagine four identical application servers behind one application domain. A load balancer is what turns those separate servers into one reliable customer entry point.",
        "Amazon API Gateway": "Imagine a serverless app where mobile clients call order, payment, and profile APIs. API Gateway becomes the managed API front door with auth and throttling.",
        "AWS IAM": "Imagine a junior engineer who should deploy only to staging, not production. IAM is where that boundary is defined.",
        "Amazon Cognito": "Imagine a beginner building a customer-facing app that needs sign-up, login, forgotten password, and social sign-in without building identity flows from scratch.",
        "AWS Secrets Manager": "Imagine a team that keeps database passwords in `.env` files and chat messages. Secrets Manager is introduced to stop that unsafe pattern.",
        "Amazon CloudWatch": "Imagine your app is slow at random times. Without metrics and logs you are guessing. CloudWatch gives the beginner team a first observability control room.",
        "AWS CloudTrail": "Imagine an S3 bucket policy suddenly changes and nobody admits it. CloudTrail is the source of truth for who made the API call.",
        "AWS Config": "Imagine leadership asks, 'How many buckets were public last month?' Config is the service that can answer that state-over-time question.",
        "Amazon SQS": "Imagine checkout requests create email jobs, invoice jobs, and stock reservation jobs. Instead of doing them inline, the app places tasks on SQS and returns quickly.",
        "Amazon SNS": "Imagine a new order should notify email service, analytics, billing, and fraud detection. SNS allows one event to fan out to many listeners.",
        "Amazon EventBridge": "Imagine many services publish business events such as `OrderPlaced`, `PaymentCaptured`, and `InvoiceGenerated`. EventBridge routes each event to the right downstream systems without tight coupling.",
        "Amazon Athena": "Imagine the team has raw CSV or Parquet data in S3 and wants answers today, not after building a whole analytics cluster. Athena is ideal for that first step.",
        "AWS Glue": "Imagine a data lake full of files nobody can query consistently because schemas are unknown and raw data is messy. Glue catalogs and transforms it into something usable.",
        "Amazon Kinesis": "Imagine an app generating clickstream events every second and the business wants near real-time dashboards. Kinesis is the moving event backbone for that pattern.",
        "AWS CloudFormation": "Imagine a beginner successfully builds one environment by hand and then realizes they need the same thing in dev, staging, prod, and disaster recovery. CloudFormation makes that repeatable.",
        "Amazon SageMaker": "Imagine a product team wants a fraud model they control end-to-end. A task-specific pretrained API is not enough. They need a proper ML platform.",
        "Amazon Textract": "Imagine a business receives thousands of invoices and forms each week and wants to extract fields automatically before humans only review exceptions.",
        "AWS DataSync": "Imagine an on-prem file share full of terabytes of project files that must move into AWS without a long manual copy effort. DataSync is built for that kind of movement.",
    }
    if name in specific:
        return specific[name]
    return f"Imagine a beginner team in the {category.lower()} space trying to solve a real product problem. {name} exists so they do not need to assemble every moving part manually before delivering value."


def external_comparisons(name: str) -> list[tuple[str, str]]:
    mapping = {
        "Amazon EC2": [("Azure Virtual Machines", "Very similar VM idea; choose by ecosystem, region, and enterprise alignment."), ("Google Compute Engine", "Strong VM alternative with different networking and platform defaults."), ("DigitalOcean Droplets", "Simpler VPS feel for smaller workloads, but not AWS-scale ecosystem depth.")],
        "AWS Lambda": [("Azure Functions", "Direct serverless functions alternative with Azure integrations."), ("Google Cloud Functions / Cloud Run", "Common GCP paths for event or container-style serverless execution."), ("OpenFaaS / Knative", "Self-managed or Kubernetes-based serverless style with more operational burden.")],
        "Amazon ECS": [("Google Cloud Run", "Higher-level container execution for simpler services, but less ECS-style service model."), ("HashiCorp Nomad", "Simpler scheduler alternative for some teams, but smaller ecosystem than AWS + ECS integration."), ("Docker Swarm", "Easier to start historically, but far less dominant and less AWS-managed.")],
        "Amazon EKS": [("Google Kubernetes Engine", "One of the strongest Kubernetes managed offerings and a natural GCP comparison."), ("Azure Kubernetes Service", "Azure's managed Kubernetes equivalent."), ("Self-managed Kubernetes", "Maximum control but significantly more operational work.")],
        "AWS Elastic Beanstalk": [("Heroku", "Classic developer PaaS comparison for app deployment simplicity."), ("Azure App Service", "Managed app hosting with less infrastructure work."), ("Google App Engine", "PaaS-style runtime deployment with opinionated platform tradeoffs.")],
        "AWS Batch": [("Google Cloud Batch", "Managed batch scheduling equivalent on GCP."), ("Azure Batch", "Azure's batch compute platform."), ("Apache Airflow + custom workers", "Workflow orchestration plus compute, but with more assembly required.")],
        "Amazon Lightsail": [("DigitalOcean", "Common starter-hosting comparison."), ("Linode", "Simple VPS model similar in spirit."), ("Hetzner Cloud", "Cost-attractive VPS alternative depending on region and needs.")],
        "Amazon S3": [("Google Cloud Storage", "Closest cloud object storage comparison."), ("Azure Blob Storage", "Azure object store equivalent."), ("MinIO", "S3-compatible object storage often used outside AWS.")],
        "Amazon EBS": [("Google Persistent Disk", "Block storage equivalent attached to VMs."), ("Azure Managed Disks", "Azure VM disk equivalent."), ("Ceph RBD", "Self-managed block storage pattern with far more operational work.")],
        "Amazon EFS": [("Azure Files", "Managed shared file storage in Azure."), ("Google Filestore", "Managed NFS-like file storage on GCP."), ("NetApp / NAS appliances", "Traditional shared file alternative with more infrastructure ownership.")],
        "Amazon FSx": [("Azure NetApp Files", "High-performance managed enterprise file services."), ("Google Filestore Enterprise / NetApp options", "Managed file systems with protocol/performance specialization."), ("Self-managed Windows/Lustre/ONTAP", "Possible but operationally expensive.")],
        "Amazon S3 Glacier": [("Azure Archive Storage", "Cold object archive equivalent."), ("Google Archive Storage", "GCP cold archive tier."), ("Tape libraries / backup vaults", "Traditional archive approach with more physical or operational burden.")],
        "AWS Storage Gateway": [("Azure StorSimple (legacy pattern) / Azure File Sync concepts", "Hybrid bridge ideas on Azure."), ("NetApp hybrid storage gateways", "Enterprise hybrid storage approach."), ("DIY caching gateway", "Possible but painful to operate and support.")],
        "Amazon RDS": [("Azure SQL / Azure Database services", "Managed relational equivalents in Azure."), ("Cloud SQL", "Managed relational databases on GCP."), ("Self-managed PostgreSQL/MySQL on VMs", "More control, much more toil.")],
        "Amazon Aurora": [("Cloud SQL + HA patterns", "Comparable managed relational story but different internals."), ("Azure Database for PostgreSQL/MySQL", "Managed relational equivalents with different performance characteristics."), ("CockroachDB / YugabyteDB", "Distributed SQL alternatives with different tradeoffs.")],
        "Amazon DynamoDB": [("Azure Cosmos DB", "Major managed NoSQL competitor."), ("Google Cloud Bigtable / Firestore", "GCP alternatives depending on access pattern."), ("Apache Cassandra", "Powerful distributed NoSQL but much more operationally heavy when self-managed.")],
        "Amazon ElastiCache": [("Azure Cache for Redis", "Direct managed Redis comparison."), ("Google Memorystore", "Managed Redis/Memcached on GCP."), ("Self-managed Redis", "More control but much more operational burden.")],
        "Amazon Neptune": [("Neo4j Aura", "Managed graph database comparison."), ("TigerGraph", "Graph analytics alternative."), ("JanusGraph + storage backend", "Open-source route with significant assembly and ops.")],
        "Amazon DocumentDB": [("MongoDB Atlas", "The most common managed document DB comparison."), ("Azure Cosmos DB Mongo API", "Document-oriented managed alternative."), ("Self-managed MongoDB", "More flexibility, more operational burden.")],
        "Amazon Redshift": [("Snowflake", "Major warehouse comparison with different operating and pricing model."), ("BigQuery", "Serverless analytics competitor on GCP."), ("Azure Synapse", "Azure analytics warehouse counterpart.")],
        "Amazon VPC": [("Azure Virtual Network", "Core private network equivalent."), ("Google VPC", "Equivalent networking boundary in GCP."), ("Traditional VLAN/network segmentation", "On-prem analogue with more hardware context.")],
        "Amazon Route 53": [("Azure DNS / Traffic Manager", "DNS and traffic steering comparison."), ("Cloud DNS / Cloud Load Balancing DNS patterns", "GCP alternatives depending on routing need."), ("NS1 / Cloudflare DNS", "External DNS providers with rich traffic management.")],
        "Amazon CloudFront": [("Cloudflare CDN", "Major edge CDN comparison."), ("Azure Front Door", "Azure global edge delivery and protection option."), ("Google Cloud CDN", "GCP CDN equivalent.")],
        "Elastic Load Balancing": [("NGINX / HAProxy", "Self-managed load balancing path with more control and more ops."), ("Azure Load Balancer / Application Gateway", "Azure equivalents depending on protocol."), ("Google Cloud Load Balancing", "Managed global/regional balancing alternative.")],
        "Amazon API Gateway": [("Apigee", "Full API management platform comparison."), ("Azure API Management", "Azure managed API gateway and management product."), ("Kong / Tyk", "Self-managed or hybrid API gateway alternatives.")],
        "AWS Direct Connect": [("Azure ExpressRoute", "Private dedicated hybrid connectivity equivalent."), ("Google Cloud Interconnect", "GCP private network connectivity option."), ("Site-to-site VPN", "Simpler but less predictable internet-based alternative.")],
        "AWS IAM": [("Azure Entra ID + RBAC", "Identity and authorization comparison in Azure."), ("Google Cloud IAM", "Direct IAM model counterpart."), ("Okta + cloud role federation", "Common external identity governance combination.")],
        "Amazon Cognito": [("Auth0", "Popular managed app identity platform."), ("Firebase Authentication", "Common developer-friendly auth alternative."), ("Keycloak", "Open-source identity provider with self-management tradeoffs.")],
        "AWS KMS": [("Azure Key Vault Keys", "Managed keys and crypto controls."), ("Google Cloud KMS", "Direct cloud KMS counterpart."), ("HashiCorp Vault Transit", "External encryption-as-a-service model with more operational ownership.")],
        "AWS Secrets Manager": [("HashiCorp Vault", "Very common secret management comparison."), ("Azure Key Vault Secrets", "Azure managed secret store."), ("Google Secret Manager", "GCP managed secret service.")],
        "AWS WAF": [("Cloudflare WAF", "Edge WAF comparison."), ("Akamai / Imperva WAF", "Enterprise web protection alternatives."), ("ModSecurity", "Open-source WAF path with more tuning burden.")],
        "AWS Shield": [("Cloudflare DDoS protection", "Edge-network DDoS comparison."), ("Akamai Prolexic", "Enterprise DDoS mitigation comparison."), ("On-prem scrubbing appliances", "Traditional but operationally heavier approach.")],
        "Amazon GuardDuty": [("Microsoft Defender for Cloud", "Cloud threat detection and posture comparison."), ("Google Security Command Center", "GCP security visibility comparison."), ("SIEM + custom detections", "Flexible but far more assembly work.")],
        "Amazon CloudWatch": [("Datadog", "Popular SaaS observability platform."), ("Prometheus + Grafana", "Open-source observability stack."), ("New Relic", "Managed monitoring and observability comparison.")],
        "AWS CloudTrail": [("Azure Activity Log", "Cloud control plane audit equivalent."), ("GCP Cloud Audit Logs", "GCP audit equivalent."), ("SIEM-only ingestion", "Possible downstream consumer, but not the original cloud event source.")],
        "AWS Config": [("Azure Policy + Resource Graph", "Configuration and compliance comparison."), ("GCP Config Controller / Asset Inventory", "State and policy comparison."), ("CMDB scripts", "Manual inventory methods with lower reliability.")],
        "AWS X-Ray": [("Jaeger", "Open-source distributed tracing option."), ("Zipkin", "Tracing alternative."), ("Datadog APM / New Relic APM", "Full managed APM competitors.")],
        "Amazon SQS": [("RabbitMQ queues", "Popular queueing alternative with broker semantics."), ("Azure Service Bus queues", "Managed queue comparison in Azure."), ("Google Pub/Sub pull subscriptions", "Cloud messaging alternative with different model.")],
        "Amazon SNS": [("Google Pub/Sub topics", "Managed publish/subscribe comparison."), ("Azure Service Bus topics", "Topic-based fan-out equivalent."), ("Kafka topic broadcasting", "Possible but a much heavier platform for simple notifications.")],
        "Amazon EventBridge": [("Azure Event Grid", "Closest cloud event-routing comparison."), ("Google Eventarc", "Event routing alternative in GCP."), ("Kafka + routing services", "Possible but much more platform assembly work.")],
        "Amazon MQ": [("Azure Service Bus / self-managed RabbitMQ", "Protocol and broker comparisons depending on need."), ("Google Pub/Sub + custom bridges", "Possible but not a direct protocol-broker match."), ("Self-managed ActiveMQ", "Direct like-for-like without the managed ops reduction.")],
        "Amazon Athena": [("BigQuery", "Serverless analytics comparison, though BigQuery is more warehouse-like."), ("Azure Synapse serverless SQL", "Serverless lake query comparison."), ("Trino/Presto clusters", "Open-source route with more infrastructure management.")],
        "Amazon EMR": [("Databricks", "Major Spark platform comparison."), ("Google Dataproc", "Managed Spark/Hadoop equivalent."), ("Self-managed Hadoop/Spark", "More control, much more operational burden.")],
        "AWS Glue": [("Azure Data Factory", "Managed data integration comparison."), ("Google Dataflow + Data Catalog patterns", "Comparable data engineering ecosystem pieces."), ("Apache Airflow + Spark scripts", "Common custom alternative with more assembly work.")],
        "Amazon Kinesis": [("Apache Kafka", "Most common streaming comparison."), ("Confluent Cloud", "Managed Kafka comparison."), ("Azure Event Hubs", "Managed streaming event bus alternative.")],
        "Amazon QuickSight": [("Power BI", "Very common BI comparison."), ("Tableau", "Popular analytics visualization alternative."), ("Looker", "Semantic-model-oriented analytics comparison.")],
        "AWS CodeCommit": [("GitHub", "Most common hosted Git comparison."), ("GitLab", "Integrated DevOps platform comparison."), ("Bitbucket", "Alternative managed Git collaboration platform.")],
        "AWS CodeBuild": [("GitHub Actions runners", "Managed CI execution comparison."), ("GitLab CI runners", "Pipeline runner alternative."), ("Jenkins agents", "Traditional self-managed build worker comparison.")],
        "AWS CodeDeploy": [("Argo Rollouts", "Progressive deployment alternative in Kubernetes environments."), ("Spinnaker", "Deployment orchestration comparison."), ("Octopus Deploy", "Release deployment tool comparison.")],
        "AWS CodePipeline": [("GitHub Actions", "Pipeline orchestration comparison."), ("GitLab CI/CD", "Integrated pipeline platform comparison."), ("Jenkins pipelines", "Traditional highly flexible self-managed option.")],
        "AWS CloudFormation": [("Terraform", "Most common infrastructure-as-code comparison."), ("Pulumi", "Code-first infrastructure definition alternative."), ("Ansible + scripts", "Possible infra automation path, but weaker declarative state management.")],
        "Amazon SageMaker": [("Azure Machine Learning", "Managed ML platform comparison."), ("Vertex AI", "GCP end-to-end ML platform comparison."), ("Databricks ML", "Alternative ML/data platform path.")],
        "Amazon Rekognition": [("Google Vision AI", "Managed vision API comparison."), ("Azure AI Vision", "Computer vision comparison."), ("OpenCV + custom models", "Flexible but much more engineering work.")],
        "Amazon Comprehend": [("Google Cloud Natural Language", "Managed NLP API comparison."), ("Azure AI Language", "Azure NLP alternative."), ("spaCy / Hugging Face pipelines", "Open-source approach with more model ownership.")],
        "Amazon Lex": [("Dialogflow", "Major managed conversational platform comparison."), ("Azure Bot Service", "Bot platform comparison."), ("Rasa", "Open-source conversational framework with more self-management.")],
        "Amazon Polly": [("Google Cloud Text-to-Speech", "Managed TTS comparison."), ("Azure Speech", "Speech service alternative."), ("ElevenLabs / custom voice providers", "External speech options depending on product needs.")],
        "Amazon Textract": [("Google Document AI", "Strong document understanding comparison."), ("Azure Document Intelligence", "Managed forms/document extraction alternative."), ("OCR engines + custom parsing", "Traditional pipeline with more custom engineering.")],
        "AWS Database Migration Service": [("Azure Database Migration Service", "Managed database migration counterpart."), ("Google Database Migration Service", "GCP migration alternative."), ("GoldenGate / custom replication", "Traditional migration path with more setup complexity.")],
        "AWS Application Migration Service": [("Azure Migrate", "Migration planning and rehost comparison."), ("Google Migrate to Virtual Machines", "Lift-and-shift VM migration alternative."), ("Manual rebuild on EC2", "Possible but slower and more error-prone at scale.")],
        "AWS DataSync": [("rsync / robocopy", "DIY transfer tools with less orchestration and verification at scale."), ("Azure Data Box / File Sync patterns", "Azure data movement comparisons depending on online/offline mode."), ("Google Storage Transfer Service", "Cloud transfer alternative in GCP.")],
        "AWS Transfer Family": [("Azure Blob SFTP / managed transfer products", "Managed protocol endpoint comparison."), ("MOVEit / GoAnywhere", "Enterprise managed file transfer alternatives."), ("Self-managed SFTP servers", "Traditional but operationally heavier approach.")],
    }
    return mapping.get(name, [("Azure equivalent", "Cloud comparison in Azure."), ("GCP equivalent", "Cloud comparison in Google Cloud."), ("Self-managed alternative", "Usually more control but more operational burden.")])


def management_split(category: str, name: str) -> tuple[list[str], list[str]]:
    by_category = {
        "Compute": (
            ["Underlying service control plane, fleet plumbing, and some degree of scaling/placement depending on the compute model."],
            ["Application code, release process, runtime tuning, cost decisions, security posture, and architecture fit."],
        ),
        "Storage": (
            ["Durability engineering, replication, storage hardware lifecycle, and managed service availability."],
            ["Data classification, naming, lifecycle rules, access control design, and restore strategy."],
        ),
        "Databases": (
            ["Engine operations, patching, backups in managed models, and service-level availability plumbing."],
            ["Schema design, indexing, query patterns, data model quality, and application behavior."],
        ),
        "Networking": (
            ["Managed network service infrastructure and service-level routing availability."],
            ["Topology design, CIDR planning, exposure model, traffic policy, and failure-domain choices."],
        ),
        "Security": (
            ["Managed control plane mechanics and service durability."],
            ["Security policy quality, least privilege, incident response, and governance discipline."],
        ),
        "Monitoring": (
            ["Telemetry platform plumbing, retention controls, and service integrations."],
            ["Signal design, naming, alert quality, dashboard usefulness, and response playbooks."],
        ),
        "Messaging": (
            ["Core queue/topic/bus durability and managed control plane behavior."],
            ["Event contracts, retry/idempotency design, ordering expectations, and consumer ownership."],
        ),
        "Analytics": (
            ["Managed analytics engine infrastructure and scaling primitives."],
            ["Data model quality, partitioning, semantics, metric definitions, and governance."],
        ),
        "DevOps": (
            ["Managed pipeline/build/deploy control plane capabilities."],
            ["Build discipline, release strategy, test quality, and infrastructure standards."],
        ),
        "AI/ML": (
            ["Managed platform plumbing and API/runtime infrastructure."],
            ["Data quality, prompt/model choice, evaluation criteria, and business-safe usage patterns."],
        ),
        "Migration": (
            ["Managed migration mechanics and transport tooling."],
            ["Cutover planning, validation, rollback strategy, and post-migration modernization."],
        ),
    }
    aws_items, you_items = by_category.get(category, (["The managed backbone of the service."], ["The architecture and usage decisions."]))
    if name == "AWS Lambda":
        aws_items = aws_items + ["Server fleet provisioning and patching for function execution."]
        you_items = you_items + ["Cold-start sensitivity, dependency packaging, and downstream throttling design."]
    if name == "Amazon EC2":
        aws_items = ["The physical server, hypervisor layer, and instance lifecycle APIs."]
        you_items = ["The guest OS, patches, agent setup, runtime stack, and most of the day-two operations."]
    if name == "AWS IAM":
        aws_items = ["The identity control plane and policy evaluation engine."]
        you_items = ["Actual permission boundaries, trust relationships, and human access hygiene."]
    return aws_items, you_items


def architecture_diagram(category: str, service: ServiceEntry) -> str:
    name = service.name
    if category == "Compute":
        return f"""Users / Events
    |
    v
{name}
    |
    +--> App code / services
    |
    +--> Data store / cache
    |
    +--> Logs / metrics / traces"""
    if category == "Storage":
        return f"""Application / Backup / Analytics job
    |
    v
{name}
    |
    +--> Durable stored data
    |
    +--> Lifecycle / archive / replication
    |
    +--> Restore or read path"""
    if category == "Databases":
        return f"""Application
    |
    v
{name}
    |
    +--> Primary data model
    |
    +--> Queries / indexes / replicas
    |
    +--> Backup / analytics / downstream events"""
    if category == "Networking":
        return f"""Client / Office / Partner
    |
    v
{name}
    |
    +--> Routing / balancing / edge policy
    |
    +--> Application targets
    |
    +--> Observability / security controls"""
    if category == "Security":
        return f"""User / App / Request
    |
    v
{name}
    |
    +--> Allow / deny / encrypt / detect
    |
    +--> Protected AWS resource or application path
    |
    +--> Audit / alert output"""
    if category == "Monitoring":
        return f"""Application / AWS resources
    |
    +--> Metrics
    +--> Logs
    +--> Traces / state / audit events
             |
             v
           {name}
             |
             +--> Dashboard / alarm / investigation"""
    if category == "Messaging":
        return f"""Producer
    |
    v
{name}
    |
    +--> One or more consumers
    |
    +--> Retries / dead-letter / replay depending on pattern"""
    if category == "Analytics":
        return f"""Raw data / stream / operational source
    |
    v
{name}
    |
    +--> Query / transform / aggregate
    |
    +--> Dashboard / warehouse / curated output"""
    if category == "DevOps":
        return f"""Source code / infra code
    |
    v
{name}
    |
    +--> Build / test / deploy / stack update
    |
    +--> Logs / approvals / promoted release"""
    if category == "AI/ML":
        return f"""Data / text / image / voice / document
    |
    v
{name}
    |
    +--> Analysis / training / inference
    |
    +--> Product workflow or human review"""
    if category == "Migration":
        return f"""Source system
    |
    v
{name}
    |
    +--> Move / replicate / validate
    |
    +--> AWS target
    |
    +--> Cutover or ongoing sync"""
    return f"Input -> {name} -> Output"


def paragraphize_points(header: str, points: Iterable[str], service_name: str) -> list[str]:
    out: list[str] = []
    for idx, point in enumerate(points, start=1):
        out.append(
            f"{header} point {idx} for {service_name}: {point} "
            f"In beginner terms, this matters because it directly changes either how easy the service is to operate, how much it costs, or how safely it can be used in production. "
            f"When reading AWS documentation, treat this point as something you should actively verify in your own design rather than as a decorative feature list item."
        )
    return out


def comparison_intro(name: str) -> str:
    return (
        f"A common beginner mistake is to compare {name} only by feature checklists. "
        f"The more useful comparison is to ask: what job is this service trying to make easier, what operational burden does it remove, and what new limitations does it introduce in exchange?"
    )


def when_not_to_use(service: ServiceEntry) -> str:
    if service.disadvantages:
        joined = " ".join(service.disadvantages[:3])
        return (
            f"You should actively avoid {service.name} when the architecture is drifting into its weak zone. "
            f"The current data for this service already signals that clearly: {joined} "
            f"If your design depends on ignoring those warnings, it usually means another service or a simpler architecture would fit better."
        )
    return f"Avoid {service.name} when the workload does not match the problem this service was built to solve."


def beginner_flow(name: str, category: str) -> list[str]:
    if category == "Compute":
        return [
            "A user request or event arrives.",
            f"{name} receives or hosts the application logic.",
            "The application reads or writes data to a backing store.",
            "Logs, metrics, and traces are emitted so the team can observe behavior.",
            "Scaling or scheduling changes capacity as traffic or workload changes.",
        ]
    if category == "Storage":
        return [
            "An application, batch job, or user creates data.",
            f"{name} stores the data using its own access model.",
            "Security and lifecycle rules control who can read it and how long it stays hot.",
            "Another service restores, queries, or processes the data later.",
        ]
    if category == "Databases":
        return [
            "The application issues a read or write using the data model the service expects.",
            f"{name} persists, indexes, or distributes the data according to its engine behavior.",
            "Operational mechanisms such as backups, replicas, or scaling protect the workload.",
            "Downstream analytics, caching, or integration services consume the results.",
        ]
    if category == "Networking":
        return [
            "A client or partner sends network traffic.",
            f"{name} routes, accelerates, or filters that traffic.",
            "Only healthy and allowed downstream targets receive the request.",
            "Observability and security services record what happened.",
        ]
    if category == "Security":
        return [
            "A user, application, or request attempts an action.",
            f"{name} evaluates identity, secret, encryption, or protection rules.",
            "The system either allows, denies, protects, or records the activity.",
            "Audit and response workflows can then act on the result.",
        ]
    if category == "Monitoring":
        return [
            "Applications and infrastructure emit telemetry or state changes.",
            f"{name} receives, stores, correlates, or evaluates those signals.",
            "Dashboards, alarms, and investigations reveal whether the system is healthy.",
            "The team uses that feedback to improve reliability and design choices.",
        ]
    if category == "Messaging":
        return [
            "A producer creates a message or event.",
            f"{name} buffers, broadcasts, or routes that message according to its model.",
            "One or more consumers process the work independently.",
            "Failures are retried, rerouted, or isolated instead of breaking the producer immediately.",
        ]
    if category == "Analytics":
        return [
            "Raw data lands in storage or arrives as a stream.",
            f"{name} queries, transforms, or aggregates that data.",
            "A curated result becomes available to analysts, dashboards, or downstream systems.",
            "The business acts on insight instead of raw records.",
        ]
    if category == "DevOps":
        return [
            "A code or infrastructure change is committed.",
            f"{name} participates in build, release, or provisioning flow.",
            "Automation verifies quality and pushes the change toward the target environment.",
            "Logs and approval steps make the release visible and repeatable.",
        ]
    if category == "AI/ML":
        return [
            "Text, images, documents, or training data enter the workflow.",
            f"{name} analyzes, transforms, trains, or serves intelligence on top of that input.",
            "A product feature or decision workflow consumes the result.",
            "Humans may review uncertain outcomes depending on risk and domain sensitivity.",
        ]
    if category == "Migration":
        return [
            "A source system is identified and validated.",
            f"{name} moves, replicates, or exposes the data/workload to AWS.",
            "The team verifies correctness, performance, and cutover readiness.",
            "Production is switched in a planned and reversible way where possible.",
        ]
    return [f"{name} receives input.", "The service processes it.", "Downstream systems consume the result."]


def faq_for(service: ServiceEntry, category: str) -> list[tuple[str, str]]:
    return [
        (f"What problem is {service.name} really solving?", f"In plain language, {service.name} exists to make a repeated {category.lower()} problem easier, safer, or faster than the fully manual alternative."),
        (f"What is the biggest beginner mistake with {service.name}?", f"The biggest mistake is using {service.name} because it sounds modern or popular rather than because the workload genuinely matches the service model."),
        (f"Can {service.name} be the default choice for every project?", f"No. Good cloud design comes from fit, not habit. {service.name} is strong in its target zone and weaker outside it."),
        (f"What should I learn first before using {service.name} in production?", f"Start with the problem it solves, the failure modes it introduces, the cost model, and how to monitor it."),
        (f"How do I become confident designing with {service.name}?", f"Study one realistic use case, draw the request or data flow, identify what AWS manages versus what you manage, and compare it with at least one adjacent service and one outside-AWS alternative."),
    ]


def review_questions(service: ServiceEntry) -> list[str]:
    return [
        f"Why is {service.name} a better fit than the closest alternative for this workload?",
        f"What exactly would break first if {service.name} were used outside its intended design zone?",
        f"Which operational task does {service.name} remove, and which new responsibility does it introduce?",
        f"What signals would tell you that your current usage of {service.name} needs redesign?",
    ]


def styles():
    sheet = getSampleStyleSheet()
    sheet.add(ParagraphStyle(name="BookTitle", parent=sheet["Title"], fontSize=22, leading=26, textColor=colors.HexColor("#12355b"), spaceAfter=12))
    sheet.add(ParagraphStyle(name="Category", parent=sheet["Heading1"], fontSize=17, leading=20, textColor=colors.HexColor("#0b4f6c"), spaceAfter=6))
    sheet.add(ParagraphStyle(name="Service", parent=sheet["Heading1"], fontSize=14.5, leading=18, textColor=colors.HexColor("#1d3557"), spaceBefore=8, spaceAfter=5))
    sheet.add(ParagraphStyle(name="Section", parent=sheet["Heading2"], fontSize=11, leading=13, textColor=colors.HexColor("#2f4858"), spaceBefore=5, spaceAfter=3))
    sheet.add(ParagraphStyle(name="Body", parent=sheet["BodyText"], fontSize=9.2, leading=11.4, spaceAfter=3))
    sheet.add(ParagraphStyle(name="BookBullet", parent=sheet["BodyText"], fontSize=9.0, leading=11.0, leftIndent=10, bulletIndent=0, spaceAfter=2))
    sheet.add(ParagraphStyle(name="Small", parent=sheet["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#555555"), spaceAfter=3))
    sheet.add(ParagraphStyle(name="BookCode", parent=sheet["BodyText"], fontName="Courier", fontSize=7.2, leading=8.4, leftIndent=6, rightIndent=6, borderPadding=4, backColor=colors.HexColor("#f8fafc"), borderWidth=0.4, borderColor=colors.HexColor("#d7dee9"), spaceBefore=2, spaceAfter=4))
    return sheet


def table(rows: list[tuple[str, str]], widths=(2.1 * inch, 4.7 * inch)):
    data = [["Item", "Explanation"]]
    data.extend(rows)
    t = Table(data, colWidths=list(widths))
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#12355b")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.8),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def add_bullets(story: list, items: Iterable[str], style):
    for item in items:
            story.append(Paragraph(escape(item), style, bulletText="-"))


def section_page(story: list, sheet, service_name: str, section_title: str, paragraphs: list[str], page_break_after: bool = False, include_service_heading: bool = True):
    if include_service_heading:
        story.append(Paragraph(escape(service_name), sheet["Service"]))
    story.append(Paragraph(escape(section_title), sheet["Section"]))
    for para in paragraphs:
        story.append(Paragraph(escape(para), sheet["Body"]))
    if page_break_after:
        story.append(PageBreak())


def build_markdown() -> str:
    lines: list[str] = []
    lines.append("# AWS Services Master Architect Handbook")
    lines.append("")
    lines.append(f"Validated against official AWS references on {AS_OF_DATE}.")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This handbook is designed for a beginner who wants to understand why AWS services exist, how to visualize them in architecture, how they compare with nearby AWS services and non-AWS tools, and how to choose them with confidence in software design.")
    lines.append("")
    lines.append("## Table of Contents")
    lines.append("")
    for category in CATEGORIES:
        lines.append(f"- {category.name}")
        for service in category.services:
            lines.append(f"  - {service.name}")
    lines.append("")
    for category in CATEGORIES:
        lines.append(f"# {category.name}")
        lines.append("")
        lines.append(category.intro)
        lines.append("")
        for service in category.services:
            lines.append(f"## {service.name}")
            lines.append("")
            lines.append("### Plain-English explanation")
            lines.append("")
            lines.append(service.tagline)
            lines.append("")
            lines.append(analogy_for(service.name, category.name))
            lines.append("")
            lines.append("### Problem before this service")
            lines.append("")
            lines.append(problem_before(service.name, category.name))
            lines.append("")
            lines.append("### Beginner scenario")
            lines.append("")
            lines.append(beginner_scenario(service.name, category.name))
            lines.append("")
            lines.append("### Core flow")
            lines.append("")
            for item in beginner_flow(service.name, category.name):
                lines.append(f"- {item}")
            lines.append("")
            lines.append("### Architecture sketch")
            lines.append("")
            lines.append("```text")
            lines.append(architecture_diagram(category.name, service))
            lines.append("```")
            lines.append("")
            lines.append("### Deep explanation")
            lines.append("")
            lines.append(service.deep_dive)
            lines.append("")
            lines.append("### Core properties explained")
            lines.append("")
            for p in paragraphize_points("Property", service.properties, service.name):
                lines.append(p)
                lines.append("")
            lines.append("### Advantages explained")
            lines.append("")
            for p in paragraphize_points("Advantage", service.advantages, service.name):
                lines.append(p)
                lines.append("")
            lines.append("### Disadvantages explained")
            lines.append("")
            for p in paragraphize_points("Disadvantage", service.disadvantages, service.name):
                lines.append(p)
                lines.append("")
            lines.append("### AWS comparisons")
            lines.append("")
            for left, right in service.comparison:
                lines.append(f"- {left}: {right}")
            lines.append("")
            lines.append("### Non-AWS comparisons")
            lines.append("")
            for left, right in external_comparisons(service.name):
                lines.append(f"- {left}: {right}")
            lines.append("")
            lines.append("### What AWS manages vs what you manage")
            aws_items, you_items = management_split(category.name, service.name)
            lines.append("")
            lines.append("AWS manages:")
            lines.extend([f"- {item}" for item in aws_items])
            lines.append("")
            lines.append("You manage:")
            lines.extend([f"- {item}" for item in you_items])
            lines.append("")
            lines.append("### When not to use it")
            lines.append("")
            lines.append(when_not_to_use(service))
            lines.append("")
            lines.append("### Implementation example")
            lines.append("")
            lines.append(f"**{service.code_title}**")
            lines.append("")
            lines.append("```text")
            lines.append(service.code)
            lines.append("```")
            lines.append("")
            lines.append("### Implementation notes")
            lines.append("")
            lines.extend([f"- {item}" for item in service.implementation_notes])
            lines.append("")
            lines.append("### FAQ")
            lines.append("")
            for q, a in faq_for(service, category.name):
                lines.append(f"**Q: {q}**")
                lines.append("")
                lines.append(a)
                lines.append("")
            lines.append("### Review questions")
            lines.append("")
            for q in review_questions(service):
                lines.append(f"- {q}")
            lines.append("")
    lines.append("# Official AWS Sources")
    lines.append("")
    for label, url in SOURCES:
        lines.append(f"- {label}: {url}")
    return "\n".join(lines)


def build_pdf():
    sheet = styles()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24,
        title="AWS Services Master Architect Handbook",
        author="OpenAI Codex",
    )
    story: list = []

    story.append(Paragraph("AWS Services Master Architect Handbook", sheet["BookTitle"]))
    story.append(Paragraph("A beginner-to-architect handbook for understanding why AWS services exist, when to use them, when not to use them, and how to compare them with confidence.", sheet["Body"]))
    story.append(Paragraph(f"Validated against official AWS references on {AS_OF_DATE}.", sheet["Small"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("How to use this handbook", sheet["Section"]))
    intro_paragraphs = [
        "This version is intentionally much larger than a short reference guide. The goal is not to dump feature lists. The goal is to teach the reader how to think. A beginner should be able to read a service chapter, understand what pain existed before that service, visualize where the service sits in architecture, compare it with alternatives, and make a calmer design choice.",
        "If you are new to AWS, read category introductions first. Then read one service chapter at a time with a notebook and draw the flow yourself. If you are preparing for interviews, focus on the sections called 'problem before this service', 'when not to use it', 'AWS comparisons', and 'review questions'. Those are the parts that turn memorization into judgment.",
        "If you are designing software, ask four questions for every service: what business problem am I solving, what operational burden does this service remove, what new limitations does it introduce, and how will I know later that this was the wrong fit? Good cloud architecture comes from good tradeoff thinking, not from using the most services possible.",
    ]
    for p in intro_paragraphs:
        story.append(Paragraph(p, sheet["Body"]))
    story.append(Paragraph("Table of contents", sheet["Section"]))
    for category in CATEGORIES:
        story.append(Paragraph(f"<b>{escape(category.name)}</b>", sheet["Body"]))
        for service in category.services:
            story.append(Paragraph(escape(service.name), sheet["BookBullet"], bulletText="-"))
    story.append(PageBreak())

    for category in CATEGORIES:
        story.append(Paragraph(escape(category.name), sheet["Category"]))
        story.append(Paragraph(escape(category.intro), sheet["Body"]))
        story.append(
            Paragraph(
                f"The services in the {category.name.lower()} category often appear overlapping to beginners. They are not overlapping in exactly the same way. They exist because the cloud needs different answers for control, scale, latency, operational burden, and team skill level. Read the next chapters with that lens.",
                sheet["Body"],
            )
        )
        story.append(Spacer(1, 4))

        for service in category.services:
            aws_manages, you_manage = management_split(category.name, service.name)
            story.append(Paragraph(escape(service.name), sheet["Service"]))

            # 1 Overview
            section_page(
                story,
                sheet,
                service.name,
                "1. Plain-English explanation and mental model",
                [
                    service.tagline,
                    analogy_for(service.name, category.name),
                    f"In plain English, {service.name} should be thought of as one answer to a very specific {category.name.lower()} problem. The service looks attractive when that problem is truly present in your system. It becomes confusing when teams use it simply because they saw it in another architecture diagram without understanding the original reason it was chosen.",
                    f"The first confidence-building habit with {service.name} is to stop asking only 'What features does it have?' and start asking 'What pain does it remove, and what responsibility does it leave with me?' That shift turns AWS study from memorization into architecture thinking.",
                ],
                include_service_heading=False,
            )

            # 2 Problem before
            section_page(
                story,
                sheet,
                service.name,
                "2. What problem existed before this service and why AWS introduced it",
                [
                    problem_before(service.name, category.name),
                    f"AWS introduced {service.name} because enough customers were repeatedly solving that problem in ways that were slow, risky, expensive, or too operationally heavy. When AWS sees a pattern like that across many customers, it often turns the pattern into a managed service so teams can spend more time on product logic and less time rebuilding infrastructure plumbing.",
                    f"For a beginner, this historical view matters because it explains the DNA of the service. {service.name} was not created to do everything. It was created to solve a particular pain. If your workload has the same pain, the service often feels natural. If your workload has a different pain, the service can feel awkward no matter how popular it is.",
                    f"In interviews and design reviews, this is often where strong answers begin: 'The reason {service.name} exists is that before it, teams had to...' That sentence immediately shows maturity because it proves you understand the service as a response to a real operational problem rather than as an isolated product name.",
                ],
                include_service_heading=False,
            )

            # 3 Managed split
            section_page(
                story,
                sheet,
                service.name,
                "3. What AWS manages versus what you still manage",
                [
                    f"One of the fastest ways to misunderstand {service.name} is to assume 'managed' means 'I no longer need to think.' Managed only means AWS took ownership of part of the stack.",
                    "AWS-managed responsibilities: " + " ".join(aws_manages),
                    "Customer-managed responsibilities: " + " ".join(you_manage),
                    f"This split is the center of architecture confidence. If you know what AWS owns and what your team still owns, you can estimate risk, staffing, monitoring needs, and the skill level required to run {service.name} well in production.",
                ],
                include_service_heading=False,
            )

            # 4 Scenario
            flow = beginner_flow(service.name, category.name)
            section_page(
                story,
                sheet,
                service.name,
                "4. Beginner-friendly scenario and step-by-step flow",
                [
                    beginner_scenario(service.name, category.name),
                    "A simple request or data flow for this service looks like this:",
                    " ".join([f"Step {idx}: {item}" for idx, item in enumerate(flow, start=1)]),
                    f"When a beginner can narrate a flow like this out loud, {service.name} starts feeling less abstract. The service moves from 'cloud vocabulary' into a mental movie of how a real system behaves.",
                ],
                include_service_heading=False,
            )

            # 5 Architecture diagram
            story.append(Paragraph("5. Architecture view and visualization", sheet["Section"]))
            story.append(
                Paragraph(
                    escape(
                        f"The diagram below is not the only valid architecture for {service.name}. It is a teaching diagram meant to help a beginner see where the service sits in relation to users, application logic, and downstream systems."
                    ),
                    sheet["Body"],
                )
            )
            story.append(Preformatted(architecture_diagram(category.name, service), sheet["BookCode"]))
            story.append(
                Paragraph(
                    escape(
                        f"When you design with {service.name}, always redraw the path in your own context. Ask where requests enter, where state lives, where retries happen, how failures are surfaced, and what security or monitoring layers surround the service."
                    ),
                    sheet["Body"],
                )
            )
            story.append(Spacer(1, 4))

            # 6 Deep explanation
            section_page(
                story,
                sheet,
                service.name,
                "6. Deep explanation: how the service behaves architecturally",
                [
                    service.deep_dive,
                    f"The architectural meaning of that description is more important than the marketing summary. {service.name} shapes the design by changing where state lives, how scaling happens, how much coupling exists between components, and who is responsible during failure.",
                    f"If you are trying to design software confidently, the key is not to memorize every feature in {service.name}. Instead, learn the service's behavior under load, its fit for certain workloads, and the hidden cost of using it in the wrong place.",
                    f"Good architects also ask what becomes simpler after choosing {service.name}. If the answer is unclear, the service may not actually be pulling its weight in the design.",
                ],
                include_service_heading=False,
            )

            # 7 Properties
            section_page(
                story,
                sheet,
                service.name,
                "7. Core properties explained in beginner language",
                paragraphize_points("Property", service.properties, service.name)
                + [
                    f"A strong design habit is to convert each property into an architecture question. For example: if one property of {service.name} implies a certain scaling model, what does that mean for cost? What does it mean for debugging? What does it mean for data consistency or user experience?"
                ],
                include_service_heading=False,
            )

            # 8 Advantages
            section_page(
                story,
                sheet,
                service.name,
                "8. Why architects choose this service: advantages explained",
                paragraphize_points("Advantage", service.advantages, service.name)
                + [
                    f"When you explain {service.name} in a design interview, advantages matter most when they are connected to a real system pressure such as speed of delivery, operations burden, latency target, team skill level, or cost shape."
                ],
                include_service_heading=False,
            )

            # 9 Disadvantages
            section_page(
                story,
                sheet,
                service.name,
                "9. Where this service hurts: disadvantages, boundaries, and when not to use it",
                paragraphize_points("Disadvantage", service.disadvantages, service.name)
                + [
                    when_not_to_use(service),
                    f"The beginner trap is to treat disadvantages as minor footnotes. In reality, disadvantages are often the fastest path to choosing the wrong service. Mature design means letting the boundaries of {service.name} influence the decision as much as its strengths do.",
                ],
                include_service_heading=False,
            )

            # 10 AWS comparisons
            story.append(Paragraph("10. AWS-to-AWS comparison", sheet["Section"]))
            story.append(Paragraph(escape(comparison_intro(service.name)), sheet["Body"]))
            story.append(table(service.comparison))
            story.append(
                Paragraph(
                    escape(
                        f"The value of this table is not to crown a winner. It is to teach service fit. Many AWS services sit near each other because they solve adjacent versions of the same problem. The better question is always 'Which one makes this architecture simpler and safer for this exact workload?'"
                    ),
                    sheet["Body"],
                )
            )
            story.append(Spacer(1, 4))

            # 11 external comparisons
            story.append(Paragraph("11. Comparison with similar non-AWS tools and services", sheet["Section"]))
            story.append(
                Paragraph(
                    escape(
                        f"To understand {service.name} deeply, it helps to compare it with non-AWS tools or other cloud equivalents. That comparison should stay conceptual. The goal is not to claim every tool is identical. The goal is to learn the design space."
                    ),
                    sheet["Body"],
                )
            )
            story.append(table(external_comparisons(service.name)))
            story.append(
                Paragraph(
                    escape(
                        f"When you compare {service.name} to outside tools, focus on operating model, not only features. Ask whether the outside alternative is more open, more portable, more ecosystem-rich, or more operationally heavy. That tells you why a team would stay on AWS native tooling or deliberately move away from it."
                    ),
                    sheet["Body"],
                )
            )
            story.append(Spacer(1, 4))

            # 12 implementation
            story.append(Paragraph("12. Beginner implementation walkthrough", sheet["Section"]))
            story.append(
                Paragraph(
                    escape(
                        f"The example below is intentionally small. It is not meant to be a full production blueprint. It is meant to make {service.name} feel concrete enough that a learner can connect architecture theory to an actual command, config, or code shape."
                    ),
                    sheet["Body"],
                )
            )
            story.append(Paragraph(escape(service.code_title), sheet["Section"]))
            story.append(Preformatted(service.code, sheet["BookCode"]))
            for note in service.implementation_notes:
                story.append(Paragraph(escape(note), sheet["BookBullet"], bulletText="-"))
            story.append(
                Paragraph(
                    escape(
                        f"After you understand the snippet, ask yourself what production concerns still remain. Usually those concerns include security, retries, scaling, observability, rollback, and cost control. That is where real architecture begins."
                    ),
                    sheet["Body"],
                )
            )
            story.append(Spacer(1, 4))

            # 13 mistakes and checklist
            checklist = [
                f"State clearly why {service.name} is in the architecture at all.",
                "Define what failure looks like and how it will be detected.",
                "Know which service is the nearest alternative and why you did not choose it.",
                "Know the cost driver for this service.",
                "Know what a beginner on the team would need to understand before operating it safely.",
            ]
            mistakes = [
                f"Using {service.name} because it is popular instead of because it matches the workload.",
                "Ignoring the operational model and focusing only on launch-day convenience.",
                "Failing to define ownership for monitoring, cost, and security boundaries.",
                "Assuming the managed nature of the service removes design responsibility.",
            ]
            section_page(
                story,
                sheet,
                service.name,
                "13. Common mistakes and production-readiness checklist",
                mistakes + checklist,
                include_service_heading=False,
            )

            # 14 FAQ and review
            story.append(Paragraph("14. FAQ, review questions, and confidence-building notes", sheet["Section"]))
            for q, a in faq_for(service, category.name):
                story.append(Paragraph(f"<b>{escape(q)}</b>", sheet["Body"]))
                story.append(Paragraph(escape(a), sheet["Body"]))
            story.append(Paragraph("Review questions", sheet["Section"]))
            add_bullets(story, review_questions(service), sheet["BookBullet"])
            story.append(
                Paragraph(
                    escape(
                        f"If a beginner can answer the questions above without looking at notes, they are moving from AWS vocabulary into AWS judgment. That is the real goal of this handbook."
                    ),
                    sheet["Body"],
                )
            )
            story.append(PageBreak())

    # Appendices
    story.append(Paragraph("Appendix A: Category-level decision lessons", sheet["Category"]))
    for category in CATEGORIES:
        story.append(Paragraph(escape(category.name), sheet["Section"]))
        story.append(
            Paragraph(
                escape(
                    f"In {category.name.lower()}, the smartest designs usually come from choosing the simplest service that still respects the workload's real constraints. Beginners often move too quickly toward the most advanced-looking option. Mature teams ask whether the simpler option would create less operational drag."
                ),
                sheet["Body"],
            )
        )
        story.append(
            Paragraph(
                escape(
                    f"If you are studying {category.name.lower()}, compare the services by these questions: what is the unit of scaling, where does state live, what failure mode is most dangerous, what skills are required to operate the service, and what sign would tell you to migrate away later."
                ),
                sheet["Body"],
            )
        )
    story.append(PageBreak())

    story.append(Paragraph("Appendix B: Service-by-service design exercises", sheet["Category"]))
    story.append(
        Paragraph(
            escape(
                "This appendix is designed to help a learner move from reading into active system design. Each page presents a focused exercise for one service. The goal is not to memorize one 'correct' answer. The goal is to learn how to justify when the service belongs in architecture and when it should be replaced with something simpler or better aligned."
            ),
            sheet["Body"],
        )
    )
    story.append(PageBreak())
    for category in CATEGORIES:
        for service in category.services:
            story.append(Paragraph(escape(service.name), sheet["Service"]))
            story.append(Paragraph("Design exercise", sheet["Section"]))
            exercise_paragraphs = [
                f"You are mentoring a beginner team building a product in the {category.name.lower()} space. They are considering {service.name}. Your first task is to explain, in plain language, the business pressure that would justify introducing this service at all.",
                f"Next, ask the team to draw where {service.name} would sit in the request path or data flow. They should identify the upstream caller, the downstream dependency, one failure mode, one cost driver, and one monitoring signal. If they cannot place those five things clearly, they do not yet understand the service well enough to commit to it.",
                f"Then ask them to compare {service.name} with the nearest AWS alternative and at least one outside-AWS alternative. The exercise is successful only if they can explain not just which option they chose, but what operational burden they deliberately accepted by making that choice.",
                f"Finally, ask the team to state a future redesign trigger. In other words: what signal would tell them that {service.name} is no longer the right fit six months from now? That question is what turns cloud learning into architecture judgment.",
            ]
            for para in exercise_paragraphs:
                story.append(Paragraph(escape(para), sheet["Body"]))
            add_bullets(story, review_questions(service), sheet["BookBullet"])
            story.append(PageBreak())

    story.append(Paragraph("Appendix C: Service revision cards", sheet["Category"]))
    story.append(
        Paragraph(
            escape(
                "This appendix gives a compact but useful revision page for every service. These cards are intentionally repetitive in structure so a learner can revise quickly before interviews, architecture reviews, or certification preparation."
            ),
            sheet["Body"],
        )
    )
    story.append(PageBreak())
    for category in CATEGORIES:
        for service in category.services:
            story.append(Paragraph(escape(service.name), sheet["Service"]))
            story.append(Paragraph("Revision card", sheet["Section"]))
            story.append(Paragraph(escape(f"One-line purpose: {service.tagline}"), sheet["Body"]))
            story.append(Paragraph(escape(f"Why it exists: {problem_before(service.name, category.name)}"), sheet["Body"]))
            story.append(Paragraph(escape(f"Beginner picture: {analogy_for(service.name, category.name)}"), sheet["Body"]))
            story.append(Paragraph(escape(f"Best first use case: {beginner_scenario(service.name, category.name)}"), sheet["Body"]))
            story.append(Paragraph(escape(f"Main warning: {when_not_to_use(service)}"), sheet["Body"]))
            story.append(Paragraph("Remember these points:", sheet["Section"]))
            add_bullets(story, service.properties[:2] + service.advantages[:2] + service.disadvantages[:2], sheet["BookBullet"])
            story.append(Paragraph("Outside-AWS comparison anchors:", sheet["Section"]))
            add_bullets(story, [f"{left}: {right}" for left, right in external_comparisons(service.name)[:2]], sheet["BookBullet"])
            story.append(PageBreak())

    story.append(Paragraph("Appendix D: Category architecture drills", sheet["Category"]))
    story.append(
        Paragraph(
            escape(
                "These drills are meant to connect individual service knowledge back to architecture thinking at the category level. Each page asks the reader to compare several nearby services and defend a design choice in clear beginner-friendly language."
            ),
            sheet["Body"],
        )
    )
    story.append(PageBreak())
    for category in CATEGORIES:
        service_names = ", ".join(service.name for service in category.services[:6])
        story.append(Paragraph(escape(category.name), sheet["Service"]))
        story.append(Paragraph("Architecture drill", sheet["Section"]))
        drill_paragraphs = [
            f"A product team in the {category.name.lower()} space is choosing between these services: {service_names}. Your task as the reviewer is to stop them from selecting on brand familiarity alone. You must force the conversation back toward workload fit, operational burden, and failure behavior.",
            f"First, ask the team to describe the unit of scale in this category. In {category.name.lower()}, that could mean requests, jobs, objects, rows, streams, endpoints, identities, or deployment artifacts depending on the service. If they cannot describe the unit of scale, they are not ready to pick a service confidently.",
            f"Second, ask what the most dangerous mistake in this category looks like. In many {category.name.lower()} decisions, the failure comes from using a service that appears more advanced than the team can operate safely or from choosing a service whose data or traffic model does not match the application.",
            f"Third, ask what simpler option they ruled out and why. Strong architecture is often less about finding the most powerful service and more about proving why the simpler service is no longer enough.",
            f"Finally, ask how they would know they chose wrong after launch. A good answer includes one cost signal, one reliability signal, one developer-experience signal, and one business impact signal. That is how cloud design becomes measurable instead of opinion-based.",
        ]
        for para in drill_paragraphs:
            story.append(Paragraph(escape(para), sheet["Body"]))
        story.append(PageBreak())

    story.append(Paragraph("Appendix E: Official AWS sources", sheet["Category"]))
    story.append(Paragraph(escape(f"The service list and category references were validated on {AS_OF_DATE} against the official AWS sources below."), sheet["Body"]))
    for label, url in SOURCES:
        story.append(Paragraph(f"<b>{escape(label)}</b><br/>{escape(url)}", sheet["Body"]))

    def add_page_number(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        canvas.drawRightString(A4[0] - 38, 22, f"Page {doc.page}")

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main():
    MARKDOWN_PATH.write_text(build_markdown(), encoding="utf-8")
    build_pdf()
    pages = len(PdfReader(str(PDF_PATH)).pages)
    print(f"Markdown written to: {MARKDOWN_PATH}")
    print(f"PDF written to: {PDF_PATH}")
    print(f"PDF pages: {pages}")


if __name__ == "__main__":
    main()
