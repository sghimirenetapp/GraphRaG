# GraphRaG
 
GraphRaG is a project designed to use Neo4j as a graph database for storing and querying complex relationships between operating systems, platforms, and software limits. This setup allows for efficient Graph Q&A capabilities using retrieval-augmented generation (RAG) with Neo4j and an external language model API.
 
## Table of Contents
 
1. [Secret Configuration](#secret-configuration)
2. [Setting Up Neo4j](#setting-up-neo4j)
3. [Pushing Data to Neo4j](#pushing-data-to-neo4j)
4. [Data Import and Constraints](#data-import-and-constraints)
5. [Running Graph Q&A with RAG](#running-graph-q-and-a-with-rag)
 
---
 
## 1. Secret Configuration
 
To store sensitive information, create a `.secrets.toml` file in the project root. This file contains configuration details for Neo4j and the external language model API.
 
### Example `.secrets.toml`
 
```toml
dynaconf_merge = true
 
[mssql]
USERNAME =
PASSWORD =
 
[neo4j]
NEO4J_URI =
NEO4J_USERNAME =
NEO4J_PASSWORD =
 
[azure]
MODEL_API_KEY=
MODEL_ENDPOINT=
EMBEDDING_API_KEY_=
EMBEDDING_ENDPOINT=
```
 
Replace the placeholders with your actual credentials.
 
---
 
## 2. Setting Up Neo4j
 
To set up Neo4j with Docker, follow these steps to configure the database and enable CSV imports.
 
### Steps to Pull and Run the Neo4j Docker Image
 
1. Pull the latest Neo4j Docker image:
 
   ```bash
   docker pull neo4j:latest
   ```
 
2. Run the Neo4j container with the necessary settings:
 
   ```bash
   docker run --name testneo4j -p 7474:7474 -p 7687:7687 \
     -v $HOME/neo4j/data:/data \
     -v $HOME/neo4j/conf:/conf \
     -v $HOME/neo4j/logs:/logs \
     -v $HOME/neo4j/import:/var/lib/neo4j/import \
     -v $HOME/neo4j/plugins:/plugins \
     --env 'NEO4J_PLUGINS=["apoc"]' \
     --env NEO4J_AUTH=neo4j/neo4j123 \
     --env NEO4J_dbms_security_allow__csv__import__from__file__urls=true \
     --env NEO4J_server_directories_import=import \
     --env NEO4J_dbms_memory_transaction_total_max=10G \
     --env NEO4J_server_memory_heap_max__size=4G \
     --env NEO4J_server_memory_pagecache_size=2G \
     neo4j:latest
   ```
 
This setup:
- Exposes Neo4j on ports `7474` (HTTP) and `7687` (Bolt).
- Allows CSV file imports.
- Configures memory limits for improved performance.
 
---
 
## 3. Pushing Data to Neo4j
 
Place your data files in the Neo4j import directory.
 
1. Copy CSV files to the Neo4j import directory:
 
   ```bash
   sudo cp ./filename.csv $HOME/neo4j/import
   ```
 
2. Set permissions:
 
   ```bash
   sudo chmod -R 755 $HOME/neo4j/import/
   sudo chown -R $USER:$USER $HOME/neo4j/import
   ```
 
---
 
## 4. Data Import and Constraints
 
The following command imports data into Neo4j and sets unique constraints on nodes.
 
### Import Data and Set Constraints
 
Run the command below to import data and set constraints:
 
```bash
docker run --interactive --tty --rm \
  --publish=7474:7474 --publish=7687:7687 \
  --volume=$HOME/neo4j/data:/data \
  --volume=$HOME/neo4j/import:/import \
  neo4j:latest bash -c \
  "neo4j-admin database import full --overwrite-destination --verbose \
   --nodes=SoftwareLimits=/import/SoftwareLimits_final.csv \
   --nodes=BoundPlatformOS=/import/BoundPlatformOS_final.csv \
   --nodes=BoundPlatformOSSoftwareLimits=/import/BoundPlatformOSSoftwareLimits_final.csv \
   --nodes=OS=/import/OS_final.csv \
   --relationships=APPLIES_LIMIT=/import/APPLIES_LIMIT.csv \
   --relationships=HAS_BOUNDPLATFORM_OS=/import/HAS_BOUNDPLATFORM_OS.csv \
   --relationships=HAS_BOUND_LIMIT=/import/HAS_BOUND_LIMIT.csv && \
   cypher-shell -u neo4j -p neo4j123 \
   'CREATE CONSTRAINT ON (n:OSFamily) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:OSType) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:MajorOS) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:OS) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:BoundOSAffiliate) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:OSAffiliate) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:PlatformType) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:PlatformFamily) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:PlatformModel) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:PlatformConfig) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:BoundPlatformOS) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:SoftwareLimitType) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:BaseSoftwareLimits) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:SoftwareLimits) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:StorageArchitectureStack) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:SoftwareLimitScope) ASSERT n.id IS UNIQUE; \
    CREATE CONSTRAINT ON (n:BoundPlatformOSSoftwareLimits) ASSERT n.id IS UNIQUE;'"
```
 
This command:
- Imports nodes and relationships.
- Sets unique constraints on specified node labels.
 
---
 
## 5. Running Graph Q&A with RAG
 
To enable question-answering on the graph data, run the `main.py` script. This uses retrieval-augmented generation (RAG) to provide answers to questions based on Neo4j data.
 
### Running `main.py`
 
1. Install required dependencies:
 
   ```bash
   pip install -r requirements.txt
   ```
 
2. Run `main.py`:
 
   ```bash
   python main.py
   ```
  
---
 
## Conclusion
 
With this setup, GraphRaG uses Neo4j for efficient storage and querying of complex relationships, and leverages an external language model API for RAG-based question answering. Use this README as a setup guide and reference for running Graph Q&A with Neo4j.