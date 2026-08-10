from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
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


ROOT = Path(r"D:\Notes")
MARKDOWN_PATH = ROOT / "AWS Services Deep Reference Book.md"
PDF_PATH = ROOT / "AWS Services Deep Reference Book.pdf"
AS_OF_DATE = "April 25, 2026"


@dataclass
class ServiceEntry:
    name: str
    tagline: str
    when_to_use: str
    deep_dive: str
    variations: list[str]
    use_cases: list[str]
    properties: list[str]
    advantages: list[str]
    disadvantages: list[str]
    implementation_notes: list[str]
    comparison: list[tuple[str, str]]
    code_title: str
    code: str


@dataclass
class Category:
    name: str
    intro: str
    services: list[ServiceEntry]


def svc(
    name: str,
    tagline: str,
    when_to_use: str,
    deep_dive: str,
    variations: list[str],
    use_cases: list[str],
    properties: list[str],
    advantages: list[str],
    disadvantages: list[str],
    implementation_notes: list[str],
    comparison: list[tuple[str, str]],
    code_title: str,
    code: str,
) -> ServiceEntry:
    return ServiceEntry(
        name=name,
        tagline=tagline,
        when_to_use=when_to_use,
        deep_dive=deep_dive,
        variations=variations,
        use_cases=use_cases,
        properties=properties,
        advantages=advantages,
        disadvantages=disadvantages,
        implementation_notes=implementation_notes,
        comparison=comparison,
        code_title=code_title,
        code=code.strip(),
    )


