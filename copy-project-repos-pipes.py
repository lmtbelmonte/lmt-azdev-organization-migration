# author        : Luis Merino
# creation Date : 18/01/2024
# Description   : Python script that access the AzDev REST API to copy 
#                 all elements (Identity, User, Group, Project, Wit , Git, Policy , Pipelines
#                 from one org/proyect to another 

""" Identity
    :param str base_url: Service URL
    :param Authentication creds: Authenticated credentials.
"""

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

from azure.devops.v7_0.identity import IdentityClient
from azure.devops.v7_0.identity.models import Identity
from azure.devops.v7_0.core.models import TeamProjectReference
from azure.devops.v7_0.core import CoreClient
from azure.devops.v7_0.git import GitClient
from azure.devops.v7_0.policy import PolicyClient
from azure.devops.v7_0.pipelines import PipelinesClient

import requests
import json
import os

# Prod org 
prod_organization_url = os.getenv("PROD_ORGANIZATION")
prod_project_name     = os.getenv("PROD_PROJECT")
prod_pat              = os.getenv("PROD_PAT")

print(f"Production Org/Project     : {prod_organization_url} / {prod_project_name}")

# Sandbox org 
sandbox_organization_url = os.getenv("SANDBOX_ORGANIZATION")
sandbox_pat              = os.getenv("SANDBOX_PAT")

print(f"SandBox Org/Project        : {sandbox_organization_url}")

# Proxies conf
proxy   = os.getenv("HTTP_PROXY")
proxy_s = os.getenv("HTTPS_PROXY")

prod_credentials = BasicAuthentication('', prod_pat)
prod_connection = Connection(base_url=prod_organization_url, creds=prod_credentials)
sandbox_credentials = BasicAuthentication('', sandbox_pat)
sandbox_connection = Connection(base_url=sandbox_organization_url, creds=sandbox_credentials)

# Init connection
# Core Prod client
core_prod_client = prod_connection.clients.get_core_client()

# Core Sandbox prod client
core_sandbox_client = sandbox_connection.clients.get_core_client()

# Identity prod client
identity_prod_client = prod_connection.clients.get_identity_client()

# Work item prod tracking client
wit_prod_client = prod_connection.clients.get_work_item_tracking_client()

# Git prod client
git_prod_client = prod_connection.clients.get_git_client()

# Policy prod client
policy_prod_client = prod_connection.clients.get_policy_client()

# Pipelines prod client
pipelines_prod_client = prod_connection.clients.get_pipelines_client()

# Pipelines sandbox client
pipelines_sandbox_client = sandbox_connection.clients.get_pipelines_client()

# Get all users in the organization
#users_prod_client = identity_prod_client.read_identities(search_filter='General')
#print(f"Users Prod Client          : {users_prod_client} ")

# Get all groups in the organization
#groups_prod_client = identity_prod_client.read_identities(search_filter='Group')
#print(f"Group Prod Client          : {groups_prod_client} ")

# Get all projects in the Prod organization
projects_prod_client = core_prod_client.get_projects()
#print(f"projects Prod Client       : {projects_prod_client} ")


# Get builds from project in Prod organization
build_prod_client = prod_connection.clients.get_build_client()

# Create Project
#def create_project(project):
#    #for project in projects_prod_client:
#    project_created = core_sandbox_client.queue_create_project(project)
#    print(f"SandBox new Project    :  {project_created}")
#
#    return project_created

def get_project(project):
    #for project in projects_prod_client:
    
    project_get = core_prod_client.get_project(project)
    print(f"Project to get             :  {project_get.description}")

    return project_get.id

# Create Users
#def create_user(project_id):
#    for user in users_prod_client:
#        identity_prod_client.create_identity(scope_descriptor=project_id, create_identity_parameters=user)
#    print(f"SandBox new User:  {user}")
#    
#    return user

# Create Groups
#def create_group(project_id):
#    for group in groups_prod_client:
#        identity_prod_client.create_identity(scope_descriptor=project_id, create_identity_parameters=group)
#    print(f"SandBox new Group:  {group}")
#    
#    return group

# Create repositories
def create_git_repos(project):
    repositories = git_prod_client.get_repositories()
    for repository in repositories:
        git_prod_client.create_repository(repository_to_create=repository, project=project)
    print(f"Sandbox new Git Repo   :  {repository}")
    
    return repository    

# Create pipelines
def create_pipelines(project):
    pipelines = pipelines_prod_client.get_pipelines()
    for pipeline in pipelines:
        pipeline_sandbox = pipelines_sandbox_client.create_pipeline(pipeline=pipeline, project=project)
    
    print(f"SandBox new Pipeline: {pipeline_sandbox}")
    return pipeline_sandbox    

# Create work items
def create_Wit(project_id):
    work_items = wit_prod_client.get_work_items()
    for work_item in work_items:
        wit_prod_client.create_work_item(work_item=work_item, project=project_id)

    print(f"SandBox new Wit: {work_item}")
    return work_item        

# Get all builds for extracting artifacts
def get_builds(project_name):
    builds = build_prod_client.get_builds(project_name)
  
    return builds

# Get build artifacts from prod org
def get_build_artifacts(project_name,build):
    artifacts = build_prod_client.get_artifacts(project_name, build)
  
    return artifacts

# Copy artifacts to sandbox org
def copy_artifacts_to_sandbox(artifacts):
    build_client = sandbox_connection.clients.get_build_client()
    for artifact in artifacts:
        # Get artifact from prod org
        artifact_content = requests.get(artifact.resource.download_url).content
 
        # Publish the artifact to sandbox organization
        build_client.publish_build_artifacts(project=prod_project_name, build_id=artifact.build_id, artifact_name=artifact.name, artifact_stream=artifact_content)

def main():
    # Get Project first from env var
    project_id = get_project(prod_project_name)

    # Get all builds from project
    builds = get_builds(prod_project_name)

    # Get all repos from Project
    repositories = git_prod_client.get_repositories(prod_project_name)
    if repositories:
       for repository in repositories:
           print (f"Repository                 : {repository.name}") 

    # get all builds 
    if builds:
      for build in builds:
        artifacts = get_build_artifacts(prod_project_name,build.id)
        for artifact in artifacts:
          print (f"Build/artifact             : {build.id}/ {artifact.id}")

    # Get all pipelines
    pipelines = pipelines_prod_client.list_pipelines(prod_project_name)
    if pipelines:
       for pipeline in pipelines:
          runs = pipelines_prod_client.list_runs(prod_project_name, pipeline.id)
          if runs:
            for run in runs:  
             print (f"pipeline / run /artifact  : {pipeline.name}:{pipeline.id} / {run.name}:{run.id}")      
    
    # Copy artifacts to sandbox organization
    #copy_artifacts_to_sandbox(artifacts)

if __name__ == "__main__":
    main()
