# author        : Luis Merino
# creation Date : 10/03/2024
# Description   : Copy the complete production organization to sandbox using the Azure Devops Python API


from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.identity import IdentityClient
from azure.devops.v6_0.identity.models import Identity
from azure.devops.v6_0.core.models import TeamProjectReference
from azure.devops.v6_0.core import CoreClient
from azure.devops.v6_0.work import WorkItemTrackingClient
from azure.devops.v6_0.git import GitClient
from azure.devops.v6_0.policy import PolicyClient
from azure.devops.v6_0.pipelines import PipelinesClient
from azure.devops.v6_0.boards import BoardsClient
import json
import os
import git

azure_prod_organization    = "XXXXXXXX"
azure_sandbox_organization = "XXXXXXXX"
azure_project_name         = "XXXXXX"
username                   = "dummy-username"

#  azure_devops_url = f"https://dev.azure.com/{azure_organization}"

# Azure DevOps token  
azure_devops_token = os.getenv("API_TOKEN")
combined_pat_token = username + ":" + azure_devops_token


# Azure DevOps organization URL
organization_url = f"https://dev.azure.com/{azure_organization}"

# Personal Access Token (PAT)
personal_access_token = os.getenv("API_TOKEN")

# Sandbox organization name
sandbox_organization = "sandbox_organization_name"

# Initialize Azure DevOps connections
source_credentials = BasicAuthentication('', personal_access_token)
source_connection = Connection(base_url=source_organization_url, creds=source_credentials)

sandbox_credentials = BasicAuthentication('', personal_access_token)
sandbox_connection = Connection(base_url=sandbox_organization_url, creds=sandbox_credentials)

# Initialize the connection
# credentials = BasicAuthentication('', personal_access_token)
# connection = Connection(base_url=organization_url, creds=credentials)

# Core client
core_client = connection.clients.get_core_client()

# Identity client
identity_client = connection.clients.get_identity_client()

# Work item tracking client
wit_client = connection.clients.get_work_item_tracking_client()

# Git client
git_client = connection.clients.get_git_client()

# Policy client
policy_client = connection.clients.get_policy_client()

# Pipelines client
pipelines_client = connection.clients.get_pipelines_client()

# Boards client
boards_client = connection.clients.get_boards_client()

# Get all users in the organization
users = identity_client.read_identities(search_filter='General')

# Get all groups in the organization
groups = identity_client.read_identities(search_filter='Group')

# Get all projects in the organization
projects = core_client.get_projects()

# Create sandbox organization
sandbox_project = core_client.queue_create_project(project_to_create=TeamProjectReference(name=sandbox_organization))

# Copy users, groups, projects, repositories, pipelines, work items, and boards
for user in users:
    identity_client.create_identity(scope_descriptor=sandbox_project.id, create_identity_parameters=user)
for group in groups:
    identity_client.create_identity(scope_descriptor=sandbox_project.id, create_identity_parameters=group)
for project in projects:
    core_client.queue_create_project(project_to_create=TeamProjectReference(name=project.name))

# Copy repositories
repositories = git_client.get_repositories()
for repository in repositories:
    git_client.create_repository(repository_to_create=repository, project=sandbox_project.id)

# Copy pipelines
pipelines = pipelines_client.get_pipelines()
for pipeline in pipelines:
    pipelines_client.create_pipeline(pipeline=pipeline, project=sandbox_project.id)

# Copy work items
work_items = wit_client.get_work_items()
for work_item in work_items:
    wit_client.create_work_item(work_item=work_item, project=sandbox_project.id)

# Copy boards
boards = boards_client.get_boards()
for board in boards:
    boards_client.create_board(board_to_create=board, project=sandbox_project.id)

print("Organization copied to sandbox successfully!")