CATEGORIES: list[Category] = [
    Category(
        name="Compute",
        intro="Compute services answer one core question: where should application code run? AWS gives you VMs, containers, serverless functions, managed PaaS layers, scheduled batch execution, and simplified VPS-style hosting. The right choice usually depends on how much control you need, how variable your traffic is, and how much operational ownership your team is willing to carry.",
        services=[
            svc(
                name="Amazon EC2",
                tagline="Resizable virtual machines for maximum OS-level and runtime control.",
                when_to_use="Use EC2 when you need custom AMIs, host-level tuning, long-running processes, GPUs, specialized networking, or software that does not fit neatly into serverless or container abstractions.",
                deep_dive="EC2 is the foundational AWS compute primitive. You choose the instance family, CPU architecture, storage, networking, IAM role, and scaling strategy. That freedom makes EC2 fit almost any workload, but it also means patching, capacity planning, autoscaling, hardening, and image lifecycle management become your responsibility unless you wrap EC2 with more managed services.",
                variations=[
                    "Instance families: general purpose, compute optimized, memory optimized, storage optimized, accelerated computing.",
                    "Pricing models: On-Demand, Savings Plans, Reserved Instances, Spot Instances, Dedicated Hosts.",
                    "Operational patterns: single instance, Auto Scaling groups, launch templates, golden AMIs, immutable fleets.",
                ],
                use_cases=[
                    "Legacy applications that need direct OS access.",
                    "Game servers, custom proxies, self-managed databases, Jenkins agents, GPU workloads.",
                    "Lift-and-shift migration where refactoring is not yet possible.",
                ],
                properties=[
                    "You control the operating system, packages, daemon lifecycle, and filesystem layout.",
                    "Tight integration with EBS, VPC, IAM roles, load balancers, and Auto Scaling.",
                    "Supports x86 and Graviton-based ARM instances for price/performance tuning.",
                ],
                advantages=[
                    "Maximum flexibility and broad workload compatibility.",
                    "Mature ecosystem for autoscaling, observability, and image management.",
                    "Strong fit for software that assumes a persistent server model.",
                ],
                disadvantages=[
                    "Highest operational burden among the compute options in this book.",
                    "You own patching, scaling policy quality, and host hardening.",
                    "Idle cost can be high if the fleet is oversized.",
                ],
                implementation_notes=[
                    "Use launch templates and Auto Scaling groups instead of manually created pets.",
                    "Separate application configuration from AMI creation so deployments stay repeatable.",
                    "Choose Spot only for interruption-tolerant workers.",
                ],
                comparison=[
                    ("EC2 vs Lambda", "Choose EC2 when the workload needs long execution time, custom runtimes, or stateful local processes."),
                    ("EC2 vs ECS/EKS", "Choose EC2 directly when container orchestration adds more complexity than value."),
                ],
                code_title="Example: launch an instance with AWS CLI",
                code="""aws ec2 run-instances \
  --image-id ami-0123456789abcdef0 \
  --instance-type t3.medium \
  --subnet-id subnet-12345678 \
  --security-group-ids sg-12345678 \
  --iam-instance-profile Name=app-ec2-role \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=orders-api}]'""",
            ),
            svc(
                name="AWS Lambda",
                tagline="Event-driven serverless functions billed by execution time and resources consumed.",
                when_to_use="Use Lambda when the workload is event-driven, bursty, integration-heavy, and small enough to fit within Lambda runtime limits.",
                deep_dive="Lambda removes server management and lets you package code as functions invoked by events from API Gateway, S3, EventBridge, SQS, DynamoDB streams, and many other sources. It scales quickly for parallel work, but you still need to design around cold starts, stateless execution, timeout limits, package size, and downstream throttling. In production, the service shines when the function is one small step in a larger asynchronous system rather than the entire architecture by itself.",
                variations=[
                    "Packaging models: zip deployment packages and container image functions.",
                    "Invocation styles: synchronous request/response, asynchronous events, stream processing, poll-based queue consumption.",
                    "Execution controls: reserved concurrency, provisioned concurrency, aliases, and weighted traffic shifting.",
                ],
                use_cases=[
                    "Image processing, webhooks, lightweight APIs, ETL triggers, scheduled jobs, and event enrichment.",
                    "Backend tasks that scale sharply and would waste money on always-on servers.",
                    "Glue code between AWS services.",
                ],
                properties=[
                    "Stateless execution environment with ephemeral local storage.",
                    "Native integrations with logs, traces, IAM roles, and event sources.",
                    "Concurrency-based scaling with service-level and downstream limits to manage carefully.",
                ],
                advantages=[
                    "No server provisioning or patching.",
                    "Pay-per-use model is excellent for spiky or low-duty-cycle workloads.",
                    "Fast delivery loop for event-driven systems.",
                ],
                disadvantages=[
                    "Not ideal for very long-running, stateful, or latency-sensitive startup paths.",
                    "Cold starts and concurrency spikes can surprise downstream systems.",
                    "Debugging complex event pipelines can be harder than debugging a monolith.",
                ],
                implementation_notes=[
                    "Keep functions narrow and push shared logic into libraries or layers sparingly.",
                    "Use idempotency for asynchronous events because retries are normal, not exceptional.",
                    "Watch concurrency against databases and third-party APIs.",
                ],
                comparison=[
                    ("Lambda vs ECS Fargate", "Choose Lambda for short, event-based units of work; choose containers for long-running services or full control over the runtime."),
                    ("Lambda vs Beanstalk", "Choose Lambda when scale-to-zero and event triggers matter more than a traditional app server model."),
                ],
                code_title="Example: Python Lambda handler",
                code="""import json

def handler(event, context):
    order_id = event["pathParameters"]["orderId"]
    response = {
        "orderId": order_id,
        "status": "received",
        "requestId": context.aws_request_id,
    }
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response),
    }""",
            ),
            svc(
                name="Amazon ECS",
                tagline="Managed container orchestration designed for AWS-native operations.",
                when_to_use="Use ECS when you want containers without taking on full Kubernetes operational complexity.",
                deep_dive="ECS schedules containers using task definitions, services, clusters, capacity providers, and integrations with ALB, IAM, Secrets Manager, and CloudWatch. It can run on EC2 for more control or Fargate for serverless containers. ECS is often the fastest path to production containers on AWS because the mental model is smaller than Kubernetes and the AWS integration is first-class.",
                variations=[
                    "Launch types: EC2-backed ECS and AWS Fargate.",
                    "Workload types: long-running services, scheduled tasks, and one-off batch-style tasks.",
                    "Capacity strategies: On-Demand, Spot, mixed capacity providers.",
                ],
                use_cases=[
                    "Web APIs and worker services packaged as containers.",
                    "Microservices that need ALB integration and simple autoscaling.",
                    "Teams standardizing on Docker but not on Kubernetes.",
                ],
                properties=[
                    "Task definitions declare containers, CPU, memory, networking, secrets, and logging.",
                    "Service scheduler maintains desired task count and integrates with health checks.",
                    "Deep AWS integrations reduce glue code for deployments and runtime access.",
                ],
                advantages=[
                    "Simpler operational model than EKS for many teams.",
                    "Works well with both EC2 and Fargate cost models.",
                    "Strong security posture through IAM roles for tasks and VPC networking.",
                ],
                disadvantages=[
                    "Less portable than Kubernetes if multi-cloud portability is a strict requirement.",
                    "Advanced service mesh and ecosystem choices are narrower than in Kubernetes land.",
                    "Cost can rise on Fargate for steady large workloads.",
                ],
                implementation_notes=[
                    "Use one task definition family per deployable unit.",
                    "Send container logs to CloudWatch and keep health checks lightweight.",
                    "Use task roles instead of baking credentials into images.",
                ],
                comparison=[
                    ("ECS vs EKS", "Choose ECS for lower operational overhead and tighter AWS integration."),
                    ("ECS vs Beanstalk", "Choose ECS when you need explicit container control and multi-container task design."),
                ],
                code_title="Example: ECS task definition excerpt",
                code="""{
  "family": "orders-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "orders-api",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/orders-api:1.0.0",
      "portMappings": [{"containerPort": 8080}],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/orders-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "app"
        }
      }
    }
  ]
}""",
            ),
            svc(
                name="Amazon EKS",
                tagline="Managed Kubernetes control plane for teams standardized on Kubernetes APIs and ecosystem patterns.",
                when_to_use="Use EKS when Kubernetes portability, CRDs, Helm, GitOps tooling, and the broader K8s ecosystem are strategic requirements.",
                deep_dive="EKS manages the Kubernetes control plane while you decide how worker capacity is provided: self-managed nodes, managed node groups, or Fargate profiles for some pods. EKS is powerful because it fits the industry-standard Kubernetes operating model, but that same flexibility introduces operational surface area in networking, ingress, add-ons, security policy, upgrades, and cost visibility. It is the best fit when your team already thinks in terms of clusters, deployments, services, controllers, and platform engineering.",
                variations=[
                    "Worker models: managed node groups, self-managed EC2 nodes, and selective Fargate execution.",
                    "Platform extensions: Ingress controllers, service mesh, Karpenter, GitOps operators, custom resources.",
                    "Security patterns: IAM Roles for Service Accounts and pod-level policy controls.",
                ],
                use_cases=[
                    "Platform teams running many containerized services.",
                    "Organizations with existing Kubernetes skills or cross-environment portability goals.",
                    "Workloads that benefit from the Kubernetes ecosystem rather than a single AWS-only control plane.",
                ],
                properties=[
                    "Managed control plane but not a fully managed application platform.",
                    "Works well with ECR, ALB, NLB, CloudWatch, and IAM integrations.",
                    "Supports declarative deployment and advanced scheduling extensions.",
                ],
                advantages=[
                    "Excellent ecosystem, portability, and extensibility.",
                    "Strong fit for organizations with platform engineering maturity.",
                    "Allows both opinionated and highly customized runtime patterns.",
                ],
                disadvantages=[
                    "Steeper learning curve and higher platform complexity than ECS.",
                    "Cluster add-ons, upgrades, and networking choices require discipline.",
                    "Easy to over-engineer for small teams or simple services.",
                ],
                implementation_notes=[
                    "Keep cluster add-ons and versions on an explicit upgrade calendar.",
                    "Standardize ingress, observability, and secrets patterns early.",
                    "Avoid building a platform before you have enough services to justify it.",
                ],
                comparison=[
                    ("EKS vs ECS", "Choose EKS when Kubernetes expertise and ecosystem leverage are more valuable than simplicity."),
                    ("EKS vs EC2", "Choose EKS when container orchestration and multi-service scheduling matter more than host-level simplicity."),
                ],
                code_title="Example: Kubernetes Deployment for EKS",
                code="""apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orders-api
  template:
    metadata:
      labels:
        app: orders-api
    spec:
      containers:
        - name: orders-api
          image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/orders-api:1.0.0
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "500m"
              memory: "1Gi"
""",
            ),
            svc(
                name="AWS Elastic Beanstalk",
                tagline="Managed application platform that deploys common web stacks on top of EC2 and related AWS services.",
                when_to_use="Use Beanstalk when you want a faster path for traditional web applications without managing every infrastructure detail yourself.",
                deep_dive="Elastic Beanstalk packages infrastructure patterns for common platforms such as Java, Node.js, Python, .NET, PHP, and Docker. It creates and manages the EC2 instances, load balancers, autoscaling groups, and deployment workflows underneath. The tradeoff is that Beanstalk is opinionated: if your application fits those opinions, it is productive; if your runtime or deployment requirements drift too far, ECS or direct IaC usually becomes cleaner.",
                variations=[
                    "Environment types: single instance and load-balanced autoscaling.",
                    "Deployment policies: all at once, rolling, rolling with additional batch, immutable, blue/green style swaps.",
                    "Platform branches: language-specific stacks and Docker-based stacks.",
                ],
                use_cases=[
                    "Traditional web apps that need quick hosting on AWS.",
                    "Teams migrating from VM/PaaS models without adopting containers yet.",
                    "Internal applications where platform simplicity matters more than deep customization.",
                ],
                properties=[
                    "Abstracts autoscaling, ELB, EC2 provisioning, and rolling deployments.",
                    "Supports application versioning and environment configuration updates.",
                    "Still runs on core AWS primitives that can be inspected and tuned.",
                ],
                advantages=[
                    "Very fast time-to-first-deploy for common app stacks.",
                    "Less platform work than raw EC2.",
                    "Good bridge from traditional hosting to AWS-native operations.",
                ],
                disadvantages=[
                    "Less flexible than ECS/EKS or direct Terraform/CloudFormation.",
                    "Platform customization can become awkward beyond standard use.",
                    "Not the best fit for highly decoupled microservice platforms.",
                ],
                implementation_notes=[
                    "Use environment variables and externalized secrets rather than bundling config.",
                    "Pick immutable or blue/green style strategies for safer upgrades.",
                    "Treat Beanstalk as an accelerator, not a permanent excuse to avoid infrastructure discipline.",
                ],
                comparison=[
                    ("Beanstalk vs EC2", "Choose Beanstalk when you want AWS-managed deployment scaffolding over raw server control."),
                    ("Beanstalk vs ECS", "Choose ECS when your app is container-native or multi-service."),
                ],
                code_title="Example: Beanstalk deployment manifest",
                code="""option_settings:
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 6
  aws:elasticbeanstalk:application:environment:
    SPRING_PROFILES_ACTIVE: prod
    LOG_LEVEL: INFO
  aws:elasticbeanstalk:healthreporting:system:
    SystemType: enhanced""",
            ),
            svc(
                name="AWS Batch",
                tagline="Managed batch scheduler for queue-driven, large-scale, non-interactive jobs.",
                when_to_use="Use Batch when work is naturally job-based, retryable, and not tied to an always-on request/response service.",
                deep_dive="Batch lets you submit jobs to queues and execute them on managed compute environments backed by EC2, Spot, or Fargate. The service handles queueing, dependency graphs, retries, and resource-aware scheduling. It is particularly effective for ETL, simulations, rendering, ML preprocessing, and large fleets of offline tasks where throughput matters more than instant interactive latency.",
                variations=[
                    "Compute environments: EC2 On-Demand, EC2 Spot, Fargate, and managed/unmanaged configurations.",
                    "Job patterns: array jobs, dependent jobs, scheduled submissions, and multi-node parallel jobs.",
                    "Image-based execution with ECR-hosted containers.",
                ],
                use_cases=[
                    "Nightly data processing and report generation.",
                    "Large parameter sweeps, Monte Carlo simulations, media transcoding, and genomics pipelines.",
                    "Queue-based workloads with uneven volume.",
                ],
                properties=[
                    "Queue + scheduler + compute environment abstraction.",
                    "Strong fit for containerized offline workloads.",
                    "Can prioritize cost efficiency with Spot capacity where interruption is acceptable.",
                ],
                advantages=[
                    "Excellent throughput for non-interactive processing.",
                    "Less bespoke scheduler code to maintain.",
                    "Scales batch fleets more intelligently than hand-rolled cron-on-EC2 patterns.",
                ],
                disadvantages=[
                    "Not intended for low-latency online serving.",
                    "Job startup time can be higher than always-warm workers.",
                    "Queue design and retry semantics still require careful thought.",
                ],
                implementation_notes=[
                    "Design jobs to be idempotent and resumable where possible.",
                    "Separate queue priorities for urgent versus cheap background work.",
                    "Use Spot for stateless retry-safe processing to cut cost.",
                ],
                comparison=[
                    ("Batch vs Lambda", "Choose Batch for long-running, resource-heavy, or high-volume job scheduling."),
                    ("Batch vs ECS services", "Choose ECS services for always-on applications; choose Batch for queued work items."),
                ],
                code_title="Example: submit a Batch job",
                code="""aws batch submit-job \
  --job-name nightly-etl \
  --job-queue analytics-priority \
  --job-definition etl-job:3 \
  --container-overrides '{"environment":[{"name":"RUN_DATE","value":"2026-04-25"}]}'""",
            ),
            svc(
                name="Amazon Lightsail",
                tagline="Simplified VPS-style hosting with predictable bundles for small projects and straightforward applications.",
                when_to_use="Use Lightsail for low-complexity websites, demos, small business apps, or learning environments where speed and simplicity matter more than deep AWS flexibility.",
                deep_dive="Lightsail packages compute, storage, snapshots, networking, DNS, databases, and load balancing into simpler constructs with fixed monthly pricing. It intentionally hides much of AWS's deeper infrastructure detail. That makes it easier to get started, but eventually some teams outgrow Lightsail and migrate to EC2, RDS, ECS, or full VPC-native architectures for scale, compliance, or fine-grained control.",
                variations=[
                    "Compute bundles with fixed CPU, memory, and transfer allowances.",
                    "Managed databases for MySQL and PostgreSQL.",
                    "Lightsail load balancers, object storage, snapshots, and static IPs.",
                ],
                use_cases=[
                    "WordPress, brochure sites, lightweight APIs, prototypes, and class projects.",
                    "Small internal tools with modest traffic.",
                    "Teams that want an easier entry point than assembling raw AWS services.",
                ],
                properties=[
                    "Flat bundled pricing simplifies budgeting.",
                    "Smaller operational surface than raw EC2 + VPC + ELB + Route 53 combinations.",
                    "Migration path exists to broader AWS services later.",
                ],
                advantages=[
                    "Very approachable for individuals and small teams.",
                    "Fast setup with little AWS experience required.",
                    "Predictable billing for modest workloads.",
                ],
                disadvantages=[
                    "Less flexible and less feature-rich than core AWS building blocks.",
                    "Not ideal for complex networking or large-scale systems.",
                    "You may need to migrate off it as requirements mature.",
                ],
                implementation_notes=[
                    "Use Lightsail when simplicity is truly the top requirement.",
                    "Do not force enterprise-style architectures into Lightsail.",
                    "Plan the migration path if the product is expected to scale significantly.",
                ],
                comparison=[
                    ("Lightsail vs EC2", "Choose Lightsail for simplicity and fixed-cost bundles; choose EC2 for control and scale."),
                    ("Lightsail vs Beanstalk", "Choose Beanstalk when you need managed app deployment on richer AWS primitives."),
                ],
                code_title="Example: create a Lightsail instance",
                code="""aws lightsail create-instances \
  --instance-names blog-app-1 \
  --availability-zone us-east-1a \
  --blueprint-id amazon_linux_2 \
  --bundle-id medium_2_0""",
            ),
        ],
    ),
    Category(
        name="Storage",
        intro="Storage choices usually come down to access pattern, interface, durability, latency, and cost. AWS separates object, block, file, archive, and hybrid gateway patterns so you can optimize for how applications actually read and write data instead of forcing every workload into one storage model.",
        services=[
            svc(
                name="Amazon S3",
                tagline="Highly durable object storage used as the default data lake, artifact store, backup target, and static content origin on AWS.",
                when_to_use="Use S3 for object data accessed via APIs rather than mounted block devices or shared POSIX filesystems.",
                deep_dive="S3 stores objects in buckets and scales nearly without practical infrastructure limits for most teams. It underpins backups, data lakes, logs, analytics, static website assets, ML datasets, and cross-service integrations. The service is more than a bucket now: lifecycle policies, replication, object lock, inventory, event notifications, access points, and storage-class transitions make S3 an operational platform in its own right.",
                variations=[
                    "Storage classes: Standard, Intelligent-Tiering, Standard-IA, One Zone-IA, Glacier Instant Retrieval, Glacier Flexible Retrieval, Glacier Deep Archive.",
                    "Protection features: versioning, object lock, replication, lifecycle rules, encryption.",
                    "Access models: bucket policies, access points, presigned URLs, static site and CloudFront origins.",
                ],
                use_cases=[
                    "Data lakes, backups, CI artifacts, logs, media files, and static web assets.",
                    "Landing zone for Athena, Glue, EMR, and Redshift integrations.",
                    "Durable archive and cross-account data exchange.",
                ],
                properties=[
                    "Object-based, not block or POSIX file storage.",
                    "Strong durability, broad integration, and global ecosystem support.",
                    "Access control can be bucket-level, prefix-level, or object-level depending on design.",
                ],
                advantages=[
                    "Excellent durability, scalability, and ecosystem support.",
                    "Wide pricing and lifecycle options for hot-to-cold data.",
                    "Often the simplest durable store for unstructured data.",
                ],
                disadvantages=[
                    "Not ideal for low-latency in-place updates like a local filesystem.",
                    "Small-object and request patterns can create surprising costs.",
                    "Permission design can become messy without naming and access conventions.",
                ],
                implementation_notes=[
                    "Design bucket and prefix naming around lifecycle, ownership, and security boundaries.",
                    "Use lifecycle policies aggressively so hot data does not stay expensive forever.",
                    "Prefer CloudFront in front of public or semi-public content delivery.",
                ],
                comparison=[
                    ("S3 vs EBS", "Choose S3 for object storage and analytics integration, not attached disk volumes."),
                    ("S3 vs EFS", "Choose S3 when applications can work through object APIs instead of shared file semantics."),
                ],
                code_title="Example: create a bucket and enable versioning",
                code="""aws s3api create-bucket \
  --bucket acme-reference-data \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket acme-reference-data \
  --versioning-configuration Status=Enabled""",
            ),
            svc(
                name="Amazon EBS",
                tagline="Persistent block storage attached to EC2 instances for databases, boot volumes, and low-latency application storage.",
                when_to_use="Use EBS when an EC2 instance needs a durable disk volume with predictable performance.",
                deep_dive="EBS volumes behave like network-attached block devices and are the most common persistent storage for EC2. You choose volume type based on IOPS, throughput, latency profile, and price. EBS snapshots turn volumes into durable backups and migration artifacts. It is a strong fit for instance-root disks, transactional databases, and custom applications that expect block-level storage rather than object APIs.",
                variations=[
                    "Volume types: gp3, io2, st1, sc1, and specialized variants depending on workload.",
                    "Operational features: snapshots, encryption, multi-attach for some types, resize operations.",
                    "Architectural role: boot volume, data volume, or restored cloned environment.",
                ],
                use_cases=[
                    "EC2 root disks, self-managed databases, queues, and low-latency local application data.",
                    "Persistent storage for single-instance or clustered systems with block semantics.",
                    "Snapshot-based backup and restore patterns.",
                ],
                properties=[
                    "Block-level storage mapped to EC2 instances in an Availability Zone.",
                    "Performance can be provisioned independently from size in modern volume types like gp3.",
                    "Snapshots integrate naturally with backup and disaster recovery workflows.",
                ],
                advantages=[
                    "Strong fit for transactional workloads on EC2.",
                    "More predictable block-storage behavior than object stores for traditional applications.",
                    "Snapshots simplify cloning and recovery.",
                ],
                disadvantages=[
                    "Tied to AZ-level placement and EC2-centric architectures.",
                    "You still manage the filesystem and backup discipline.",
                    "Not a shared multi-writer POSIX filesystem for general use.",
                ],
                implementation_notes=[
                    "Use gp3 by default unless you specifically need io2 or cold HDD patterns.",
                    "Separate root and data volumes for cleaner lifecycle management.",
                    "Automate snapshots and test restore, not just backup creation.",
                ],
                comparison=[
                    ("EBS vs EFS", "Choose EBS for a single attached host or tightly controlled block use; choose EFS for shared file access."),
                    ("EBS vs S3", "Choose EBS for mounted volumes, not durable object repositories."),
                ],
                code_title="Example: create a gp3 EBS volume",
                code="""aws ec2 create-volume \
  --availability-zone us-east-1a \
  --size 200 \
  --volume-type gp3 \
  --iops 6000 \
  --throughput 250 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=orders-db-data}]'""",
            ),
            svc(
                name="Amazon EFS",
                tagline="Elastic shared file storage for Linux workloads that need NFS semantics across multiple instances or containers.",
                when_to_use="Use EFS when multiple compute nodes need to read and write the same filesystem concurrently.",
                deep_dive="EFS provides a managed NFS filesystem that scales automatically and is commonly mounted by EC2, ECS, and EKS workloads. It removes capacity planning friction for shared file data but trades away some of the performance determinism of tightly tuned block storage. It is most useful when application design truly needs a shared filesystem or when replatforming an NFS-oriented application into AWS.",
                variations=[
                    "Performance modes and throughput modes for general purpose versus higher-scale patterns.",
                    "Storage classes for standard and infrequent access data with lifecycle transitions.",
                    "Mount targets across Availability Zones for resilient access.",
                ],
                use_cases=[
                    "Content management systems, shared uploads, home directories, and ML shared datasets.",
                    "Kubernetes or ECS workloads needing shared file persistence.",
                    "Legacy NFS-dependent applications.",
                ],
                properties=[
                    "Managed shared POSIX-style file access over NFS.",
                    "Scales capacity automatically; performance depends on workload profile and chosen mode.",
                    "Integrates with security groups, IAM authorization options, and lifecycle policies.",
                ],
                advantages=[
                    "Simplifies shared storage for Linux fleets.",
                    "No filesystem cluster to build and maintain yourself.",
                    "Works across many instances and container tasks.",
                ],
                disadvantages=[
                    "Usually more expensive than carefully tuned alternatives for some patterns.",
                    "Not ideal for every latency-sensitive transactional database workload.",
                    "Shared filesystems can become accidental coupling points between services.",
                ],
                implementation_notes=[
                    "Use EFS only when shared-file semantics are genuinely required.",
                    "Watch small-file and metadata-heavy workloads closely.",
                    "Keep directory ownership and POSIX permission schemes intentional.",
                ],
                comparison=[
                    ("EFS vs FSx", "Choose EFS for elastic managed NFS on Linux; choose FSx for filesystem-specific performance or protocol needs."),
                    ("EFS vs S3", "Choose EFS when applications need mounted filesystem access rather than object APIs."),
                ],
                code_title="Example: create an EFS filesystem",
                code="""aws efs create-file-system \
  --creation-token shared-content-efs \
  --performance-mode generalPurpose \
  --encrypted""",
            ),
            svc(
                name="Amazon FSx",
                tagline="Managed file systems for specialized protocols and high-performance workloads.",
                when_to_use="Use FSx when the workload needs a specific filesystem family rather than generic NFS.",
                deep_dive="FSx is a family, not a single behavior. FSx for Windows File Server fits SMB and Active Directory-centric workloads. FSx for Lustre fits HPC and high-throughput analytics. FSx for NetApp ONTAP and OpenZFS fit enterprise file and migration scenarios that depend on snapshots, replication, and familiar administrative models. Think of FSx as the answer when 'shared file storage' is too generic and the protocol, performance model, or migration target matters.",
                variations=[
                    "FSx for Windows File Server for SMB and Windows apps.",
                    "FSx for Lustre for HPC, analytics, and S3-linked high-throughput files.",
                    "FSx for NetApp ONTAP and FSx for OpenZFS for advanced enterprise file capabilities.",
                ],
                use_cases=[
                    "Windows line-of-business apps, VDI profiles, media processing, genomics, and lift-and-shift file services.",
                    "HPC workloads that need very high throughput and parallel access.",
                    "Enterprise file migration where protocol compatibility matters.",
                ],
                properties=[
                    "Protocol and filesystem behavior vary by FSx flavor.",
                    "Supports advanced features such as snapshots, backups, replication, and directory integration depending on the family.",
                    "Often the best path when application compatibility outweighs architectural purity.",
                ],
                advantages=[
                    "Lets you choose the right filesystem instead of overloading EFS or S3.",
                    "Great for migration and specialized performance profiles.",
                    "Managed operations reduce the burden of running these filesystems yourself.",
                ],
                disadvantages=[
                    "Requires the team to understand which FSx family matches the workload.",
                    "Can be overkill for simpler shared storage needs.",
                    "Costs and operational options vary substantially by family.",
                ],
                implementation_notes=[
                    "Choose the FSx family based on protocol first, performance second.",
                    "Use FSx for Lustre with S3-linked data sets when high-throughput analytics matters.",
                    "Validate AD and network dependencies early for Windows-oriented deployments.",
                ],
                comparison=[
                    ("FSx vs EFS", "Choose FSx when protocol specificity or enterprise filesystem behavior matters."),
                    ("FSx for Lustre vs EBS", "Choose Lustre when the workload is distributed and throughput-hungry, not single-instance block storage."),
                ],
                code_title="Example: create FSx for Windows",
                code="""aws fsx create-file-system \
  --file-system-type WINDOWS \
  --storage-capacity 300 \
  --subnet-ids subnet-12345678 \
  --windows-configuration ThroughputCapacity=32""",
            ),
            svc(
                name="Amazon S3 Glacier",
                tagline="Cold and archival object storage optimized for lower cost and slower retrieval workflows.",
                when_to_use="Use Glacier classes when data is rarely accessed but must remain durable and recoverable.",
                deep_dive="S3 Glacier is best understood as a set of cold storage classes and retrieval patterns rather than a separate bucket architecture. Glacier Instant Retrieval is for infrequently accessed but still quickly retrievable data. Glacier Flexible Retrieval and Deep Archive drive the lowest storage cost for backup, retention, and regulatory archives where restore time can be minutes to hours. The key design question is not 'can I store data there?' but 'how fast do I need it back, and how predictable is that need?'",
                variations=[
                    "Glacier Instant Retrieval for infrequent but near-immediate access.",
                    "Glacier Flexible Retrieval for archive data with retrieval workflows.",
                    "Glacier Deep Archive for the lowest-cost long-term retention.",
                ],
                use_cases=[
                    "Compliance archives, backup retention, financial records, log archives, and media preservation.",
                    "Disaster recovery data that should not sit in hot storage forever.",
                    "Cold tiers behind lifecycle policies from S3 Standard or IA classes.",
                ],
                properties=[
                    "Durable object storage with retrieval time and cost tradeoffs.",
                    "Usually consumed through S3 lifecycle and restore workflows.",
                    "Best paired with explicit retention and retrieval planning.",
                ],
                advantages=[
                    "Excellent cost profile for long-term retention.",
                    "Integrates naturally with S3 lifecycle and object management.",
                    "Strong fit for governance-heavy data sets.",
                ],
                disadvantages=[
                    "Retrieval is not instant in all tiers.",
                    "Poor fit for unpredictable frequent access.",
                    "Teams sometimes move data cold without rehearsing restore procedures.",
                ],
                implementation_notes=[
                    "Use lifecycle rules so archive movement is automatic rather than manual.",
                    "Document retrieval expectations with the business before choosing a tier.",
                    "Test restore times and costs on realistic sample data.",
                ],
                comparison=[
                    ("Glacier vs S3 Standard-IA", "Choose Glacier when retrieval speed matters less than long-term cost reduction."),
                    ("Glacier Deep Archive vs backup software vaults", "Choose based on restore workflow integration and compliance retention needs."),
                ],
                code_title="Example: lifecycle rule to archive old objects",
                code="""{
  "Rules": [
    {
      "ID": "archive-logs",
      "Status": "Enabled",
      "Filter": {"Prefix": "logs/"},
      "Transitions": [
        {"Days": 30, "StorageClass": "GLACIER_IR"},
        {"Days": 180, "StorageClass": "DEEP_ARCHIVE"}
      ]
    }
  ]
}""",
            ),
            svc(
                name="AWS Storage Gateway",
                tagline="Hybrid bridge that exposes AWS storage through familiar on-premises file, volume, or tape interfaces.",
                when_to_use="Use Storage Gateway when on-premises applications need AWS-backed storage without being rewritten immediately.",
                deep_dive="Storage Gateway is designed for hybrid reality. Many enterprises still run software that speaks NFS, SMB, iSCSI, or virtual tape protocols and cannot be reworked overnight. Storage Gateway lets those systems continue using familiar interfaces while the durable backend lives in AWS. It is especially useful for backup modernization, edge caching, data movement, and phased migration away from local infrastructure.",
                variations=[
                    "File Gateway for NFS/SMB access to S3-backed data.",
                    "Volume Gateway for block-style volumes with cached or stored approaches.",
                    "Tape Gateway for backup applications that expect virtual tapes.",
                ],
                use_cases=[
                    "Backup modernization, archive migration, hybrid file sharing, and disaster recovery.",
                    "Replacing physical tape workflows with cloud-backed virtual tape libraries.",
                    "Incremental migration from on-prem storage systems to AWS.",
                ],
                properties=[
                    "Exposes familiar storage protocols while caching hot data locally.",
                    "Optimizes transfer and resilience between on-prem and AWS.",
                    "Hybrid-first service rather than cloud-native application storage.",
                ],
                advantages=[
                    "Pragmatic migration tool for enterprises with legacy storage dependencies.",
                    "Reduces the need for immediate application rewrites.",
                    "Strong fit for backup and archive workflows.",
                ],
                disadvantages=[
                    "Adds another component to operate in hybrid environments.",
                    "Not a substitute for redesigning unsuitable storage architectures forever.",
                    "Network planning and cache sizing still matter.",
                ],
                implementation_notes=[
                    "Treat it as a bridge in a broader migration strategy, not just permanent storage debt.",
                    "Place the gateway close to workloads that need low-latency cached access.",
                    "Validate backup vendor integration before committing large archive moves.",
                ],
                comparison=[
                    ("Storage Gateway vs DataSync", "Choose Storage Gateway for ongoing hybrid access; choose DataSync for explicit transfer jobs."),
                    ("Storage Gateway vs direct S3", "Choose Storage Gateway when applications cannot natively use S3 APIs."),
                ],
                code_title="Example: conceptual File Gateway flow",
                code="""On-prem application -> SMB/NFS share -> Storage Gateway cache
Storage Gateway -> optimized transfer -> Amazon S3 bucket
Lifecycle policy -> Glacier tiers for archive retention""",
            ),
        ],
    ),
    Category(
        name="Databases",
        intro="Database selection should start with the data model and access pattern, not with brand preference. AWS gives you relational, key-value, document, in-memory, graph, and warehouse options. The biggest architecture wins come from matching the service to the workload instead of forcing one engine to do everything.",
        services=[
            svc(
                name="Amazon RDS",
                tagline="Managed relational databases for standard OLTP workloads using familiar engines.",
                when_to_use="Use RDS when the workload is relational, transactional, and fits mainstream engines such as PostgreSQL, MySQL, MariaDB, SQL Server, or Oracle.",
                deep_dive="RDS reduces undifferentiated relational database administration by automating backups, patching, Multi-AZ options, monitoring, and routine operations. It is the default answer for many business applications because SQL, ACID transactions, and mature ecosystem tooling remain valuable. The main architecture question is not whether RDS works, but whether you need standard RDS engines, the Aurora architecture, or a non-relational model entirely.",
                variations=[
                    "Engines: PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, and specialized options depending on region.",
                    "Deployment patterns: single-AZ, Multi-AZ, read replicas, and backup/restore strategies.",
                    "Operational options: provisioned instances, storage tuning, performance insights, and managed backups.",
                ],
                use_cases=[
                    "ERP, CRM, order management, billing, and conventional transactional systems.",
                    "Apps with relational joins, constraints, and established SQL tooling.",
                    "Migrations from self-managed relational databases.",
                ],
                properties=[
                    "Managed but still requires schema design, indexing, and query discipline.",
                    "Strong compatibility with existing relational application stacks.",
                    "Integrates with monitoring, IAM auth options, and backup workflows.",
                ],
                advantages=[
                    "Familiar operational model for most engineering teams.",
                    "Less database toil than self-managed EC2 databases.",
                    "Flexible engine choices for different licensing and compatibility needs.",
                ],
                disadvantages=[
                    "Vertical scaling and tuning may still become bottlenecks for extreme scale.",
                    "Can be overused for workloads better served by key-value or event-driven storage.",
                    "License-heavy engines can be costly.",
                ],
                implementation_notes=[
                    "Prefer PostgreSQL or MySQL family unless a commercial engine is truly required.",
                    "Use read replicas for read scaling, not as a substitute for poor query design.",
                    "Design backups and failover drills as first-class operational practices.",
                ],
                comparison=[
                    ("RDS vs Aurora", "Choose Aurora when you need the Aurora architecture's scale, failover, or performance profile."),
                    ("RDS vs DynamoDB", "Choose RDS when relational modeling and SQL transactions are central."),
                ],
                code_title="Example: create a PostgreSQL RDS instance",
                code="""aws rds create-db-instance \
  --db-instance-identifier orders-postgres \
  --engine postgres \
  --db-instance-class db.t4g.medium \
  --allocated-storage 100 \
  --master-username adminuser \
  --manage-master-user-password \
  --backup-retention-period 7""",
            ),
            svc(
                name="Amazon Aurora",
                tagline="AWS-built relational engine compatible with MySQL and PostgreSQL, designed for higher performance and availability at scale.",
                when_to_use="Use Aurora when you want managed relational semantics but need better scale-out, failover behavior, or price/performance than a standard RDS engine can comfortably provide.",
                deep_dive="Aurora separates compute from a distributed storage layer and adds fast replication, many reader endpoints, and operational options such as Serverless v2 and Global Database. It stays familiar to application teams because it speaks MySQL or PostgreSQL-compatible protocols, yet it behaves differently under the hood from self-managed versions of those engines. It is often the premium relational choice for cloud-native business systems.",
                variations=[
                    "Aurora MySQL-compatible and Aurora PostgreSQL-compatible editions.",
                    "Provisioned clusters, Aurora Serverless v2, Global Database, and reader endpoints.",
                    "Operational choices such as I/O-Optimized storage profile.",
                ],
                use_cases=[
                    "High-throughput SaaS systems, e-commerce backends, payment platforms, and globally distributed read-heavy systems.",
                    "Relational workloads that outgrow standard RDS comfort zones.",
                    "Applications needing multiple low-latency replicas and strong managed failover behavior.",
                ],
                properties=[
                    "Distributed storage architecture with strong replication and availability characteristics.",
                    "Compatible with MySQL or PostgreSQL tools and drivers with caveats.",
                    "Supports advanced cluster patterns beyond a single DB instance model.",
                ],
                advantages=[
                    "Strong scale and availability story for relational workloads.",
                    "Often excellent price/performance versus commercial databases.",
                    "Good bridge between familiar SQL and cloud-native resilience.",
                ],
                disadvantages=[
                    "More feature-rich and sometimes more expensive than standard RDS for simple workloads.",
                    "Aurora-specific behaviors mean it is not just 'MySQL in the cloud'.",
                    "Can encourage oversized relational architectures when another data model fits better.",
                ],
                implementation_notes=[
                    "Use reader endpoints intentionally rather than spraying reads without consistency awareness.",
                    "Benchmark your actual workload before assuming Aurora is always worth the premium.",
                    "Use Global Database only when cross-region relational requirements justify the complexity.",
                ],
                comparison=[
                    ("Aurora vs RDS PostgreSQL/MySQL", "Choose Aurora for higher scale, cluster-oriented operations, and advanced failover."),
                    ("Aurora vs Redshift", "Choose Aurora for OLTP, not warehouse analytics."),
                ],
                code_title="Example: create an Aurora PostgreSQL cluster",
                code="""aws rds create-db-cluster \
  --db-cluster-identifier orders-aurora \
  --engine aurora-postgresql \
  --master-username adminuser \
  --manage-master-user-password""",
            ),
            svc(
                name="Amazon DynamoDB",
                tagline="Serverless key-value and document database built for massive scale and single-digit millisecond access.",
                when_to_use="Use DynamoDB when access patterns are known up front and the system needs predictable low-latency performance at scale without managing database servers.",
                deep_dive="DynamoDB rewards teams that model around query patterns rather than around generalized relational flexibility. Partition keys, sort keys, GSIs, LSIs, item design, and hot-partition avoidance are the heart of success. When the model fits, DynamoDB can absorb extraordinary scale with very low operational overhead. When the model does not fit, teams can spend months fighting access-pattern mismatches that a relational or search system would have handled more naturally.",
                variations=[
                    "Capacity modes: on-demand and provisioned with autoscaling.",
                    "Data access options: tables, GSIs, LSIs, streams, TTL, DAX, global tables.",
                    "Data model support: key-value and document-style items.",
                ],
                use_cases=[
                    "Shopping carts, session stores, profile stores, event metadata, gaming state, IoT state, and high-scale APIs.",
                    "Systems with huge request rates and simple predictable access paths.",
                    "Multi-region active-active patterns using global tables.",
                ],
                properties=[
                    "Schema-light item model but heavily access-pattern-driven design.",
                    "Serverless and highly managed, with integrated streams and scaling.",
                    "Strong fit for event-driven and internet-scale products.",
                ],
                advantages=[
                    "Very high scale with low operational effort.",
                    "Excellent latency and elasticity for well-modeled workloads.",
                    "Powerful ecosystem features such as streams and TTL.",
                ],
                disadvantages=[
                    "Poor fit for ad hoc joins and relational query flexibility.",
                    "Data modeling mistakes are costly to unwind later.",
                    "Costs can grow fast with inefficient access patterns or large scans.",
                ],
                implementation_notes=[
                    "Model from queries backward, not entities forward.",
                    "Design keys to avoid hot partitions and large unbounded item collections.",
                    "Use streams for event integration rather than polling tables.",
                ],
                comparison=[
                    ("DynamoDB vs RDS", "Choose DynamoDB for scale-first key-based access patterns, not relational workloads."),
                    ("DynamoDB vs ElastiCache", "Choose DynamoDB for durable primary data; choose ElastiCache for caching or transient acceleration."),
                ],
                code_title="Example: create a DynamoDB table",
                code="""aws dynamodb create-table \
  --table-name Orders \
  --attribute-definitions \
      AttributeName=PK,AttributeType=S \
      AttributeName=SK,AttributeType=S \
  --key-schema \
      AttributeName=PK,KeyType=HASH \
      AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST""",
            ),
            svc(
                name="Amazon ElastiCache",
                tagline="Managed in-memory caching for Redis and Memcached use cases.",
                when_to_use="Use ElastiCache when you need to reduce database load, accelerate reads, manage sessions, or support high-speed ephemeral data structures.",
                deep_dive="ElastiCache is not usually the system of record. Its value comes from offloading hot reads, session state, counters, leaderboards, pub/sub patterns, and some queue-like or rate-limiting behavior. Redis-backed ElastiCache is feature-rich and can support more than simple caching, while Memcached stays intentionally simpler. The main risk is promoting the cache into an accidental primary database without owning the failure semantics that come with that choice.",
                variations=[
                    "Redis-compatible clusters for richer data structures and replication patterns.",
                    "Memcached for simpler distributed caching.",
                    "Serverless ElastiCache options for simplified capacity management in supported modes.",
                ],
                use_cases=[
                    "Read-through caching, session stores, leaderboard counters, token buckets, and queue-like lightweight patterns.",
                    "Reducing latency for repeatedly requested data.",
                    "Shielding relational or document databases from hot-spot reads.",
                ],
                properties=[
                    "Memory-first design with much lower latency than disk-backed databases.",
                    "Best used as a complement to primary durable storage, not blindly as a replacement.",
                    "Operational semantics differ depending on Redis versus Memcached.",
                ],
                advantages=[
                    "Huge latency and throughput wins for hot data.",
                    "Can dramatically reduce downstream database pressure.",
                    "Managed service reduces the pain of operating cache clusters directly.",
                ],
                disadvantages=[
                    "Cache invalidation and data freshness are application problems, not service problems.",
                    "Using Redis as an all-purpose database without careful design can create durability surprises.",
                    "Memory-heavy workloads can become expensive if poorly scoped.",
                ],
                implementation_notes=[
                    "Be explicit about TTL, eviction policy, and cache fill strategy.",
                    "Treat cache miss storms as a design problem and add request coalescing where needed.",
                    "Choose Redis when you need richer structures; choose Memcached for simpler cache-only patterns.",
                ],
                comparison=[
                    ("ElastiCache vs DynamoDB", "Choose ElastiCache for acceleration and transient data; choose DynamoDB for durable primary storage."),
                    ("ElastiCache vs MemoryDB", "Choose MemoryDB when in-memory data must also be the durable primary store."),
                ],
                code_title="Example: Redis client usage pattern",
                code="""import redis

r = redis.Redis(host="orders-cache.xxxxxx.use1.cache.amazonaws.com", port=6379)
cached = r.get("order:123")
if cached is None:
    # Fetch from database and write back with TTL
    r.setex("order:123", 300, '{"id":"123","status":"PAID"}')""",
            ),
            svc(
                name="Amazon Neptune",
                tagline="Managed graph database for highly connected data and relationship-heavy traversal queries.",
                when_to_use="Use Neptune when the shape of the problem is fundamentally graph-oriented: relationships are first-class, and traversals matter more than simple key lookups.",
                deep_dive="Neptune supports property graph and RDF models with Gremlin and SPARQL query patterns. It is built for recommendation engines, fraud detection, knowledge graphs, network topology, identity linkage, and dependency analysis. Teams should move to Neptune when relationship queries become awkward, slow, or brittle in relational or document stores, not because graph databases sound fashionable.",
                variations=[
                    "Property graph workloads with Gremlin.",
                    "Semantic graph workloads with RDF and SPARQL.",
                    "Operational analytics extensions through Neptune Analytics patterns.",
                ],
                use_cases=[
                    "Fraud rings, social graphs, recommendation systems, asset dependency maps, and knowledge graphs.",
                    "Identity resolution and access relationship analysis.",
                    "Connected-data exploration that would require many joins elsewhere.",
                ],
                properties=[
                    "Optimized for traversing edges and relationships with low latency.",
                    "Graph model changes how teams think about data access and schema evolution.",
                    "Managed backups, replicas, and availability features reduce graph ops burden.",
                ],
                advantages=[
                    "Much better fit than relational joins for deep relationship queries.",
                    "Powerful expressiveness for recommendation and fraud domains.",
                    "Specialized tooling without self-managing graph clusters.",
                ],
                disadvantages=[
                    "Specialized skill set and query languages.",
                    "Can be overkill for data that is not truly graph-shaped.",
                    "Operational success still depends on clear graph modeling discipline.",
                ],
                implementation_notes=[
                    "Validate that graph traversal is the real bottleneck before introducing Neptune.",
                    "Model vertices and edges around business semantics, not database convenience alone.",
                    "Benchmark representative traversals, not only simple node lookups.",
                ],
                comparison=[
                    ("Neptune vs DocumentDB", "Choose Neptune when relationship traversal is the central workload."),
                    ("Neptune vs RDS", "Choose Neptune when repeated multi-hop graph traversals dominate the design."),
                ],
                code_title="Example: Gremlin traversal",
                code="""g.V().has("user", "id", "u-1001")
  .out("purchased")
  .in("purchased")
  .groupCount()
  .order(local)
  .by(values, desc)""",
            ),
            svc(
                name="Amazon DocumentDB",
                tagline="Managed document database with MongoDB compatibility for JSON-style application models.",
                when_to_use="Use DocumentDB when the workload fits a document model and the team wants managed operations with MongoDB-compatible tooling expectations.",
                deep_dive="DocumentDB is designed for JSON-like document workloads such as catalogs, profiles, content systems, and metadata stores. It is important to remember that compatibility does not mean identical behavior to every MongoDB deployment or ecosystem feature. The service is valuable when flexible document schemas help application evolution, but teams should still validate indexing strategy, query behavior, and feature compatibility against their actual workload.",
                variations=[
                    "Cluster-based managed document architecture.",
                    "Compatibility-driven migration target for some MongoDB-style applications.",
                    "Replica and backup patterns for production document workloads.",
                ],
                use_cases=[
                    "Product catalogs, user profile stores, content metadata, and semi-structured application data.",
                    "Applications that benefit from JSON document flexibility.",
                    "Managed alternative to self-run document clusters.",
                ],
                properties=[
                    "Document-oriented storage and query behavior.",
                    "Managed backups, patching, and scaling at the cluster level.",
                    "Good fit when data evolves faster than rigid relational schemas.",
                ],
                advantages=[
                    "Flexible model for semi-structured application data.",
                    "Managed operations reduce document database toil.",
                    "Compatible client tooling lowers migration friction in many cases.",
                ],
                disadvantages=[
                    "Not a drop-in substitute for every MongoDB feature or assumption.",
                    "Can become a dumping ground for poorly modeled data.",
                    "Complex analytics still often belong elsewhere.",
                ],
                implementation_notes=[
                    "Benchmark your exact queries and compatibility requirements before migrating.",
                    "Use disciplined document design rather than treating JSON as schema-free chaos.",
                    "Pair with search or warehouse services when analytical workloads grow.",
                ],
                comparison=[
                    ("DocumentDB vs DynamoDB", "Choose DocumentDB for richer document query flexibility; choose DynamoDB for scale-first key-based access."),
                    ("DocumentDB vs RDS JSON columns", "Choose DocumentDB when the document model is primary, not incidental."),
                ],
                code_title="Example: Mongo-style insert",
                code="""db.products.insertOne({
  sku: "BK-1001",
  title: "AWS Services Handbook",
  tags: ["aws", "cloud", "reference"],
  pricing: { currency: "USD", amount: 49.0 }
})""",
            ),
            svc(
                name="Amazon Redshift",
                tagline="Managed cloud data warehouse for large-scale analytics and BI workloads.",
                when_to_use="Use Redshift when the goal is analytical SQL over large structured or semi-structured data sets, not OLTP transactions.",
                deep_dive="Redshift is a warehouse, not an application database. It is built for aggregation, BI, reporting, and analytical modeling over large data sets. The modern Redshift story includes both provisioned clusters and Redshift Serverless, spectrum-style external access, and tight integration with S3-based data lakes. Teams get the most value when they separate operational transaction storage from analytical warehouse storage instead of asking one database to do both poorly.",
                variations=[
                    "Provisioned clusters for controlled warehouse sizing.",
                    "Redshift Serverless for on-demand analytics capacity.",
                    "Spectrum and lakehouse-style access patterns over S3-backed data.",
                ],
                use_cases=[
                    "Executive reporting, product analytics, finance dashboards, marketing attribution, and large-scale SQL transformations.",
                    "Joining many large tables for analytics workloads.",
                    "BI tooling and dimensional models on cloud data.",
                ],
                properties=[
                    "Columnar analytics engine, not a row-oriented OLTP system.",
                    "Excellent fit for warehouse-style SQL and aggregated query patterns.",
                    "Often sits downstream from transactional stores and event pipelines.",
                ],
                advantages=[
                    "Strong analytical performance at scale.",
                    "Broad SQL and BI tooling compatibility.",
                    "Can unify warehouse and data-lake style patterns effectively.",
                ],
                disadvantages=[
                    "Poor fit for per-request application transactions.",
                    "Warehouse modeling and governance still require real discipline.",
                    "Costs can rise if clusters stay oversized or data layout is unmanaged.",
                ],
                implementation_notes=[
                    "Keep OLTP data off the warehouse path; load it intentionally.",
                    "Use Serverless when workload variability outweighs fixed cluster planning.",
                    "Model data for analytics consumers, not just raw ingestion convenience.",
                ],
                comparison=[
                    ("Redshift vs Athena", "Choose Redshift for repeated warehouse workloads and strong performance over modeled data."),
                    ("Redshift vs RDS", "Choose Redshift for analytics, not transactional app storage."),
                ],
                code_title="Example: create a Redshift Serverless namespace",
                code="""aws redshift-serverless create-namespace \
  --namespace-name analytics-core \
  --admin-username adminuser \
  --manage-admin-password""",
            ),
        ],
    ),
    Category(
        name="Networking",
        intro="Networking services define how systems connect, route traffic, expose APIs, cache content at the edge, and bridge private environments into AWS. In practice, networking decisions also shape security, latency, multi-account architecture, and operational blast radius.",
        services=[
            svc(
                name="Amazon VPC",
                tagline="Logical private network boundary for AWS resources, subnets, routing, and security controls.",
                when_to_use="Use VPC whenever you need network isolation, custom IP ranges, subnet design, and security control over AWS workloads.",
                deep_dive="VPC is the baseline network building block in AWS. It defines address space, subnets, route tables, internet egress patterns, network boundaries, and many of the controls used by compute and data services. Most higher-level architectures eventually reduce to a few VPC questions: what is public, what is private, how does traffic flow, what is shared, and how do we prevent accidental over-connectivity?",
                variations=[
                    "Public and private subnet patterns.",
                    "Single-VPC, shared-services VPC, hub-and-spoke, and multi-account network models.",
                    "Supporting constructs such as security groups, NACLs, NAT gateways, endpoints, and peering/transit options.",
                ],
                use_cases=[
                    "Isolated application environments, multi-tier app networks, regulated workloads, and multi-account landing zones.",
                    "Backend systems that should not be internet-reachable.",
                    "Hybrid extensions into on-premises networks.",
                ],
                properties=[
                    "Defines the network blast radius and trust boundaries for workloads.",
                    "Acts as the backbone for compute, managed databases, and internal services.",
                    "Network design choices affect cost, security, and troubleshooting complexity.",
                ],
                advantages=[
                    "Strong isolation and flexible topology design.",
                    "Deep integration with AWS services and security controls.",
                    "Supports both simple and enterprise-grade network architectures.",
                ],
                disadvantages=[
                    "Easy to overcomplicate with too many peering and exception rules.",
                    "Poor IP planning creates migration pain later.",
                    "NAT, inspection, and cross-AZ traffic can create hidden cost.",
                ],
                implementation_notes=[
                    "Keep CIDR planning future-proof and avoid overlapping address ranges.",
                    "Prefer simple subnet and route designs before building complex hub-spoke patterns.",
                    "Use VPC endpoints for private access to AWS services where justified.",
                ],
                comparison=[
                    ("VPC vs managed public defaults", "Choose custom VPC design when you need control, isolation, and repeatability."),
                    ("VPC peering vs Transit Gateway", "Use peering for small simple links; use Transit Gateway for many-network scale."),
                ],
                code_title="Example: create a VPC",
                code="""aws ec2 create-vpc \
  --cidr-block 10.20.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=platform-prod}]'""",
            ),
            svc(
                name="Amazon Route 53",
                tagline="Managed DNS and routing service for domain registration, health checks, and traffic steering.",
                when_to_use="Use Route 53 when you need authoritative DNS, health-aware routing, or global traffic policies on AWS.",
                deep_dive="Route 53 is more than DNS hosting. It is often the top-level traffic control point for failover, weighted releases, latency-based routing, and health checks. In cloud architecture, DNS decisions affect deployment safety, cross-region failover, and how quickly users are shifted between environments. Route 53 is especially powerful when combined with CloudFront, ELB, S3 static hosting, and regional application stacks.",
                variations=[
                    "Routing policies: simple, weighted, latency-based, failover, geolocation, geoproximity, and multivalue answers.",
                    "Hosted zones for public and private DNS.",
                    "Domain registration, health checks, and resolver integrations.",
                ],
                use_cases=[
                    "Application domain hosting, blue/green cutovers, multi-region routing, and private service discovery.",
                    "Health-based failover between regional stacks.",
                    "Split-horizon or private DNS inside VPC environments.",
                ],
                properties=[
                    "Global DNS layer with programmable routing policy behavior.",
                    "Often used to control deployment traffic gradually or safely.",
                    "Works across public internet and private VPC-bound DNS contexts.",
                ],
                advantages=[
                    "Reliable and flexible traffic steering.",
                    "Useful for both external customer traffic and internal service naming.",
                    "Integrates cleanly with many AWS front-door services.",
                ],
                disadvantages=[
                    "DNS caching means changes are never truly instant everywhere.",
                    "Poor TTL strategy can slow rollbacks or create unnecessary query volume.",
                    "It is easy to build confusing DNS topologies across accounts and environments.",
                ],
                implementation_notes=[
                    "Set TTLs based on expected change frequency and rollback needs.",
                    "Name records so environment ownership is obvious.",
                    "Pair health checks with realistic failure criteria, not only instance liveness.",
                ],
                comparison=[
                    ("Route 53 vs CloudFront", "Choose Route 53 for DNS routing; choose CloudFront for CDN edge delivery."),
                    ("Route 53 failover vs Global Accelerator", "Use DNS failover for many scenarios; use Global Accelerator when static anycast endpoints and network path optimization matter."),
                ],
                code_title="Example: weighted DNS record",
                code="""{
  "Comment": "Blue green rollout",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.example.com",
        "Type": "A",
        "SetIdentifier": "blue",
        "Weight": 90,
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "blue-alb-123.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }
  ]
}""",
            ),
            svc(
                name="Amazon CloudFront",
                tagline="Global content delivery network and edge security/performance layer.",
                when_to_use="Use CloudFront when you need low-latency global delivery, edge caching, origin shielding, or a secure front door for static and dynamic content.",
                deep_dive="CloudFront caches static assets, accelerates dynamic content, and often becomes the public entry point for websites, APIs, media, and downloads. It can sit in front of S3, ALBs, EC2 origins, and API Gateway. CloudFront also becomes a security and resilience layer when paired with WAF, Shield, signed URLs, origin access controls, and edge functions. In many architectures, CloudFront is not optional decoration; it is the performance and security boundary users actually touch.",
                variations=[
                    "Static and dynamic content caching behaviors.",
                    "Security features such as signed URLs/cookies and origin access controls.",
                    "Edge logic with CloudFront Functions and Lambda@Edge patterns.",
                ],
                use_cases=[
                    "Static websites, download distribution, media delivery, API acceleration, and regional origin protection.",
                    "Secure S3 content without exposing buckets directly.",
                    "Global front door for web applications.",
                ],
                properties=[
                    "Edge caching, global POP network, and request policy controls.",
                    "Can reduce origin load and improve perceived latency substantially.",
                    "Supports fine-grained cache key and header/query handling.",
                ],
                advantages=[
                    "Strong global performance improvements.",
                    "Reduces origin exposure and often improves security posture.",
                    "Useful for both static and dynamic workloads.",
                ],
                disadvantages=[
                    "Caching misconfiguration can cause stale or inconsistent behavior.",
                    "Debugging cache keys and edge policies takes discipline.",
                    "Some dynamic use cases see less benefit than teams expect.",
                ],
                implementation_notes=[
                    "Design cache behavior deliberately around headers, cookies, and query strings.",
                    "Keep origins private wherever possible.",
                    "Use versioned asset paths for painless cache invalidation strategy.",
                ],
                comparison=[
                    ("CloudFront vs API Gateway edge-optimized exposure", "Choose CloudFront when you want explicit CDN and edge policy control."),
                    ("CloudFront vs direct ALB exposure", "Choose CloudFront to improve global delivery and reduce origin attack surface."),
                ],
                code_title="Example: CloudFront distribution origin snippet",
                code="""{
  "Origins": {
    "Items": [
      {
        "Id": "static-site-origin",
        "DomainName": "my-site-bucket.s3.amazonaws.com",
        "OriginAccessControlId": "E123ABCXYZ"
      }
    ],
    "Quantity": 1
  }
}""",
            ),
            svc(
                name="Elastic Load Balancing",
                tagline="Managed traffic distribution across compute targets, with layer-7 and layer-4 options.",
                when_to_use="Use ELB when you need highly available traffic distribution, health checks, and a stable entry point for multiple targets.",
                deep_dive="ELB is a family: Application Load Balancer for HTTP/HTTPS and advanced routing, Network Load Balancer for high-performance TCP/UDP and static IP-friendly flows, Gateway Load Balancer for network appliance chains, and the older Classic Load Balancer for legacy cases. Choosing the right balancer affects protocol support, observability, TLS strategy, and deployment style. ALB is the default for modern web apps; NLB is common for performance-sensitive or non-HTTP traffic.",
                variations=[
                    "Application Load Balancer, Network Load Balancer, and Gateway Load Balancer.",
                    "Target types: EC2 instances, IP targets, Lambda in ALB-specific patterns, and container tasks.",
                    "Capabilities such as path routing, host routing, TLS termination, health checks, and stickiness.",
                ],
                use_cases=[
                    "Web apps, APIs, microservices ingress, internal service balancing, and appliance traffic chaining.",
                    "Container service front doors in ECS and EKS.",
                    "Blue/green or canary deployments when combined with weighted rules or DNS.",
                ],
                properties=[
                    "Health-based traffic distribution across multiple targets and AZs.",
                    "Protocol-aware features differ significantly by load balancer type.",
                    "Can be internet-facing or internal-only.",
                ],
                advantages=[
                    "Highly available managed entry point for services.",
                    "Removes the need to run custom reverse proxy fleets for common cases.",
                    "Integrates tightly with autoscaling and container platforms.",
                ],
                disadvantages=[
                    "Wrong load balancer choice causes avoidable complexity later.",
                    "Layer-7 features can tempt teams into application logic at the edge.",
                    "Cross-zone and data-processing costs need attention.",
                ],
                implementation_notes=[
                    "Default to ALB for HTTP applications unless you know you need NLB.",
                    "Keep health checks representative but lightweight.",
                    "Be explicit about idle timeout, header forwarding, and TLS termination boundaries.",
                ],
                comparison=[
                    ("ALB vs NLB", "Choose ALB for HTTP routing intelligence; choose NLB for TCP/UDP performance and static-IP-friendly patterns."),
                    ("ELB vs API Gateway", "Choose ELB for service ingress and balancing; choose API Gateway for API product features and request management."),
                ],
                code_title="Example: create an application load balancer",
                code="""aws elbv2 create-load-balancer \
  --name orders-alb \
  --subnets subnet-11111111 subnet-22222222 \
  --security-groups sg-12345678 \
  --scheme internet-facing \
  --type application""",
            ),
            svc(
                name="Amazon API Gateway",
                tagline="Managed API front door for REST, HTTP, and WebSocket APIs.",
                when_to_use="Use API Gateway when you need API-specific capabilities such as auth, throttling, stage management, usage plans, or Lambda-native integration.",
                deep_dive="API Gateway is not just a router. It is a product layer for APIs, with request validation, authorizers, transformations, throttling, WebSocket support, and stage-aware publishing. It fits serverless and API-first systems especially well. For simple container-backed HTTP routing, an ALB may be cheaper and simpler. For APIs that need developer-facing controls, policy enforcement, and usage management, API Gateway earns its place quickly.",
                variations=[
                    "HTTP APIs for lower-cost modern HTTP use cases.",
                    "REST APIs for richer legacy and management features.",
                    "WebSocket APIs for bidirectional connection patterns.",
                ],
                use_cases=[
                    "Public APIs, partner APIs, internal platform APIs, serverless backends, and WebSocket messaging.",
                    "Request validation and auth enforcement in front of Lambda or HTTP backends.",
                    "API products with stages and environment separation.",
                ],
                properties=[
                    "Fully managed API plane with auth, quotas, and monitoring hooks.",
                    "Supports direct AWS integrations as well as HTTP backends.",
                    "Can shape how teams version and publish APIs.",
                ],
                advantages=[
                    "Strong API management capabilities without building them from scratch.",
                    "Excellent fit for Lambda-centric systems.",
                    "Useful request governance controls such as throttling and authorizers.",
                ],
                disadvantages=[
                    "May be unnecessary overhead for simple internal-only traffic routing.",
                    "Payload transformations and mapping logic can become hard to maintain.",
                    "Costs differ materially from raw load balancer exposure at scale.",
                ],
                implementation_notes=[
                    "Use HTTP APIs unless you specifically need REST API features that HTTP APIs do not cover.",
                    "Keep request transformation logic minimal and testable.",
                    "Set throttles and auth centrally instead of re-implementing them in each backend.",
                ],
                comparison=[
                    ("API Gateway vs ALB", "Choose API Gateway for API product features; choose ALB for simpler service ingress."),
                    ("API Gateway vs CloudFront", "Choose CloudFront for CDN edge delivery; choose API Gateway for API lifecycle and request control."),
                ],
                code_title="Example: HTTP API integration",
                code="""aws apigatewayv2 create-api \
  --name orders-http-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:us-east-1:123456789012:function:orders-handler""",
            ),
            svc(
                name="AWS Direct Connect",
                tagline="Dedicated private network connection from your premises into AWS.",
                when_to_use="Use Direct Connect when hybrid connectivity needs more predictable throughput, private routing, or consistent performance than internet VPN can provide.",
                deep_dive="Direct Connect gives enterprises a dedicated private link into AWS through partner or hosted connectivity models. It is commonly used for large-scale migrations, predictable data transfer, regulated environments, and hybrid systems where internet-based connectivity is not good enough. Direct Connect is not a universal requirement; many teams do fine with VPN. But for heavy hybrid traffic or strict network posture, it becomes foundational.",
                variations=[
                    "Dedicated and hosted connection models.",
                    "Private, public, and transit virtual interfaces depending on target routing needs.",
                    "Single-link and resilient dual-link hybrid designs.",
                ],
                use_cases=[
                    "Data center to AWS connectivity, large migrations, backup transfer, and enterprise hybrid operations.",
                    "Private access to VPC resources with predictable network behavior.",
                    "Regulated or latency-sensitive hybrid applications.",
                ],
                properties=[
                    "Physical or partner-facilitated private connectivity rather than internet transit.",
                    "Often paired with VPN for encrypted overlay or failover patterns.",
                    "Design must account for redundancy and routing strategy.",
                ],
                advantages=[
                    "More consistent connectivity than internet-only paths in many scenarios.",
                    "Supports large hybrid traffic volumes well.",
                    "Can reduce exposure to public internet path volatility.",
                ],
                disadvantages=[
                    "Longer lead time and more network coordination than VPN-based connectivity.",
                    "Additional cost and carrier/partner dependencies.",
                    "Not justified for every workload or every organization size.",
                ],
                implementation_notes=[
                    "Design for redundancy from day one; a single link is a risk, not a strategy.",
                    "Be explicit about route ownership and BGP operations.",
                    "Use Direct Connect when business need is clear, not just because it sounds enterprise-grade.",
                ],
                comparison=[
                    ("Direct Connect vs Site-to-Site VPN", "Choose Direct Connect for predictable high-volume private connectivity; use VPN for simpler and faster setup."),
                    ("Direct Connect public vs private VIF", "Public reaches AWS public services; private reaches VPC resources."),
                ],
                code_title="Example: conceptual hybrid routing design",
                code="""Office/Data Center
  -> Direct Connect location
  -> Direct Connect gateway
  -> Transit Gateway or VPC
  -> Private subnets, databases, and internal application tiers""",
            ),
        ],
    ),
    Category(
        name="Security",
        intro="Security services shape identity, secret handling, encryption, web protection, and threat detection. The most useful mental model is layered control: identity defines who can do something, encryption protects data, perimeter controls filter requests, and detection services tell you when assumptions are failing.",
        services=[
            svc(
                name="AWS IAM",
                tagline="Foundational identity and authorization service for AWS accounts, principals, roles, and policies.",
                when_to_use="Use IAM everywhere as the core mechanism for AWS API authorization and role-based access to resources.",
                deep_dive="IAM is the control plane gatekeeper of AWS. Users, groups, roles, policies, permission boundaries, conditions, and trust relationships define what actors can do and under what context. The most important pattern is short-lived access through roles rather than long-lived credentials. In mature AWS environments, almost every security conversation eventually touches IAM design quality.",
                variations=[
                    "Principals: users, roles, federated identities, service principals.",
                    "Policy layers: identity policies, resource policies, SCPs, permission boundaries, session policies.",
                    "Access styles: console federation, role assumption, workload IAM roles, cross-account trust.",
                ],
                use_cases=[
                    "Human admin access, CI/CD deployment access, workload-to-service permissions, and cross-account automation.",
                    "Least-privilege control of all AWS services.",
                    "Temporary credential issuance through assumed roles.",
                ],
                properties=[
                    "Policy evaluation combines allows, denies, conditions, and multiple policy sources.",
                    "Identity design strongly affects auditability and blast radius.",
                    "IAM is central to both platform security and developer experience.",
                ],
                advantages=[
                    "Rich and expressive authorization model.",
                    "Short-lived credentials through roles reduce secret sprawl.",
                    "Central to multi-account governance and automation safety.",
                ],
                disadvantages=[
                    "Policy complexity grows quickly in large estates.",
                    "Broad permissions and wildcard resources are easy shortcuts with long-term cost.",
                    "Troubleshooting effective permissions can be non-trivial.",
                ],
                implementation_notes=[
                    "Prefer roles over access keys wherever possible.",
                    "Use least privilege and test policies with realistic workflows.",
                    "Treat cross-account trust policies as high-risk surfaces that need review.",
                ],
                comparison=[
                    ("IAM roles vs static credentials", "Prefer roles almost always for operational safety."),
                    ("IAM vs Cognito", "IAM controls AWS resource access; Cognito manages end-user app identity."),
                ],
                code_title="Example: trust policy for EC2 role",
                code="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}""",
            ),
            svc(
                name="Amazon Cognito",
                tagline="Managed identity service for application end users, sign-in flows, and federation.",
                when_to_use="Use Cognito when your application needs user sign-up, sign-in, token issuance, and social or enterprise federation.",
                deep_dive="Cognito is application identity, not infrastructure IAM. It helps web and mobile apps manage user pools, authentication flows, hosted UI, MFA, and identity federation. Cognito can also broker identities to AWS resources through identity pools, though that model should be used carefully. It is valuable when a team wants managed auth building blocks without operating a custom identity platform.",
                variations=[
                    "User Pools for authentication and user directory management.",
                    "Identity Pools for brokering federated identities to AWS credentials.",
                    "Hosted UI, custom auth flows, MFA, and social/SAML/OIDC federation.",
                ],
                use_cases=[
                    "Consumer apps, internal portals, mobile apps, and B2C-style sign-in systems.",
                    "Applications needing JWT-based identity with managed auth flows.",
                    "Federated access across social and enterprise identity providers.",
                ],
                properties=[
                    "Issues tokens for applications and can integrate with API Gateway and ALB auth patterns.",
                    "Supports managed user directory behavior and federation choices.",
                    "Useful when auth is a feature, not the company's main product.",
                ],
                advantages=[
                    "Avoids building core auth plumbing from scratch.",
                    "Scales well for many application identity scenarios.",
                    "Supports common auth standards and user management features.",
                ],
                disadvantages=[
                    "Customization has boundaries and some flows can feel opaque.",
                    "Complex identity and token flows still require careful design.",
                    "Migration between auth systems can be painful later.",
                ],
                implementation_notes=[
                    "Use Cognito for application users, not for AWS admin access.",
                    "Keep token claims and scopes intentionally designed.",
                    "Validate UX requirements early if hosted UI is part of the plan.",
                ],
                comparison=[
                    ("Cognito vs custom auth", "Choose Cognito when managed identity is good enough and speed matters."),
                    ("Cognito User Pools vs Identity Pools", "User Pools authenticate users; Identity Pools broker access to AWS resources."),
                ],
                code_title="Example: initiate auth flow",
                code="""aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id 4exampleclientid \
  --auth-parameters USERNAME=user@example.com,PASSWORD='StrongPass!123'""",
            ),
            svc(
                name="AWS KMS",
                tagline="Managed cryptographic key service for encryption control, key policies, and audit integration.",
                when_to_use="Use KMS when AWS services or applications need centralized key management, envelope encryption, and audit-friendly key usage controls.",
                deep_dive="KMS is the standard encryption control plane in AWS. Many AWS services can use KMS keys to encrypt data at rest, and applications can call KMS directly for envelope encryption patterns. The important architecture questions are ownership, key policy design, cross-account use, rotation, and whether KMS-native performance is acceptable for the workload. KMS usually works best when paired with data keys rather than making every application encrypt large payloads directly with the service.",
                variations=[
                    "AWS managed keys, customer managed keys, multi-Region keys, and imported/external key material options.",
                    "Symmetric and asymmetric keys depending on cryptographic use case.",
                    "Service-integrated encryption versus application-driven envelope encryption.",
                ],
                use_cases=[
                    "Encrypting S3, EBS, RDS, Secrets Manager, and application data.",
                    "Controlling key access by account, role, and service context.",
                    "Auditing key usage in regulated environments.",
                ],
                properties=[
                    "Central key lifecycle service with strong IAM and policy integration.",
                    "Backs many AWS encryption-at-rest features.",
                    "Application usage often relies on data keys for scale and efficiency.",
                ],
                advantages=[
                    "Standardized encryption control across AWS services.",
                    "Good audit and access governance model.",
                    "Reduces need to run custom HSM-backed key systems for many teams.",
                ],
                disadvantages=[
                    "Policy design and grants can become complex in multi-account use.",
                    "Per-request cost and latency matter for high-volume direct usage.",
                    "Does not remove the need for sound application secret and data handling design.",
                ],
                implementation_notes=[
                    "Prefer customer managed keys for critical systems that need explicit ownership.",
                    "Use envelope encryption for larger payload workflows.",
                    "Keep key policies narrow and avoid unnecessary wildcards.",
                ],
                comparison=[
                    ("KMS vs CloudHSM", "Choose KMS for most managed encryption needs; choose CloudHSM for strict dedicated HSM control requirements."),
                    ("KMS vs Secrets Manager", "KMS manages keys; Secrets Manager manages secrets while often using KMS underneath."),
                ],
                code_title="Example: encrypt with KMS",
                code="""aws kms encrypt \
  --key-id alias/app-data \
  --plaintext fileb://payload.txt \
  --output text \
  --query CiphertextBlob""",
            ),
            svc(
                name="AWS Secrets Manager",
                tagline="Managed secret storage and rotation for credentials, tokens, and connection strings.",
                when_to_use="Use Secrets Manager when applications need secure retrieval and rotation of secrets rather than hard-coded configuration.",
                deep_dive="Secrets Manager stores secrets, controls access, versions values, and can automate rotation for supported systems such as databases. It is most useful when teams want to eliminate plaintext secrets in repos, images, environment files, and ad hoc vaulting solutions. The biggest design decision is retrieval strategy: fetch at startup, cache in memory, or integrate with rotation-aware sidecars or agents.",
                variations=[
                    "Managed rotation for supported services and custom Lambda rotation workflows.",
                    "Version stages such as AWSCURRENT and AWSPREVIOUS.",
                    "Integration with ECS, Lambda, EKS, and application startup flows.",
                ],
                use_cases=[
                    "Database passwords, API keys, OAuth client secrets, SSH credentials, and certificates.",
                    "Removing secret sprawl from code and CI/CD variables.",
                    "Automated credential rotation for databases and apps.",
                ],
                properties=[
                    "Encrypted secret store with fine-grained IAM access control.",
                    "Supports versioning and rotation workflows.",
                    "Works well with bootstrapped app config and runtime fetch patterns.",
                ],
                advantages=[
                    "Far safer than embedding secrets in code or static config files.",
                    "Rotation support reduces manual secret hygiene burden.",
                    "Strong integration across AWS runtime services.",
                ],
                disadvantages=[
                    "Apps still need sensible local caching and refresh logic.",
                    "Rotation can break consumers if compatibility assumptions are weak.",
                    "Cost may exceed Parameter Store for large low-sensitivity configuration catalogs.",
                ],
                implementation_notes=[
                    "Group secrets by lifecycle and ownership, not just by application name.",
                    "Cache secrets responsibly to avoid latency and API overuse.",
                    "Test rotation in non-production with real consumers before enabling broadly.",
                ],
                comparison=[
                    ("Secrets Manager vs SSM Parameter Store", "Choose Secrets Manager when rotation and secret-focused controls are needed."),
                    ("Secrets Manager vs env vars", "Use env vars only as short-lived delivery mechanisms, not as the secret system of record."),
                ],
                code_title="Example: retrieve a secret",
                code="""aws secretsmanager get-secret-value \
  --secret-id prod/orders/db \
  --query SecretString \
  --output text""",
            ),
            svc(
                name="AWS WAF",
                tagline="Web application firewall for filtering, rate limiting, and inspecting HTTP/S traffic.",
                when_to_use="Use WAF when internet-facing applications need managed rules and custom controls against common web exploits and abusive request patterns.",
                deep_dive="WAF attaches to CloudFront, ALB, API Gateway, and some other front-door services to inspect layer-7 traffic. It is useful for managed rule groups, IP reputation filtering, request size checks, bot mitigation, rate-based rules, geo controls, and custom match logic. WAF is valuable but not magical: it is one layer in defense-in-depth, not a substitute for secure application code.",
                variations=[
                    "Managed rule groups, custom rules, rate-based rules, and CAPTCHA/challenge capabilities.",
                    "Deployment in front of CloudFront, ALB, and API Gateway.",
                    "Per-application or shared policy models depending on traffic ownership.",
                ],
                use_cases=[
                    "Blocking common OWASP-style attacks, abusive scraping, and high-rate request floods.",
                    "Protecting APIs and websites with centrally managed policy.",
                    "Applying different controls by path, country, IP reputation, or header patterns.",
                ],
                properties=[
                    "HTTP/S inspection at the application edge or ingress layer.",
                    "Rule order and false-positive management are operationally important.",
                    "Best when combined with CloudFront and Shield for layered protection.",
                ],
                advantages=[
                    "Fast way to improve edge-layer defense.",
                    "Managed rules reduce the burden of writing every detection yourself.",
                    "Useful request-level observability and control.",
                ],
                disadvantages=[
                    "False positives can impact customers if rules are rolled out carelessly.",
                    "Cannot fix vulnerable application logic behind it.",
                    "Rule tuning requires real traffic awareness.",
                ],
                implementation_notes=[
                    "Start in count mode where possible before enforcing aggressively.",
                    "Review blocked traffic regularly and tune to actual attack patterns.",
                    "Separate reusable baseline controls from app-specific exceptions.",
                ],
                comparison=[
                    ("WAF vs Security Groups", "WAF filters HTTP/S requests; security groups filter network traffic at lower layers."),
                    ("WAF vs Shield", "WAF targets application-layer filtering; Shield focuses on DDoS mitigation."),
                ],
                code_title="Example: WAF rate-based rule concept",
                code="""If requests from one IP > 2,000 in 5 minutes:
  action = BLOCK
Else:
  action = ALLOW

Scope: /login and /checkout paths""",
            ),
            svc(
                name="AWS Shield",
                tagline="Managed DDoS protection service for network and application availability.",
                when_to_use="Use Shield whenever public workloads need AWS-native DDoS protection, with Advanced for higher-risk internet-facing systems.",
                deep_dive="Shield Standard is built in for many AWS customers at no additional charge and protects against common volumetric attacks. Shield Advanced adds deeper visibility, enhanced mitigations, and cost protection for critical applications behind supported front-door services. The real design choice is not whether DDoS exists, but whether the application's risk profile justifies the Advanced operating model and associated support processes.",
                variations=[
                    "Shield Standard for baseline protections.",
                    "Shield Advanced for enhanced protections, visibility, and support workflows.",
                    "Common pairings with CloudFront, Route 53, and ELB.",
                ],
                use_cases=[
                    "Public websites, APIs, e-commerce systems, and business-critical internet applications.",
                    "High-visibility systems that cannot tolerate prolonged disruption.",
                    "Workloads likely to attract volumetric or targeted disruption.",
                ],
                properties=[
                    "Focused on availability protection against DDoS events.",
                    "Most effective when paired with edge architecture and observability.",
                    "Service value depends on application criticality and exposure profile.",
                ],
                advantages=[
                    "AWS-native DDoS protection that fits cloud front-door patterns well.",
                    "Advanced tier adds operational support for higher-risk systems.",
                    "Works naturally with CloudFront and Route 53-based architectures.",
                ],
                disadvantages=[
                    "Not a replacement for WAF, secure code, or resilient application design.",
                    "Advanced tier is not necessary for every workload.",
                    "Teams still need incident response runbooks and monitoring.",
                ],
                implementation_notes=[
                    "Use CloudFront and Route 53 strategically because Shield protections are strongest at the front door.",
                    "Know which applications justify Shield Advanced by business impact, not fear alone.",
                    "Coordinate with operations and security teams before an incident, not during one.",
                ],
                comparison=[
                    ("Shield Standard vs Advanced", "Advanced is for higher business-criticality, visibility, and response support needs."),
                    ("Shield vs WAF", "Shield handles DDoS protection; WAF handles application-layer request filtering."),
                ],
                code_title="Example: protection architecture",
                code="""Internet users
  -> Route 53
  -> CloudFront + AWS Shield + AWS WAF
  -> ALB/API Gateway
  -> application services""",
            ),
            svc(
                name="Amazon GuardDuty",
                tagline="Managed threat detection that analyzes logs, events, and telemetry for suspicious behavior.",
                when_to_use="Use GuardDuty when you need continuous detection of anomalous or malicious activity across AWS accounts and workloads.",
                deep_dive="GuardDuty consumes sources such as CloudTrail events, VPC flow logs, DNS logs, EKS audit signals, malware-related findings, and runtime telemetry features depending on enabled capabilities. It is designed to surface suspicious behaviors like credential abuse, reconnaissance, crypto-mining activity, and anomalous network patterns. GuardDuty is a detection layer, not a prevention system, so its real value depends on triage quality and response automation.",
                variations=[
                    "Core detection from account and network telemetry.",
                    "Optional features for EKS, S3, malware scanning, and runtime-related findings in supported areas.",
                    "Multi-account delegated administration patterns.",
                ],
                use_cases=[
                    "Security monitoring in AWS organizations.",
                    "Detection of suspicious access patterns, compromised instances, or unusual data behavior.",
                    "Feeding findings into Security Hub, SIEMs, or incident workflows.",
                ],
                properties=[
                    "Managed analytics on AWS-native signals rather than a DIY detection stack.",
                    "Works best as part of a centralized security operations process.",
                    "Findings need prioritization and response automation to deliver real value.",
                ],
                advantages=[
                    "Fast path to threat detection without building a custom SOC pipeline first.",
                    "Strong AWS-native signal coverage.",
                    "Useful organization-wide security baseline control.",
                ],
                disadvantages=[
                    "Detection alone is not protection or response.",
                    "Noisy or poorly triaged findings can lead to alert fatigue.",
                    "Teams still need ownership for investigation and remediation.",
                ],
                implementation_notes=[
                    "Enable GuardDuty centrally and define finding ownership by severity.",
                    "Automate obvious containment actions carefully and audit those workflows.",
                    "Correlate GuardDuty with CloudTrail, Config, and workload logs for investigation context.",
                ],
                comparison=[
                    ("GuardDuty vs CloudTrail", "CloudTrail records events; GuardDuty analyzes signals for suspicious activity."),
                    ("GuardDuty vs Security Hub", "GuardDuty generates threat findings; Security Hub aggregates security posture and findings."),
                ],
                code_title="Example: event-driven GuardDuty response concept",
                code="""GuardDuty finding -> EventBridge rule -> Lambda responder
Responder steps:
1. Tag affected resource
2. Notify security channel
3. Optionally isolate instance or revoke credential""",
            ),
        ],
    ),
    Category(
        name="Monitoring",
        intro="Monitoring is how cloud systems become operable instead of merely deployable. Metrics, logs, traces, config history, and audit events answer different questions, and AWS splits them across several services that work best when combined rather than treated as substitutes.",
        services=[
            svc(
                name="Amazon CloudWatch",
                tagline="Metrics, logs, alarms, dashboards, and operational monitoring for AWS resources and applications.",
                when_to_use="Use CloudWatch as the default operational telemetry platform for AWS workloads.",
                deep_dive="CloudWatch spans multiple concerns: metrics, log groups, alarms, dashboards, anomaly detection, event rules in older patterns, synthetic checks in adjacent offerings, and more. Teams get the most value when they standardize telemetry naming, dimensions, and alert design. The service becomes significantly more useful when metrics, logs, and application-level custom telemetry are treated as part of product engineering rather than afterthoughts.",
                variations=[
                    "Native service metrics, custom application metrics, log groups, alarms, dashboards, and metric math.",
                    "Container and server observability extensions depending on workload.",
                    "Composite alarms and anomaly detection for mature operations teams.",
                ],
                use_cases=[
                    "Resource monitoring, SLO alerting, application logs, dashboards, and cost-aware observability baselines.",
                    "Autoscaling triggers and incident notifications.",
                    "Centralizing runtime telemetry for EC2, Lambda, ECS, EKS, and many managed services.",
                ],
                properties=[
                    "Operational telemetry platform rather than a single feature.",
                    "Works best with naming standards and alert hygiene.",
                    "Supports both AWS-native and custom application observability patterns.",
                ],
                advantages=[
                    "Deep AWS integration and broad default coverage.",
                    "Useful for both dashboards and automation triggers.",
                    "Good default observability baseline without introducing external tooling immediately.",
                ],
                disadvantages=[
                    "Alert sprawl is common if teams do not design carefully.",
                    "Log costs and cardinality issues can creep up quickly.",
                    "Complex distributed observability may still need complementary tooling patterns.",
                ],
                implementation_notes=[
                    "Alert on symptoms the customer feels, not every noisy infrastructure fluctuation.",
                    "Name metrics and dashboards by service and environment consistently.",
                    "Set log retention explicitly instead of keeping everything forever.",
                ],
                comparison=[
                    ("CloudWatch vs X-Ray", "CloudWatch covers broad metrics and logs; X-Ray focuses on request tracing."),
                    ("CloudWatch vs Config", "CloudWatch monitors operational behavior; Config tracks resource configuration state."),
                ],
                code_title="Example: create a CPU alarm",
                code="""aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-orders-api \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 60 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 5""",
            ),
            svc(
                name="AWS CloudTrail",
                tagline="Audit log of AWS API activity and account-level actions.",
                when_to_use="Use CloudTrail when you need to know who changed what, when, from where, and via which API path.",
                deep_dive="CloudTrail records management events and, when configured, data events for services such as S3 and Lambda. It is central to audit, forensics, change tracking, and incident response. CloudTrail is not performance telemetry; it is a control plane history system. Teams gain the most value when trails are centralized, immutable enough for investigation needs, and connected to detection or alerting for sensitive events.",
                variations=[
                    "Management events, data events, and insights features depending on use case.",
                    "Organization-wide multi-account trails.",
                    "Event history, S3 delivery, and Lake-based query patterns.",
                ],
                use_cases=[
                    "Audit trails, security investigations, compliance evidence, and sensitive action alerting.",
                    "Tracking IAM changes, key deletions, bucket policy changes, and deployment actions.",
                    "Post-incident reconstruction of account activity.",
                ],
                properties=[
                    "Records AWS API actions rather than app business events.",
                    "Critical for security and compliance, but also useful for ops debugging.",
                    "Needs retention and centralization strategy to be operationally useful.",
                ],
                advantages=[
                    "Essential audit foundation for AWS environments.",
                    "Wide service coverage and strong investigative value.",
                    "Integrates naturally with GuardDuty, EventBridge, and SIEM workflows.",
                ],
                disadvantages=[
                    "Data events can become expensive if enabled carelessly everywhere.",
                    "Volume is high; without search and triage patterns, it becomes hard to use.",
                    "Not a substitute for application logs.",
                ],
                implementation_notes=[
                    "Enable organization trails and protect the destination bucket strongly.",
                    "Alert on a shortlist of high-risk events instead of everything.",
                    "Use CloudTrail Lake or downstream analytics for deeper investigations.",
                ],
                comparison=[
                    ("CloudTrail vs CloudWatch Logs", "CloudTrail records AWS API actions; CloudWatch Logs capture runtime/app logs."),
                    ("CloudTrail vs Config", "CloudTrail records API calls; Config records resulting resource state over time."),
                ],
                code_title="Example: create a multi-region trail",
                code="""aws cloudtrail create-trail \
  --name org-audit-trail \
  --s3-bucket-name acme-cloudtrail-logs \
  --is-multi-region-trail""",
            ),
            svc(
                name="AWS Config",
                tagline="Configuration history and compliance evaluation for AWS resources.",
                when_to_use="Use Config when you need to know the state of resources over time and whether they violate defined configuration rules.",
                deep_dive="Config records snapshots of resource configuration and can evaluate rules to determine whether environments stay compliant with expectations such as encryption enabled, public access blocked, or approved instance types only. It is especially helpful for governance, drift detection, and audit readiness. It answers 'what does the environment look like and when did it change?' better than raw event logs do.",
                variations=[
                    "Configuration recorder and timeline history.",
                    "Managed and custom Config rules.",
                    "Conformance packs for grouped policy checks across accounts.",
                ],
                use_cases=[
                    "Compliance checking, drift visibility, security baselines, and governance reporting.",
                    "Answering whether buckets are public, keys are rotated, or resources are tagged correctly.",
                    "Multi-account control monitoring.",
                ],
                properties=[
                    "State-oriented view of infrastructure rather than request/response runtime behavior.",
                    "Rules can be managed by AWS or custom logic.",
                    "Works well in organizations that need policy evidence, not just operational dashboards.",
                ],
                advantages=[
                    "Excellent for governance and change-state visibility.",
                    "Makes audit and control reporting easier.",
                    "Useful complement to CloudTrail and IAM-based controls.",
                ],
                disadvantages=[
                    "Not a real-time app observability tool.",
                    "Rule sprawl can create noise if every possible check is enabled without ownership.",
                    "Custom rules add Lambda or logic maintenance burden.",
                ],
                implementation_notes=[
                    "Start with a focused control baseline: encryption, logging, public exposure, tagging, and backup-related policies.",
                    "Map each rule to an owner and remediation path.",
                    "Use conformance packs where a standard set of controls is repeated.",
                ],
                comparison=[
                    ("Config vs CloudTrail", "Config shows resource state and compliance; CloudTrail shows API activity."),
                    ("Config vs Security Hub", "Config is a control-state engine; Security Hub aggregates broader security posture findings."),
                ],
                code_title="Example: managed Config rule",
                code="""aws configservice put-config-rule \
  --config-rule '{
    "ConfigRuleName": "s3-bucket-server-side-encryption-enabled",
    "Source": {
      "Owner": "AWS",
      "SourceIdentifier": "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
    }
  }'""",
            ),
            svc(
                name="AWS X-Ray",
                tagline="Distributed tracing service for following requests across microservices and dependencies.",
                when_to_use="Use X-Ray when application latency, dependency behavior, and request-path debugging matter across multiple services.",
                deep_dive="X-Ray tracks segments and subsegments for a request as it flows through application components and some AWS integrations. It helps answer which dependency added latency, where errors cluster, and how a microservice call chain behaves in production. Tracing is most useful when teams use it proactively during performance tuning and incident response rather than enabling it once and forgetting it.",
                variations=[
                    "End-to-end request traces across instrumented services.",
                    "Service maps for dependency visualization.",
                    "Sampling strategies to balance insight and cost.",
                ],
                use_cases=[
                    "Debugging latency in microservices, serverless flows, and API chains.",
                    "Understanding which downstream dependencies are slow or error-prone.",
                    "Tracing customer-impacting transactions across many services.",
                ],
                properties=[
                    "Request-centric rather than host-centric visibility.",
                    "Depends on instrumentation quality and propagation across boundaries.",
                    "Complements logs and metrics rather than replacing them.",
                ],
                advantages=[
                    "Very helpful for tracing complex request paths.",
                    "Makes dependency and latency hotspots easier to see.",
                    "Good fit for distributed architectures where logs alone are insufficient.",
                ],
                disadvantages=[
                    "Requires instrumentation and trace propagation discipline.",
                    "Sampling can hide rare edge cases if set poorly.",
                    "Trace data without logging context still limits investigation depth.",
                ],
                implementation_notes=[
                    "Instrument customer-critical paths first, not every code path equally.",
                    "Propagate correlation IDs in addition to traces for operational clarity.",
                    "Use traces during load testing, not only after production incidents.",
                ],
                comparison=[
                    ("X-Ray vs CloudWatch Logs", "X-Ray follows a request path; logs capture event detail."),
                    ("X-Ray vs CloudWatch metrics", "X-Ray explains where latency happened; metrics show that latency exists."),
                ],
                code_title="Example: traced Lambda segment concept",
                code="""Client request
  -> API Gateway
  -> Lambda handler
  -> DynamoDB getItem
  -> SNS publish

Trace output identifies which sub-call dominated latency.""",
            ),
        ],
    ),
    Category(
        name="Messaging",
        intro="Messaging services decouple producers and consumers, smooth bursts, and change failure handling from synchronous dependency to asynchronous workflow. The key design tradeoffs are ordering, fan-out, delivery semantics, replayability, and how much coupling you want between systems.",
        services=[
            svc(
                name="Amazon SQS",
                tagline="Managed message queue for asynchronous buffering and work decoupling.",
                when_to_use="Use SQS when producers and consumers should be decoupled in time, scale, and failure handling.",
                deep_dive="SQS is the simplest reliable asynchronous backbone in AWS. Producers write messages to a queue, consumers poll, process, and delete them. Standard queues prioritize scale and at-least-once delivery; FIFO queues add ordering and deduplication guarantees with throughput tradeoffs. SQS improves resilience by turning spikes and partial outages into manageable backlog instead of immediate cascading failure.",
                variations=[
                    "Standard queues for high scale and at-least-once delivery.",
                    "FIFO queues for ordered processing and deduplication.",
                    "Dead-letter queues for poison-message isolation.",
                ],
                use_cases=[
                    "Worker processing, order workflows, email sending, ETL tasks, and service decoupling.",
                    "Absorbing spikes so consumers scale at their own pace.",
                    "Reducing synchronous dependency chains.",
                ],
                properties=[
                    "Pull-based queue with visibility timeout and retry semantics.",
                    "Excellent integration with Lambda, ECS, EC2 workers, and event workflows.",
                    "Design must account for duplicate processing and idempotency.",
                ],
                advantages=[
                    "Simple and highly effective resilience primitive.",
                    "Scales well and is easy to reason about operationally.",
                    "Makes backpressure explicit instead of hidden in request failures.",
                ],
                disadvantages=[
                    "Consumers must be idempotent because duplicates happen.",
                    "Long-running handlers need visibility timeout tuning.",
                    "Ordering guarantees require FIFO tradeoffs.",
                ],
                implementation_notes=[
                    "Use DLQs and monitor age-of-oldest-message, not just queue depth.",
                    "Make handlers idempotent before production traffic arrives.",
                    "Choose FIFO only when ordering is a real business requirement.",
                ],
                comparison=[
                    ("SQS vs SNS", "Choose SQS for buffering and queued processing; choose SNS for broadcast fan-out."),
                    ("SQS vs EventBridge", "Choose SQS for worker queues; choose EventBridge for event routing and pub/sub integration."),
                ],
                code_title="Example: send an SQS message",
                code="""aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/orders-queue \
  --message-body '{"orderId":"123","action":"reserve-inventory"}'""",
            ),
            svc(
                name="Amazon SNS",
                tagline="Managed pub/sub fan-out service for broadcasting messages to many subscribers.",
                when_to_use="Use SNS when one event should notify multiple downstream systems or channels.",
                deep_dive="SNS topics let publishers send one message that fans out to many subscribers such as SQS queues, Lambda functions, HTTPS endpoints, mobile push channels, email, or SMS in some patterns. The important design insight is that SNS decouples the publisher from knowing who all the consumers are. In event-driven systems, SNS is often the simplest first fan-out backbone before teams need more sophisticated routing logic.",
                variations=[
                    "Standard topics and FIFO topics where supported patterns apply.",
                    "Protocol-based subscriptions: SQS, Lambda, HTTPS, email, SMS, mobile push.",
                    "Message filtering policies for selective subscriber delivery.",
                ],
                use_cases=[
                    "Broadcasting order events, user notifications, audit fan-out, and multi-subscriber workflows.",
                    "Decoupling one producer from many listeners.",
                    "Notification pipelines to queues, functions, and webhooks.",
                ],
                properties=[
                    "Push-based fan-out rather than queued pull processing.",
                    "Subscriber filtering reduces unnecessary downstream noise.",
                    "Often paired with SQS for durable multi-consumer event processing.",
                ],
                advantages=[
                    "Very simple fan-out model.",
                    "Supports many subscriber types with little setup.",
                    "Great fit for event broadcast and notifications.",
                ],
                disadvantages=[
                    "Less flexible event routing than EventBridge for complex patterns.",
                    "Not itself a work queue with backlog semantics like SQS.",
                    "Some subscriber patterns still need durability via SQS.",
                ],
                implementation_notes=[
                    "Fan out to SQS when subscribers need durable independent processing.",
                    "Use filtering policies to avoid event spam.",
                    "Define event contracts explicitly so many consumers do not create chaos.",
                ],
                comparison=[
                    ("SNS vs EventBridge", "Choose SNS for simple fan-out; choose EventBridge for richer routing and SaaS/AWS event bus semantics."),
                    ("SNS vs SQS", "SNS broadcasts; SQS buffers work for consumers."),
                ],
                code_title="Example: publish to an SNS topic",
                code="""aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456789012:order-events \
  --message '{"eventType":"OrderPlaced","orderId":"123"}'""",
            ),
            svc(
                name="Amazon EventBridge",
                tagline="Event bus and routing service for application events, AWS service events, schedules, and integrations.",
                when_to_use="Use EventBridge when you need event routing based on patterns, multi-producer bus architectures, SaaS integration, or schedule-based triggering.",
                deep_dive="EventBridge acts like a central event router: producers emit events, rules match patterns, and targets receive them. It is ideal for event-driven architectures where routing logic should live outside each producer. It also handles AWS service events and scheduled invocations. Compared with SNS, EventBridge shines when matching rules, schema discipline, cross-account buses, and richer event governance matter.",
                variations=[
                    "Default, custom, and partner event buses.",
                    "Rules, archives, replays, scheduler, and pipes-style integration patterns.",
                    "Cross-account event routing for platform architectures.",
                ],
                use_cases=[
                    "Decoupled application event routing, AWS service event automation, cron replacement, and SaaS event ingestion.",
                    "Platform-wide event contracts with many independent consumers.",
                    "Reactive ops and remediation workflows.",
                ],
                properties=[
                    "Pattern-based routing on structured event envelopes.",
                    "Useful for governance and event contract standardization.",
                    "Supports replay and routing evolution more naturally than direct point-to-point integrations.",
                ],
                advantages=[
                    "Powerful routing model with low operational burden.",
                    "Natural fit for AWS-native event automation and business events.",
                    "Cleaner decoupling than embedding subscriber logic in producers.",
                ],
                disadvantages=[
                    "Requires event contract discipline to stay understandable at scale.",
                    "Not a durable worker queue in the same way SQS is.",
                    "Teams can create 'event spaghetti' if ownership is vague.",
                ],
                implementation_notes=[
                    "Standardize event envelope fields such as source, detail-type, and version.",
                    "Route to SQS for durable work execution when needed.",
                    "Use archives and replay intentionally for event-driven debugging and recovery.",
                ],
                comparison=[
                    ("EventBridge vs SNS", "Choose EventBridge for routing logic and event buses; choose SNS for simple fan-out."),
                    ("EventBridge vs cron jobs", "Choose EventBridge Scheduler for managed schedule-based invocation instead of homegrown timers."),
                ],
                code_title="Example: put a custom event",
                code="""aws events put-events \
  --entries '[
    {
      "Source": "acme.orders",
      "DetailType": "OrderPlaced",
      "Detail": "{\"orderId\":\"123\",\"customerId\":\"c-99\"}",
      "EventBusName": "application-bus"
    }
  ]'""",
            ),
            svc(
                name="Amazon MQ",
                tagline="Managed message broker service for workloads that need traditional broker protocols such as ActiveMQ or RabbitMQ.",
                when_to_use="Use Amazon MQ when legacy applications or integration products require standard broker protocols rather than AWS-native queue or event services.",
                deep_dive="Amazon MQ exists because not every workload can or should be rewritten around SNS, SQS, or EventBridge right now. It offers managed ActiveMQ and RabbitMQ deployments for JMS, AMQP, STOMP, MQTT, and similar integration expectations depending on engine choice. It is usually the right migration bridge when application protocol compatibility matters more than adopting the most AWS-native messaging style immediately.",
                variations=[
                    "ActiveMQ and RabbitMQ engine choices depending on protocol and app compatibility needs.",
                    "Single-instance and highly available deployment patterns.",
                    "Broker-centric messaging semantics such as exchanges, queues, and topics depending on engine.",
                ],
                use_cases=[
                    "Legacy enterprise integration, JMS-based applications, and protocol-dependent middleware.",
                    "Migration of broker-based systems without an immediate rewrite.",
                    "Applications that explicitly depend on RabbitMQ/ActiveMQ semantics.",
                ],
                properties=[
                    "Managed broker rather than queue-as-a-service abstraction.",
                    "Compatibility-driven choice more than a greenfield-first default.",
                    "Operational characteristics depend on broker engine selection.",
                ],
                advantages=[
                    "Preserves protocol compatibility for existing systems.",
                    "Reduces self-managed broker operational burden.",
                    "Useful bridge for gradual modernization.",
                ],
                disadvantages=[
                    "Usually more operationally involved than SQS/SNS/EventBridge.",
                    "Not the simplest choice for greenfield AWS-native systems.",
                    "Engine-specific semantics mean portability is not free.",
                ],
                implementation_notes=[
                    "Use Amazon MQ when protocol compatibility is a requirement, not as a default habit.",
                    "Plan a long-term modernization roadmap if the current broker model is legacy debt.",
                    "Benchmark failover and throughput behavior for the chosen engine.",
                ],
                comparison=[
                    ("Amazon MQ vs SQS", "Choose MQ for protocol compatibility; choose SQS for simpler AWS-native queuing."),
                    ("RabbitMQ vs ActiveMQ", "Choose based on required protocol semantics and existing application dependencies."),
                ],
                code_title="Example: broker-centric architecture",
                code="""Legacy app -> RabbitMQ/ActiveMQ broker on Amazon MQ
Consumers:
1. order-processor service
2. billing integration
3. notification adapter""",
            ),
        ],
    ),
    Category(
        name="Analytics",
        intro="Analytics services turn stored data into usable insight. The key design choices are whether you want interactive query, managed Hadoop/Spark-style processing, streaming ingestion, ETL metadata management, or BI consumption. These services often work best together rather than independently.",
        services=[
            svc(
                name="Amazon Athena",
                tagline="Serverless interactive SQL over data in S3.",
                when_to_use="Use Athena when you want fast ad hoc or scheduled SQL analysis on data already stored in S3 without managing a cluster.",
                deep_dive="Athena is often the fastest route from raw data to answers. You point it at S3-backed files, define schema in the Glue Data Catalog, and query using SQL. It is excellent for exploratory analytics, audits, log analysis, and lightweight lakehouse-style querying. It is less ideal when workloads become constant, heavily modeled, or require warehouse-style performance tuning that Redshift handles better.",
                variations=[
                    "Interactive ad hoc SQL.",
                    "Partitioned and columnar lake querying with Glue Catalog integration.",
                    "Workgroups for query isolation, governance, and cost control.",
                ],
                use_cases=[
                    "Querying logs, audit data, clickstream data, and staged datasets in S3.",
                    "Analytics for teams that already store raw data in a data lake.",
                    "Occasional reporting without running a warehouse full time.",
                ],
                properties=[
                    "Serverless query model over S3 data.",
                    "Performance and cost depend heavily on partitioning, file formats, and scanned data size.",
                    "Great companion to Glue and S3-centered analytics patterns.",
                ],
                advantages=[
                    "Very low operational burden.",
                    "Fast time-to-insight for many lake queries.",
                    "Excellent for occasional or exploratory analysis.",
                ],
                disadvantages=[
                    "Inefficient file formats and poor partitioning become expensive quickly.",
                    "Not a replacement for all warehouse workloads.",
                    "Concurrency and query tuning patterns are more limited than full warehouse systems.",
                ],
                implementation_notes=[
                    "Use Parquet or ORC and partition by common filter dimensions.",
                    "Set workgroup limits to avoid surprise spend.",
                    "Keep raw, curated, and analytics-ready zones distinct in S3.",
                ],
                comparison=[
                    ("Athena vs Redshift", "Choose Athena for serverless lake queries; choose Redshift for repeated warehouse analytics."),
                    ("Athena vs EMR Spark SQL", "Choose Athena when cluster control is unnecessary."),
                ],
                code_title="Example: Athena SQL",
                code="""SELECT customer_id, count(*) AS order_count
FROM lake.orders
WHERE order_date >= DATE '2026-04-01'
GROUP BY customer_id
ORDER BY order_count DESC
LIMIT 20;""",
            ),
            svc(
                name="Amazon EMR",
                tagline="Managed big data platform for Spark, Hadoop, Hive, and related distributed processing frameworks.",
                when_to_use="Use EMR when workloads need Spark/Hadoop ecosystem tools, custom distributed processing, or big data frameworks beyond serverless query alone.",
                deep_dive="EMR is the managed path for big data engines such as Spark. It can run on EC2, EKS, and increasingly flexible infrastructure choices. EMR is powerful for large ETL, machine learning preprocessing, and data engineering tasks that need more control than Athena or Glue jobs provide. It rewards teams that understand distributed compute tuning and cluster economics.",
                variations=[
                    "EMR on EC2, EMR on EKS, and serverless-style options in adjacent offerings.",
                    "Spark, Hive, HBase, Presto/Trino-style and other ecosystem engines depending on distribution capabilities.",
                    "Long-running clusters versus transient job clusters.",
                ],
                use_cases=[
                    "Large ETL pipelines, feature engineering, log processing, and distributed data science workloads.",
                    "Spark-first data platforms.",
                    "Custom distributed transformations too involved for simpler serverless query paths.",
                ],
                properties=[
                    "Framework-centric analytics platform rather than turnkey BI.",
                    "Performance and cost depend on cluster sizing, autoscaling, and storage design.",
                    "Excellent fit when teams already know Spark/Hadoop patterns.",
                ],
                advantages=[
                    "Very flexible for large-scale data processing.",
                    "Supports rich open-source data ecosystem tooling.",
                    "Can be cost-efficient when job scheduling and Spot usage are designed well.",
                ],
                disadvantages=[
                    "Higher operational and tuning burden than Athena or Glue.",
                    "Distributed job optimization requires specialized skills.",
                    "Easy to overprovision if clusters are left running casually.",
                ],
                implementation_notes=[
                    "Prefer transient clusters or managed job-oriented patterns when possible.",
                    "Separate storage in S3 from ephemeral compute for cleaner economics.",
                    "Instrument job runtime and shuffle costs early.",
                ],
                comparison=[
                    ("EMR vs Athena", "Choose EMR for custom large-scale distributed processing, not just interactive SQL."),
                    ("EMR vs Glue", "Choose EMR when Spark control and ecosystem flexibility outweigh Glue's managed simplicity."),
                ],
                code_title="Example: Spark job snippet",
                code="""from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("orders-etl").getOrCreate()
df = spark.read.parquet("s3://acme-raw/orders/")
result = df.groupBy("country").count()
result.write.mode("overwrite").parquet("s3://acme-curated/orders-by-country/")""",
            ),
            svc(
                name="AWS Glue",
                tagline="Managed data integration platform for ETL, schema discovery, and metadata cataloging.",
                when_to_use="Use Glue when you need managed crawlers, a shared data catalog, and serverless ETL jobs integrated with the AWS analytics stack.",
                deep_dive="Glue combines several roles: schema catalog, data crawlers, ETL jobs, and integration utilities. The Data Catalog is the connective tissue for many lake-based systems because Athena and other tools rely on shared metadata. Glue jobs are useful for serverless ETL, though teams should still treat them like real data products with versioning, testing, and observability rather than invisible background scripts.",
                variations=[
                    "Data Catalog, Crawlers, ETL Jobs, workflows, and related integration tools.",
                    "Spark-based and Python shell-style execution patterns depending on job type.",
                    "Catalog-centric data discovery and partition management.",
                ],
                use_cases=[
                    "Building curated datasets, discovering schemas, and maintaining lake metadata.",
                    "Scheduled ETL from raw landing zones to analytics-ready zones.",
                    "Shared metadata registry for lakehouse workflows.",
                ],
                properties=[
                    "Managed metadata and ETL service that integrates deeply with S3, Athena, and Redshift ecosystems.",
                    "Good default for lake-oriented data engineering on AWS.",
                    "Success depends on data model quality, partition strategy, and job governance.",
                ],
                advantages=[
                    "Useful combination of catalog and ETL capabilities.",
                    "Low infrastructure overhead for many data engineering teams.",
                    "Strong AWS integration across analytics services.",
                ],
                disadvantages=[
                    "Crawler results still need human validation and stewardship.",
                    "ETL jobs can become hard to govern if every team writes ad hoc transforms.",
                    "Complex transformations may fit EMR or custom platforms better.",
                ],
                implementation_notes=[
                    "Treat the catalog as shared infrastructure with ownership and naming standards.",
                    "Use curated zones rather than querying raw semi-structured data forever.",
                    "Keep ETL job code in source control with deployment pipelines.",
                ],
                comparison=[
                    ("Glue vs Athena", "Glue prepares and catalogs data; Athena queries it."),
                    ("Glue vs EMR", "Choose Glue for managed ETL and cataloging; choose EMR for heavier custom data processing."),
                ],
                code_title="Example: Glue crawler concept",
                code="""Data source: s3://acme-raw/orders/
Crawler scans prefixes
Catalog database: lake_raw
Catalog table created: lake_raw.orders_raw""",
            ),
            svc(
                name="Amazon Kinesis",
                tagline="Streaming data platform for ingesting and processing real-time event streams.",
                when_to_use="Use Kinesis when the workload needs near real-time ingestion and processing of ordered event streams at scale.",
                deep_dive="Kinesis is best understood as a family. Kinesis Data Streams supports custom stream consumers and shard-based scaling. Firehose focuses on delivery into destinations like S3, OpenSearch, or Redshift with minimal management. Video Streams serves media/IoT use cases. For this book's scope, the central pattern is event stream ingestion where data should be consumed continuously rather than via periodic batch loads.",
                variations=[
                    "Kinesis Data Streams for durable stream consumption.",
                    "Kinesis Data Firehose for managed delivery to downstream storage and analytics targets.",
                    "Video Streams for media/vision-oriented workloads.",
                ],
                use_cases=[
                    "Clickstream ingestion, IoT telemetry, log pipelines, fraud signals, and operational event streams.",
                    "Real-time dashboards and alerting pipelines.",
                    "Streaming data delivery into S3, Redshift, or analytics systems.",
                ],
                properties=[
                    "Ordered stream partitions with throughput scaling strategies.",
                    "Supports replay windows and multiple consumers depending on pattern.",
                    "Strong fit for continuously arriving data rather than periodic files.",
                ],
                advantages=[
                    "Enables near real-time analytics and event processing.",
                    "Supports high-volume stream ingestion patterns.",
                    "Flexible downstream consumer ecosystem.",
                ],
                disadvantages=[
                    "Shard or throughput planning can be non-trivial.",
                    "Consumer lag and reprocessing logic require operational maturity.",
                    "Overkill for simple event fan-out or queue-based workflows.",
                ],
                implementation_notes=[
                    "Choose Firehose when you mainly need managed delivery, not custom consumer logic.",
                    "Partition streams by keys that balance ordering with throughput distribution.",
                    "Monitor lag and shard hot spots early.",
                ],
                comparison=[
                    ("Kinesis vs SQS", "Choose Kinesis for ordered streams and continuous consumers; choose SQS for work queues."),
                    ("Kinesis vs EventBridge", "Choose Kinesis for high-throughput streaming ingestion; choose EventBridge for event routing."),
                ],
                code_title="Example: put a record into Kinesis",
                code="""aws kinesis put-record \
  --stream-name clickstream \
  --partition-key user-123 \
  --data '{"event":"page_view","path":"/pricing"}'""",
            ),
            svc(
                name="Amazon QuickSight",
                tagline="Cloud BI service for dashboards, reports, and embedded analytics.",
                when_to_use="Use QuickSight when business users or product teams need dashboards and visual analytics on top of curated data sources.",
                deep_dive="QuickSight sits at the consumption layer of analytics. It connects to data sources such as Athena, Redshift, RDS, and files, then turns them into dashboards, visuals, and embedded analytics. The real challenge is not the charting tool itself; it is whether the underlying data model is trustworthy, timely, and understandable. QuickSight works well when upstream data engineering has already produced clean semantic datasets.",
                variations=[
                    "Interactive dashboards, paginated reporting, and embedded analytics scenarios.",
                    "SPICE in-memory acceleration versus direct query modes.",
                    "Role-based authoring and consumption patterns.",
                ],
                use_cases=[
                    "Executive dashboards, product analytics, finance reports, and customer-facing embedded BI.",
                    "Operational reporting on top of Athena, Redshift, or RDS sources.",
                    "Shared analytics access for non-engineering teams.",
                ],
                properties=[
                    "BI presentation layer, not a data processing engine.",
                    "Performance depends on source design or SPICE strategy.",
                    "Best results come from curated datasets and clear metric definitions.",
                ],
                advantages=[
                    "Managed BI with AWS-native connectivity.",
                    "Good fit for internal and embedded analytics delivery.",
                    "Scales sharing more easily than spreadsheet-driven reporting cultures.",
                ],
                disadvantages=[
                    "Dashboard quality depends on upstream data quality and semantic consistency.",
                    "BI sprawl happens quickly if metrics are not governed.",
                    "Direct-query latency depends on the underlying source design.",
                ],
                implementation_notes=[
                    "Define business metrics centrally before publishing many dashboards.",
                    "Use SPICE for recurring dashboards where performance matters.",
                    "Treat dashboard ownership like product ownership, not one-time report creation.",
                ],
                comparison=[
                    ("QuickSight vs Athena", "Athena queries data; QuickSight presents it visually."),
                    ("QuickSight vs custom dashboards", "Choose QuickSight when managed BI is enough and speed matters more than bespoke UI control."),
                ],
                code_title="Example: analytics stack pattern",
                code="""S3/Redshift/Athena datasets
  -> curated semantic layer
  -> QuickSight dataset
  -> dashboard for finance and product teams""",
            ),
        ],
    ),
    Category(
        name="DevOps",
        intro="DevOps services automate source control, builds, deployments, pipelines, and infrastructure definition. The best designs keep delivery repeatable and observable, but they also avoid turning the CI/CD system into a maze of opaque YAML nobody trusts.",
        services=[
            svc(
                name="AWS CodeCommit",
                tagline="Managed Git repository service hosted on AWS.",
                when_to_use="Use CodeCommit when you need AWS-hosted Git repositories and want tight IAM-based access control inside AWS-centric environments.",
                deep_dive="CodeCommit provides managed Git repositories with IAM integration and encryption. For some organizations it fits well, especially where staying inside AWS-native controls matters. In many teams, however, GitHub or GitLab remains the broader ecosystem default. CodeCommit is strongest when repository hosting simplicity and AWS-native access governance are more important than marketplace integrations or social coding workflows.",
                variations=[
                    "Standard Git repository workflows with IAM-controlled access.",
                    "Integration into CodeBuild and CodePipeline.",
                    "Cross-account or role-based repository access models.",
                ],
                use_cases=[
                    "Internal source control in AWS-centric enterprises.",
                    "Code repositories where IAM control and private hosting are priorities.",
                    "Simple Git hosting for automation pipelines.",
                ],
                properties=[
                    "Managed Git service rather than full software collaboration platform.",
                    "Access control aligns with IAM roles and policies.",
                    "Best understood as a source repo backend, not a whole developer ecosystem.",
                ],
                advantages=[
                    "AWS-native identity and encryption integration.",
                    "Simple managed Git hosting without separate infrastructure.",
                    "Useful for tightly controlled internal environments.",
                ],
                disadvantages=[
                    "Smaller ecosystem than GitHub/GitLab for collaboration workflows.",
                    "May not match existing developer expectations outside AWS-centric shops.",
                    "Pull request and community workflow depth is more limited than major code hosting platforms.",
                ],
                implementation_notes=[
                    "Use it when AWS-native governance is a real requirement, not just familiarity bias.",
                    "Keep branch protections and repository permissions explicit.",
                    "Consider developer ergonomics before standardizing across the whole org.",
                ],
                comparison=[
                    ("CodeCommit vs GitHub", "Choose CodeCommit for AWS-native governance; choose GitHub for broader ecosystem and collaboration depth."),
                    ("CodeCommit vs S3 code storage", "Use proper Git hosting for source history, branching, and review workflows."),
                ],
                code_title="Example: clone a CodeCommit repository",
                code="""git clone https://git-codecommit.us-east-1.amazonaws.com/v1/repos/platform-infra""",
            ),
            svc(
                name="AWS CodeBuild",
                tagline="Managed build service for compiling code, running tests, and producing build artifacts.",
                when_to_use="Use CodeBuild when you want ephemeral build workers instead of maintaining your own CI runners.",
                deep_dive="CodeBuild spins up build environments on demand, runs your buildspec commands, and tears down the environment afterward. It supports many languages and integrates with source, artifact, and deployment services. It is most effective when builds are deterministic and well-packaged. If builds require too much custom machine state, the team should usually fix the build discipline rather than blame the service.",
                variations=[
                    "On-demand ephemeral builds across multiple runtime images.",
                    "Privileged container builds for Docker image creation.",
                    "Integrated roles, artifacts, and reports in AWS pipelines.",
                ],
                use_cases=[
                    "Running tests, packaging applications, building container images, and generating deployment artifacts.",
                    "Replacing self-hosted Jenkins workers for standard build flows.",
                    "CI steps inside CodePipeline-driven delivery.",
                ],
                properties=[
                    "Ephemeral build environments improve isolation and repeatability.",
                    "Build behavior is driven by buildspec configuration and environment variables.",
                    "Strong fit for infrastructure as code and application packaging workflows.",
                ],
                advantages=[
                    "No build fleet to patch or scale manually.",
                    "Good integration with AWS delivery services and IAM.",
                    "Repeatable ephemeral workers reduce machine drift.",
                ],
                disadvantages=[
                    "Cold start and package download time can affect build speed.",
                    "Over-customized build environments can get messy.",
                    "Debugging failed builds is harder if logs and artifacts are weak.",
                ],
                implementation_notes=[
                    "Keep builds hermetic and deterministic.",
                    "Cache dependencies intentionally but avoid hidden state dependence.",
                    "Publish test reports and artifacts so failures are diagnosable quickly.",
                ],
                comparison=[
                    ("CodeBuild vs self-hosted Jenkins agents", "Choose CodeBuild for ephemeral managed builds when custom fleet control is not required."),
                    ("CodeBuild vs GitHub-hosted runners", "Choose based on ecosystem fit, security posture, and where the rest of delivery lives."),
                ],
                code_title="Example: buildspec.yml",
                code="""version: 0.2
phases:
  install:
    commands:
      - npm ci
  build:
    commands:
      - npm test
      - npm run build
artifacts:
  files:
    - dist/**/*
    - appspec.yml""",
            ),
            svc(
                name="AWS CodeDeploy",
                tagline="Deployment orchestrator for application revisions across EC2, on-prem, Lambda, and some ECS patterns.",
                when_to_use="Use CodeDeploy when you need managed rollout control, deployment hooks, and traffic shifting for supported compute targets.",
                deep_dive="CodeDeploy coordinates how application revisions land on targets and how failures are handled. It supports in-place and blue/green patterns depending on target type and integrates with lifecycle hooks. For Lambda and ECS-style controlled traffic shifting, CodeDeploy can be part of safe progressive delivery. Its value rises when deployment risk is high enough that simple 'replace all' strategies are no longer acceptable.",
                variations=[
                    "In-place and blue/green deployments for supported targets.",
                    "EC2/on-prem, Lambda, and some ECS deployment patterns.",
                    "Lifecycle hooks for pre/post validation and rollback decisions.",
                ],
                use_cases=[
                    "Safer deployments to instance fleets and traffic-shifted serverless rollouts.",
                    "Coordinating revision rollout with health validation.",
                    "Standardizing deploy steps across multiple applications.",
                ],
                properties=[
                    "Deployment-focused service rather than full CI/CD system.",
                    "Hook-based lifecycle can embed checks and migration logic.",
                    "Works best when artifact and deployment boundaries are well-defined.",
                ],
                advantages=[
                    "Safer rollout control than ad hoc SSH or script deployments.",
                    "Supports rollback-aware release patterns.",
                    "Useful for progressive traffic shifting in supported cases.",
                ],
                disadvantages=[
                    "Another service to understand in the pipeline chain.",
                    "Hook logic can become brittle if it carries too much application behavior.",
                    "Some teams may prefer simpler container-native or GitOps deployment models.",
                ],
                implementation_notes=[
                    "Keep lifecycle hooks fast, explicit, and idempotent.",
                    "Use blue/green for customer-facing critical apps when possible.",
                    "Pair deployment metrics with rollback thresholds.",
                ],
                comparison=[
                    ("CodeDeploy vs direct ECS rolling update", "Choose CodeDeploy when deployment safety orchestration is a primary concern."),
                    ("CodeDeploy vs ad hoc scripts", "Choose CodeDeploy for repeatability, visibility, and rollback discipline."),
                ],
                code_title="Example: appspec.yml",
                code="""version: 0.0
os: linux
files:
  - source: /
    destination: /srv/orders-api
hooks:
  AfterInstall:
    - location: scripts/after_install.sh
  ApplicationStart:
    - location: scripts/start.sh
  ValidateService:
    - location: scripts/health_check.sh""",
            ),
            svc(
                name="AWS CodePipeline",
                tagline="Managed orchestration service for CI/CD stages and promotion flows.",
                when_to_use="Use CodePipeline when you want AWS-managed stage orchestration between source, build, approval, test, and deploy steps.",
                deep_dive="CodePipeline coordinates the flow of artifacts and actions across environments. It is useful when teams want a managed pipeline backbone without running a dedicated pipeline engine themselves. The core design challenge is pipeline clarity: the best pipelines are obvious, traceable, and environment-aware. The worst ones are dense graphs of hidden side effects and inconsistent manual approval logic.",
                variations=[
                    "Linear and branched stage orchestration patterns.",
                    "Integration with CodeBuild, CodeDeploy, CloudFormation, Lambda, and external actions.",
                    "Manual approval and environment promotion steps.",
                ],
                use_cases=[
                    "Application deployment pipelines, infrastructure promotion, and release automation.",
                    "Coordinating build, test, approval, and deploy across environments.",
                    "Reducing manual release steps.",
                ],
                properties=[
                    "Orchestration layer rather than build or deploy execution engine itself.",
                    "Artifact-centric workflow with stage transitions and approvals.",
                    "Best when stage purpose and ownership are obvious.",
                ],
                advantages=[
                    "Managed pipeline engine integrated with AWS tooling.",
                    "Reduces custom scripting glue for standard release flows.",
                    "Good visibility into artifact promotion stages.",
                ],
                disadvantages=[
                    "Complex pipelines can become hard to reason about.",
                    "Not always as flexible or developer-friendly as specialized CI/CD platforms.",
                    "Manual approval overuse can create release bottlenecks.",
                ],
                implementation_notes=[
                    "Keep stages aligned to real quality gates, not organizational theater.",
                    "Prefer automated checks over frequent manual approvals.",
                    "Version both application and infrastructure pipelines as code.",
                ],
                comparison=[
                    ("CodePipeline vs GitHub Actions", "Choose CodePipeline when the delivery backbone is mostly AWS-native."),
                    ("CodePipeline vs custom scripts", "Choose CodePipeline for repeatability and managed orchestration."),
                ],
                code_title="Example: pipeline stages",
                code="""Source -> Build -> Integration Test -> Manual Approval -> Deploy Staging -> Deploy Production""",
            ),
            svc(
                name="AWS CloudFormation",
                tagline="Infrastructure as code service for declaratively provisioning and updating AWS resources.",
                when_to_use="Use CloudFormation when infrastructure should be versioned, repeatable, and deployable through templates instead of click-ops.",
                deep_dive="CloudFormation turns infrastructure into code-defined stacks with change sets, rollbacks, dependencies, and drift considerations. It is a cornerstone of disciplined AWS operations because it makes environments reproducible and reviewable. Whether you write raw YAML/JSON templates or generate them via higher-level tools, the underlying value is the same: environments should be built from source control, not memory.",
                variations=[
                    "Stacks, nested stacks, StackSets, and change sets.",
                    "Raw templates and higher-level generation approaches such as CDK producing CloudFormation.",
                    "Cross-account and multi-region rollout patterns via StackSets.",
                ],
                use_cases=[
                    "Networking, IAM baselines, application infrastructure, and repeatable environment creation.",
                    "Standardized account bootstrapping and platform foundations.",
                    "Safe reviewed changes to AWS resources.",
                ],
                properties=[
                    "Declarative model with rollback behavior and stack lifecycle management.",
                    "Drift and template complexity require active stewardship.",
                    "Foundational for auditable and repeatable cloud engineering.",
                ],
                advantages=[
                    "Eliminates much manual infrastructure drift.",
                    "Improves reviewability, repeatability, and disaster recovery posture.",
                    "Integrates naturally with CI/CD.",
                ],
                disadvantages=[
                    "Templates can become verbose and difficult to maintain if not modularized.",
                    "Stack failures can be disruptive if change discipline is weak.",
                    "Still requires design thought; IaC does not automatically equal good architecture.",
                ],
                implementation_notes=[
                    "Break templates into coherent bounded stacks instead of giant all-in-one files.",
                    "Use parameters sparingly and favor opinionated defaults.",
                    "Review change sets before production updates.",
                ],
                comparison=[
                    ("CloudFormation vs Terraform", "Choose based on ecosystem preference and organizational standards; CloudFormation is the AWS-native path."),
                    ("CloudFormation vs console changes", "Choose CloudFormation for anything you expect to live beyond experimentation."),
                ],
                code_title="Example: CloudFormation S3 bucket resource",
                code="""Resources:
  ReferenceBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: acme-reference-assets
      VersioningConfiguration:
        Status: Enabled""",
            ),
        ],
    ),
    Category(
        name="AI/ML",
        intro="AI and ML services span model building, pretrained intelligence APIs, and document/media understanding. The main design question is whether you need a platform for custom ML workflows or a task-specific managed API that already solves the problem.",
        services=[
            svc(
                name="Amazon SageMaker",
                tagline="Managed ML platform for building, training, deploying, and operating machine learning models.",
                when_to_use="Use SageMaker when you need a full ML platform rather than a single pretrained AI API.",
                deep_dive="SageMaker covers notebooks, training jobs, processing, pipelines, feature management patterns, model registry, endpoints, batch transform, and MLOps-oriented workflows. It is the right choice when the organization owns the model lifecycle and needs repeatable ML engineering. It is not necessary when a task-specific API like Textract or Rekognition already solves the need without custom training.",
                variations=[
                    "Training jobs, processing jobs, real-time endpoints, serverless inference, and batch transform.",
                    "Pipelines, model registry, experiments, and MLOps workflow features.",
                    "Studio/notebook environments and managed algorithms versus custom containers.",
                ],
                use_cases=[
                    "Fraud models, recommendation models, forecasting, custom NLP/CV workflows, and MLOps pipelines.",
                    "Teams that need end-to-end ownership of training and deployment.",
                    "Production ML systems with governance requirements.",
                ],
                properties=[
                    "Platform for custom ML lifecycle management.",
                    "Supports both managed components and custom containers/frameworks.",
                    "Best fit when ML is a sustained engineering capability, not a one-off feature.",
                ],
                advantages=[
                    "Comprehensive managed ML platform.",
                    "Strong fit for production model lifecycle and governance.",
                    "Flexible enough for many custom training/inference patterns.",
                ],
                disadvantages=[
                    "Significant platform surface area and learning curve.",
                    "Overkill if a pretrained API already handles the problem.",
                    "MLOps discipline is still required; the service does not create it automatically.",
                ],
                implementation_notes=[
                    "Start with a narrow use case and a repeatable pipeline before scaling platform ambition.",
                    "Version datasets, features, training code, and model artifacts explicitly.",
                    "Choose endpoint type based on latency, volume, and cost profile.",
                ],
                comparison=[
                    ("SageMaker vs pretrained AI APIs", "Choose SageMaker when you need custom models or full ML lifecycle control."),
                    ("SageMaker real-time vs batch transform", "Real-time serves live requests; batch transform handles offline inference."),
                ],
                code_title="Example: SageMaker training estimator",
                code="""from sagemaker.sklearn.estimator import SKLearn

estimator = SKLearn(
    entry_point="train.py",
    role="arn:aws:iam::123456789012:role/sagemaker-execution-role",
    instance_type="ml.m5.large",
    framework_version="1.2-1",
)
estimator.fit({"train": "s3://acme-ml/train/"})""",
            ),
            svc(
                name="Amazon Rekognition",
                tagline="Managed computer vision API for image and video analysis.",
                when_to_use="Use Rekognition when you need object, face, moderation, or image analysis without training a custom vision system first.",
                deep_dive="Rekognition provides ready-made computer vision capabilities for common tasks such as label detection, face analysis, unsafe content moderation, and video analysis. It accelerates delivery when the use case fits its pretrained capabilities. If domain-specific accuracy needs or custom model behavior become critical, the team may eventually move toward custom ML workflows.",
                variations=[
                    "Image analysis and video analysis APIs.",
                    "Labels, faces, moderation, text, and other detection capabilities depending on the API.",
                    "Batch and event-triggered processing patterns using S3 and Lambda.",
                ],
                use_cases=[
                    "Content moderation, media tagging, search enrichment, identity verification assistance, and simple vision automation.",
                    "Analyzing images uploaded by users or media pipelines.",
                    "Reducing manual review effort for visual assets.",
                ],
                properties=[
                    "Pretrained API rather than full custom model platform.",
                    "Fast to integrate for many common vision tasks.",
                    "Output quality depends on image quality and domain fit.",
                ],
                advantages=[
                    "Quick time-to-value for standard vision tasks.",
                    "No model training infrastructure needed for common use cases.",
                    "Easy integration into event-driven pipelines.",
                ],
                disadvantages=[
                    "Limited control compared with custom vision models.",
                    "Human review is still necessary for sensitive use cases.",
                    "Accuracy may not fit every industry or edge case.",
                ],
                implementation_notes=[
                    "Use confidence thresholds carefully and include human review where business risk is high.",
                    "Store raw evidence and decisions for auditability in moderation workflows.",
                    "Benchmark with representative domain images before launch.",
                ],
                comparison=[
                    ("Rekognition vs SageMaker custom vision", "Choose Rekognition for quick pretrained tasks; choose SageMaker when custom accuracy or custom classes are needed."),
                    ("Rekognition vs Textract", "Rekognition is for image understanding broadly; Textract is for document text and structure extraction."),
                ],
                code_title="Example: detect labels",
                code="""aws rekognition detect-labels \
  --image '{"S3Object":{"Bucket":"media-bucket","Name":"uploads/photo.jpg"}}' \
  --max-labels 10 \
  --min-confidence 80""",
            ),
            svc(
                name="Amazon Comprehend",
                tagline="Managed NLP service for extracting meaning, entities, sentiment, and classification from text.",
                when_to_use="Use Comprehend when you need NLP capabilities without building your own language models first.",
                deep_dive="Comprehend provides managed text analytics such as entity extraction, sentiment analysis, key phrases, syntax, topic modeling, and classification patterns. It is especially useful for support tickets, reviews, documents, and textual metadata enrichment. Like other pretrained AI services, its value depends on whether the business problem aligns with what the API can reliably infer.",
                variations=[
                    "Entity detection, sentiment analysis, key phrase extraction, classification, and PII detection features.",
                    "Synchronous text analysis and asynchronous batch jobs.",
                    "Custom classification/entity models in supported workflows.",
                ],
                use_cases=[
                    "Support ticket routing, customer feedback analysis, document enrichment, and compliance scanning for PII.",
                    "Tagging large text collections for search or analytics.",
                    "Adding language intelligence to apps quickly.",
                ],
                properties=[
                    "Task-focused NLP API with optional customization in some areas.",
                    "Works well on moderate-scale text enrichment pipelines.",
                    "Should be validated against domain vocabulary and edge cases.",
                ],
                advantages=[
                    "Fast path to useful NLP features.",
                    "No heavy model ops required for common language tasks.",
                    "Can unlock analytics value from text that would otherwise stay unstructured.",
                ],
                disadvantages=[
                    "Pretrained behavior may miss domain nuance or jargon.",
                    "Sensitive business decisions still need human or domain-specific checks.",
                    "Not a replacement for broad custom LLM/NLP platforms when requirements expand.",
                ],
                implementation_notes=[
                    "Test with real domain text, not only clean sample sentences.",
                    "Keep confidence handling and fallback behavior explicit.",
                    "Use PII detection in broader governance workflows, not as a lone control.",
                ],
                comparison=[
                    ("Comprehend vs custom NLP in SageMaker", "Choose Comprehend for managed NLP tasks; choose SageMaker for custom model behavior."),
                    ("Comprehend vs Lex", "Comprehend analyzes text meaning; Lex builds conversational bots."),
                ],
                code_title="Example: detect sentiment",
                code="""aws comprehend detect-sentiment \
  --language-code en \
  --text "The checkout flow was smooth, but delivery was late."
""",
            ),
            svc(
                name="Amazon Lex",
                tagline="Managed conversational AI service for chatbots and voice bots.",
                when_to_use="Use Lex when you need intent-based conversational interfaces integrated with backend logic.",
                deep_dive="Lex helps build conversational bots by managing intents, utterances, slots, prompts, and integrations with Lambda or backend services. It is strong when the conversation space is structured enough to model explicitly. It becomes less attractive when the use case needs broad open-ended reasoning rather than bounded task completion.",
                variations=[
                    "Text and voice bot interactions.",
                    "Intent, slot, and prompt models for task-focused dialogs.",
                    "Lambda-backed fulfillment and validation flows.",
                ],
                use_cases=[
                    "Customer support bots, internal helpdesk bots, booking workflows, and guided self-service tasks.",
                    "Voice interfaces tied to explicit business intents.",
                    "Chat experiences where deterministic workflow matters.",
                ],
                properties=[
                    "Intent-centric conversational design rather than open-ended generation.",
                    "Good fit for task completion and structured bot flows.",
                    "Integrates with backend automation to complete actions.",
                ],
                advantages=[
                    "Managed path to deploy conversational interfaces.",
                    "Useful for bounded support and task workflows.",
                    "Voice and text support in one service family.",
                ],
                disadvantages=[
                    "Conversation design still takes real UX effort.",
                    "Weak fit for open-domain generative conversation needs.",
                    "Rigid intent modeling can become cumbersome as use cases sprawl.",
                ],
                implementation_notes=[
                    "Keep bot scope narrow and goal-oriented.",
                    "Use human escalation paths for ambiguous or high-risk interactions.",
                    "Instrument fallback intents heavily to learn where the bot fails users.",
                ],
                comparison=[
                    ("Lex vs Comprehend", "Lex runs conversations; Comprehend analyzes text."),
                    ("Lex vs custom LLM chatbot", "Choose Lex for structured workflows and predictable intent handling."),
                ],
                code_title="Example: bot intent concept",
                code="""Intent: TrackOrder
Slots:
  - orderId
Fulfillment:
  -> Lambda looks up order status
Response:
  -> "Order 123 is out for delivery." """,
            ),
            svc(
                name="Amazon Polly",
                tagline="Text-to-speech service for generating lifelike spoken audio.",
                when_to_use="Use Polly when applications need synthesized speech output for accessibility, IVR, or voice experiences.",
                deep_dive="Polly turns text into spoken audio using a range of voice options and speech features. It is useful for accessibility, alerts, e-learning, telephony prompts, and voice-enabled applications. The real design question is less about the API call and more about tone, pronunciation handling, caching strategy, and whether generated audio should be produced on demand or pre-rendered.",
                variations=[
                    "Multiple voice types and language options depending on region and feature set.",
                    "On-demand synthesis and cached generated audio patterns.",
                    "Speech markup support for pronunciation and pacing control.",
                ],
                use_cases=[
                    "Accessibility narration, IVR prompts, e-learning, notifications, and spoken assistants.",
                    "Generating audio versions of written content.",
                    "Reducing reliance on prerecorded human voice assets for dynamic content.",
                ],
                properties=[
                    "Speech synthesis API, not a full conversational platform.",
                    "Output quality can be shaped with SSML and post-processing choices.",
                    "Works well in serverless media-generation pipelines.",
                ],
                advantages=[
                    "Easy to add speech output to applications.",
                    "Good for dynamic content where prerecorded audio is impractical.",
                    "Supports many accessibility and voice UX patterns.",
                ],
                disadvantages=[
                    "May still sound synthetic depending on content and voice choice.",
                    "Pronunciation tuning is sometimes necessary.",
                    "Voice experience quality depends heavily on product design, not only the API.",
                ],
                implementation_notes=[
                    "Use SSML for pronunciation, pauses, and emphasis where needed.",
                    "Cache commonly generated phrases or files to reduce repeated synthesis cost.",
                    "Review accessibility requirements with actual users.",
                ],
                comparison=[
                    ("Polly vs Lex", "Polly generates speech; Lex manages bot conversations."),
                    ("Polly vs prerecorded audio", "Choose Polly when content is dynamic or multilingual at scale."),
                ],
                code_title="Example: synthesize speech",
                code="""aws polly synthesize-speech \
  --output-format mp3 \
  --voice-id Joanna \
  --text "Your report is ready for download." \
  output.mp3""",
            ),
            svc(
                name="Amazon Textract",
                tagline="Managed document understanding service for text, forms, and table extraction.",
                when_to_use="Use Textract when you need to extract structured information from scanned or digital documents at scale.",
                deep_dive="Textract goes beyond OCR by identifying forms, tables, key-value pairs, and document structure. It is valuable for invoice processing, identity documents, statements, claims, and records modernization. The real system design work sits around confidence thresholds, human review, exception handling, and downstream workflow integration, not just document parsing.",
                variations=[
                    "Synchronous analysis for small documents and asynchronous jobs for larger workloads.",
                    "Plain text OCR, table extraction, form extraction, and specialized document patterns depending on API choice.",
                    "Human-review pipelines in sensitive automation scenarios.",
                ],
                use_cases=[
                    "Invoice extraction, onboarding documents, compliance archives, and document digitization.",
                    "Turning PDF/image records into searchable structured data.",
                    "Reducing manual data entry from forms and paperwork.",
                ],
                properties=[
                    "Document AI service focused on extraction rather than storage or workflow.",
                    "Works best when paired with human validation for business-critical fields.",
                    "Quality depends on document quality, layout variation, and domain complexity.",
                ],
                advantages=[
                    "Accelerates document processing dramatically versus manual entry.",
                    "Extracts more structure than simple OCR alone.",
                    "Fits event-driven workflows well.",
                ],
                disadvantages=[
                    "Not all documents are clean or consistent enough for full automation.",
                    "Field-level validation and exception handling are still required.",
                    "Poor scan quality can materially reduce usefulness.",
                ],
                implementation_notes=[
                    "Separate low-risk straight-through processing from exception-review workflows.",
                    "Store extracted confidence and source references for audits.",
                    "Benchmark across all real document layouts, not just the easiest examples.",
                ],
                comparison=[
                    ("Textract vs Rekognition text detection", "Textract is purpose-built for documents and structure extraction."),
                    ("Textract vs manual OCR pipelines", "Textract reduces custom pipeline work but still needs business validation design."),
                ],
                code_title="Example: analyze a document",
                code="""aws textract analyze-document \
  --document '{"S3Object":{"Bucket":"docs-bucket","Name":"invoice-1001.pdf"}}' \
  --feature-types TABLES FORMS""",
            ),
        ],
    ),
    Category(
        name="Migration",
        intro="Migration services help organizations move data, applications, and protocols into AWS with less disruption. The real question is not only how to move the workload, but how much modernization should happen during or after the move.",
        services=[
            svc(
                name="AWS Database Migration Service",
                tagline="Managed database migration and replication service for moving data between database engines with low downtime.",
                when_to_use="Use DMS when data must move into AWS with minimal application downtime and the source system must stay running during migration.",
                deep_dive="DMS supports homogeneous and heterogeneous database migration by continuously replicating changes from source to target. It is often paired with schema conversion tooling or manual schema work for heterogeneous moves. DMS is best treated as a migration data plane, not as a substitute for validating schema design, data quality, or application query compatibility on the target side.",
                variations=[
                    "Homogeneous and heterogeneous database migrations.",
                    "One-time migration, ongoing replication, and CDC-based cutover patterns.",
                    "Traditional instances and serverless-style options in supported contexts.",
                ],
                use_cases=[
                    "Moving Oracle, SQL Server, MySQL, PostgreSQL, and other databases into AWS-managed targets.",
                    "Low-downtime database migrations and replication feeds.",
                    "Populating analytics platforms from operational databases.",
                ],
                properties=[
                    "Replication-focused migration service rather than schema redesign service.",
                    "Can keep source operational during migration.",
                    "Success depends on testing cutover, constraints, and target performance characteristics.",
                ],
                advantages=[
                    "Reduces downtime during database migration.",
                    "Supports many source and target combinations.",
                    "Useful for both migration and ongoing replication patterns.",
                ],
                disadvantages=[
                    "Schema conversion and application compatibility still require real effort.",
                    "Migration validation is not optional just because replication succeeded.",
                    "Operational tuning may be needed for large-scale or high-change-rate systems.",
                ],
                implementation_notes=[
                    "Run parallel validation queries and application tests before cutover.",
                    "Benchmark target performance separately from migration success.",
                    "Keep rollback criteria explicit for production migration weekends.",
                ],
                comparison=[
                    ("DMS vs export/import", "Choose DMS for lower downtime and ongoing replication needs."),
                    ("DMS vs DataSync", "DMS migrates database changes; DataSync moves file/object data."),
                ],
                code_title="Example: DMS migration flow",
                code="""Source database -> DMS replication instance/task -> Aurora PostgreSQL target

Cutover steps:
1. Full load
2. Ongoing CDC
3. Application validation
4. Final switch""",
            ),
            svc(
                name="AWS Application Migration Service",
                tagline="Lift-and-shift server migration service for replicating source machines into AWS.",
                when_to_use="Use Application Migration Service when the goal is rehosting existing servers into AWS quickly with minimal redesign.",
                deep_dive="Application Migration Service continuously replicates source servers and converts them into launchable EC2 instances for test and cutover. It is useful when business pressure favors migration speed over immediate modernization. The service solves a specific phase of cloud adoption well, but teams should still plan what happens after landing in AWS: hardening, rightsizing, redesign, and managed-service adoption.",
                variations=[
                    "Continuous block-level replication and non-disruptive test launches.",
                    "Cutover waves for batches of servers.",
                    "Rehost-first patterns across Windows and Linux estates.",
                ],
                use_cases=[
                    "Data center exits, VMware migrations, and rehosting legacy apps into AWS.",
                    "Fast movement of server-based workloads with limited redesign time.",
                    "Migration factories handling many application waves.",
                ],
                properties=[
                    "Optimized for speed of migration rather than architectural elegance.",
                    "Moves servers into EC2-centric landing zones.",
                    "Best as part of a broader migration and modernization roadmap.",
                ],
                advantages=[
                    "Accelerates large-scale server migration significantly.",
                    "Reduces manual rehost effort.",
                    "Useful for phased cloud adoption where time matters.",
                ],
                disadvantages=[
                    "Rehosted systems can carry legacy operational debt into AWS.",
                    "Not a substitute for post-migration modernization work.",
                    "May overpreserve inefficient source-system assumptions.",
                ],
                implementation_notes=[
                    "Rightsize after migration rather than cloning waste forever.",
                    "Group migration waves by dependency and rollback logic.",
                    "Treat rehosting as a transition state unless the architecture is already sound.",
                ],
                comparison=[
                    ("Application Migration Service vs rebuild", "Choose the service when speed and compatibility matter more than immediate redesign."),
                    ("Application Migration Service vs containerization", "Use rehost to land fast, then modernize deliberately where justified."),
                ],
                code_title="Example: migration wave plan",
                code="""Wave 1: low-risk internal apps
Wave 2: shared middleware
Wave 3: customer-facing systems
For each wave:
  replicate -> test launch -> dependency validation -> cutover""",
            ),
            svc(
                name="AWS DataSync",
                tagline="Accelerated online data transfer service for moving file and object data between storage systems and AWS.",
                when_to_use="Use DataSync when you need fast, reliable transfer of large data sets between on-premises storage, AWS storage, and some cloud endpoints.",
                deep_dive="DataSync is purpose-built data movement. It handles incremental transfers, verification, scheduling, bandwidth optimization, and metadata handling better than many hand-rolled rsync-style scripts. It is ideal for file migrations, periodic sync, backup movement, and storage consolidation. Unlike Storage Gateway, DataSync is about transfer jobs, not making AWS storage look like a continuously mounted local system.",
                variations=[
                    "Transfers between NFS/SMB/object stores and AWS destinations such as S3, EFS, and FSx.",
                    "Agent-based and service-managed transfer patterns depending on source/target.",
                    "One-time migration and scheduled synchronization jobs.",
                ],
                use_cases=[
                    "NAS migrations, archive ingestion, dataset movement, backup transfers, and periodic sync workflows.",
                    "Moving large on-prem files into S3 or EFS efficiently.",
                    "Hybrid data mobility without custom transfer tooling.",
                ],
                properties=[
                    "Job-oriented data transfer with validation and scheduling.",
                    "Protocol-aware migration rather than application rewrite tooling.",
                    "Useful for both initial migration and repeated sync operations.",
                ],
                advantages=[
                    "Faster and more reliable than many DIY file migration scripts.",
                    "Good validation and operational visibility.",
                    "Supports practical hybrid data movement patterns well.",
                ],
                disadvantages=[
                    "It moves data, not application behavior or semantics.",
                    "Bandwidth, file-count, and metadata planning still matter.",
                    "Not a shared runtime access layer like Storage Gateway.",
                ],
                implementation_notes=[
                    "Run pilot transfers to estimate time and metadata edge cases.",
                    "Plan cutover windows around last-delta synchronization behavior.",
                    "Separate transfer verification from business application validation.",
                ],
                comparison=[
                    ("DataSync vs Storage Gateway", "Choose DataSync for transfer jobs; choose Storage Gateway for ongoing hybrid access."),
                    ("DataSync vs Snow family", "Choose DataSync for online transfer; use offline appliances when network is the bottleneck."),
                ],
                code_title="Example: DataSync task concept",
                code="""Source: on-prem NFS share
Task:
  transfer -> verify -> schedule daily delta
Destination: s3://acme-archive/legacy-files/""",
            ),
            svc(
                name="AWS Transfer Family",
                tagline="Managed file transfer endpoints for SFTP, FTPS, FTP, and AS2-style business file exchange patterns.",
                when_to_use="Use Transfer Family when partners or legacy systems require standard file transfer protocols but you want AWS-managed backend storage.",
                deep_dive="Transfer Family is the service you use when the protocol is the requirement. Many partner integrations, finance workflows, and legacy systems still expect SFTP or related managed file transfer patterns. Transfer Family lets you meet that expectation while landing files into S3 or EFS and layering IAM, logging, and downstream automation on top. It is a modernization bridge that keeps the protocol stable while the backend becomes cloud-native.",
                variations=[
                    "SFTP, FTPS, FTP, and AS2-related managed transfer endpoints depending on supported configuration.",
                    "S3-backed and EFS-backed storage backends.",
                    "Identity integration choices for users and partner access.",
                ],
                use_cases=[
                    "Partner file exchange, B2B workflows, managed inbound/outbound transfers, and regulated transfer channels.",
                    "Replacing self-managed SFTP servers.",
                    "Landing partner files directly into AWS processing pipelines.",
                ],
                properties=[
                    "Protocol compatibility on the front end, cloud storage on the back end.",
                    "Good bridge between partner expectations and modern data pipelines.",
                    "Useful for both inbound and outbound managed transfer scenarios.",
                ],
                advantages=[
                    "Removes the burden of running your own transfer servers.",
                    "Lets partners keep familiar protocols while you modernize storage.",
                    "Integrates well with downstream event-driven AWS workflows.",
                ],
                disadvantages=[
                    "Protocol-driven architecture can preserve legacy exchange habits longer than ideal.",
                    "Still requires user/account lifecycle management for partners.",
                    "Not needed if both sides can already use modern APIs directly.",
                ],
                implementation_notes=[
                    "Use landing buckets or directories by partner and environment for clear separation.",
                    "Automate post-upload validation and ingestion.",
                    "Retire bespoke SFTP servers where Transfer Family can standardize the pattern.",
                ],
                comparison=[
                    ("Transfer Family vs DataSync", "Choose Transfer Family for partner protocol endpoints; choose DataSync for bulk transfer/sync jobs."),
                    ("Transfer Family vs direct API uploads", "Choose APIs when partners can support them; use Transfer Family when protocols are fixed."),
                ],
                code_title="Example: protocol bridge pattern",
                code="""Partner system -> SFTP endpoint on AWS Transfer Family
  -> S3 landing bucket
  -> EventBridge / Lambda validation
  -> ETL or business workflow""",
            ),
        ],
    ),
]


SOURCES = [
    ("AWS Overview of Amazon Web Services", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/introduction.html"),
    ("AWS Compute Services Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/compute-services.html"),
    ("AWS Storage Services Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/storage-services.html"),
    ("AWS Database Services Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/database.html"),
    ("AWS Networking and Content Delivery Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/networking-services.html"),
    ("AWS Security, Identity, and Compliance Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/security-services.html"),
    ("AWS Management and Governance Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/management-governance.html"),
    ("AWS Analytics Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/analytics.html"),
    ("AWS Developer Tools Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/developer-tools.html"),
    ("AWS Machine Learning Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/machine-learning.html"),
    ("AWS Migration and Transfer Overview", "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/migration-services.html"),
    ("Amazon Aurora User Guide Overview", "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html"),
]


def build_markdown() -> str:
    lines: list[str] = []
    lines.append("# AWS Services Deep Reference Book")
    lines.append("")
    lines.append(f"Validated against official AWS overview pages on {AS_OF_DATE}.")
    lines.append("")
    lines.append("## What This Book Covers")
    lines.append("")
    lines.append("This book explains the listed AWS services with a practical architect's lens: what the service is, when to use it, how it differs from nearby services, the main properties to remember, the most common strengths and tradeoffs, and a compact implementation example.")
    lines.append("")
    lines.append("## How To Read This Book")
    lines.append("")
    lines.append("- Use the category introductions to understand the design space.")
    lines.append("- Use each service section when making architecture or interview decisions.")
    lines.append("- Use the comparison notes when multiple AWS services appear to overlap.")
    lines.append("- Use the implementation snippets as starting points, not production-ready final state.")
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
            lines.append(f"**Summary:** {service.tagline}")
            lines.append("")
            lines.append(f"**When to use it:** {service.when_to_use}")
            lines.append("")
            lines.append("**Deep explanation**")
            lines.append("")
            lines.append(service.deep_dive)
            lines.append("")
            lines.append("**Variations and related forms**")
            lines.extend([f"- {item}" for item in service.variations])
            lines.append("")
            lines.append("**Common use cases**")
            lines.extend([f"- {item}" for item in service.use_cases])
            lines.append("")
            lines.append("**Core properties**")
            lines.extend([f"- {item}" for item in service.properties])
            lines.append("")
            lines.append("**Advantages**")
            lines.extend([f"- {item}" for item in service.advantages])
            lines.append("")
            lines.append("**Disadvantages**")
            lines.extend([f"- {item}" for item in service.disadvantages])
            lines.append("")
            lines.append("**Implementation notes**")
            lines.extend([f"- {item}" for item in service.implementation_notes])
            lines.append("")
            lines.append("**Comparison notes**")
            for other, note in service.comparison:
                lines.append(f"- {other}: {note}")
            lines.append("")
            lines.append(f"**{service.code_title}**")
            lines.append("")
            lines.append("```text")
            lines.append(service.code)
            lines.append("```")
            lines.append("")

    lines.append("# Sources")
    lines.append("")
    lines.append(f"The service list and category coverage were validated on {AS_OF_DATE} against these official AWS references:")
    lines.append("")
    for label, url in SOURCES:
        lines.append(f"- {label}: {url}")
    lines.append("")
    return "\n".join(lines)


def styles() -> StyleSheet1:
    sheet = getSampleStyleSheet()
    sheet.add(
        ParagraphStyle(
            name="BookTitle",
            parent=sheet["Title"],
            fontSize=24,
            leading=30,
            textColor=colors.HexColor("#13315c"),
            spaceAfter=18,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="CategoryHeading",
            parent=sheet["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0b5a7a"),
            spaceBefore=12,
            spaceAfter=10,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="ServiceHeading",
            parent=sheet["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1f3c88"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="SectionLabel",
            parent=sheet["Heading3"],
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#444444"),
            spaceBefore=6,
            spaceAfter=4,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Body",
            parent=sheet["BodyText"],
            fontSize=10,
            leading=14,
            spaceAfter=6,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="Small",
            parent=sheet["BodyText"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#555555"),
            spaceAfter=4,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="BulletBody",
            parent=sheet["BodyText"],
            fontSize=10,
            leading=13,
            leftIndent=12,
            bulletIndent=0,
            spaceAfter=3,
        )
    )
    sheet.add(
        ParagraphStyle(
            name="CodeBlock",
            parent=sheet["BodyText"],
            fontName="Courier",
            fontSize=8.3,
            leading=10.2,
            leftIndent=10,
            rightIndent=10,
            spaceBefore=4,
            spaceAfter=8,
            backColor=colors.HexColor("#f5f7fb"),
            borderColor=colors.HexColor("#d9e2ef"),
            borderWidth=0.5,
            borderPadding=6,
        )
    )
    return sheet


def add_bullets(story: list, items: Iterable[str], bullet_style: ParagraphStyle) -> None:
    for item in items:
        story.append(Paragraph(escape(item), bullet_style, bulletText="-"))


def comparison_table(rows: list[tuple[str, str]]) -> Table:
    data = [["Comparison", "Guidance"]]
    data.extend([[left, right] for left, right in rows])
    table = Table(data, colWidths=[1.65 * inch, 4.95 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#13315c")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_pdf() -> None:
    sheet = styles()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=44,
        bottomMargin=44,
        title="AWS Services Deep Reference Book",
        author="OpenAI Codex",
    )

    story: list = []
    story.append(Paragraph("AWS Services Deep Reference Book", sheet["BookTitle"]))
    story.append(Paragraph("A practical reference for architecture, implementation, and comparison decisions.", sheet["Body"]))
    story.append(Paragraph(f"Validated against official AWS overview pages on {AS_OF_DATE}.", sheet["Small"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("What this book is designed to do", sheet["SectionLabel"]))
    story.append(
        Paragraph(
            "This reference explains each requested service in terms that matter during real design and delivery work: where it fits, where it does not, what its important operating characteristics are, what tradeoffs it introduces, and how to start implementing it cleanly.",
            sheet["Body"],
        )
    )
    story.append(Paragraph("Table of contents", sheet["SectionLabel"]))
    for category in CATEGORIES:
        story.append(Paragraph(f"<b>{escape(category.name)}</b>", sheet["Body"]))
        for service in category.services:
            story.append(Paragraph(escape(service.name), sheet["BulletBody"], bulletText="-"))
    story.append(PageBreak())

    for category_index, category in enumerate(CATEGORIES):
        if category_index > 0:
            story.append(PageBreak())
        story.append(Paragraph(escape(category.name), sheet["CategoryHeading"]))
        story.append(Paragraph(escape(category.intro), sheet["Body"]))
        for service in category.services:
            story.append(Paragraph(escape(service.name), sheet["ServiceHeading"]))
            story.append(Paragraph(f"<b>Summary:</b> {escape(service.tagline)}", sheet["Body"]))
            story.append(Paragraph(f"<b>When to use it:</b> {escape(service.when_to_use)}", sheet["Body"]))
            story.append(Paragraph("Deep explanation", sheet["SectionLabel"]))
            story.append(Paragraph(escape(service.deep_dive), sheet["Body"]))

            story.append(Paragraph("Variations and related forms", sheet["SectionLabel"]))
            add_bullets(story, service.variations, sheet["BulletBody"])

            story.append(Paragraph("Common use cases", sheet["SectionLabel"]))
            add_bullets(story, service.use_cases, sheet["BulletBody"])

            story.append(Paragraph("Core properties", sheet["SectionLabel"]))
            add_bullets(story, service.properties, sheet["BulletBody"])

            story.append(Paragraph("Advantages", sheet["SectionLabel"]))
            add_bullets(story, service.advantages, sheet["BulletBody"])

            story.append(Paragraph("Disadvantages", sheet["SectionLabel"]))
            add_bullets(story, service.disadvantages, sheet["BulletBody"])

            story.append(Paragraph("Implementation notes", sheet["SectionLabel"]))
            add_bullets(story, service.implementation_notes, sheet["BulletBody"])

            story.append(Paragraph("Comparison notes", sheet["SectionLabel"]))
            story.append(comparison_table(service.comparison))
            story.append(Spacer(1, 4))
            story.append(Paragraph(escape(service.code_title), sheet["SectionLabel"]))
            story.append(Preformatted(service.code, sheet["CodeBlock"]))

    story.append(PageBreak())
    story.append(Paragraph("Official AWS Sources", sheet["CategoryHeading"]))
    story.append(
        Paragraph(
            f"The category and service names in this book were validated on {AS_OF_DATE} against official AWS overview pages. The explanations in the book are interpretive reference guidance built on top of those official service definitions.",
            sheet["Body"],
        )
    )
    for label, url in SOURCES:
        story.append(Paragraph(f"<b>{escape(label)}</b><br/>{escape(url)}", sheet["Body"]))

    def add_page_number(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        canvas.drawRightString(A4[0] - 40, 24, f"Page {doc.page}")

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main() -> None:
    MARKDOWN_PATH.write_text(build_markdown(), encoding="utf-8")
    build_pdf()
    print(f"Markdown written to: {MARKDOWN_PATH}")
    print(f"PDF written to: {PDF_PATH}")


if __name__ == "__main__":
    main()
