# author        : Luis Merino
# creation Date : 18/01/2024
# Description   : Python script that access the AzDev REST API to copy 
#                 all elements (Identity, User, Group, Project, Wit , Git, Policy , Pipelines
#                 from one org/proyect to another 


from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

from azure.devops.v7_0.identity import IdentityClient
from azure.devops.v7_0.identity.models import Identity
from azure.devops.v7_0.core.models import TeamProjectReference
from azure.devops.v7_0.core import CoreClient
from azure.devops.v7_1.git import GitClient
from azure.devops.v7_0.policy import PolicyClient
from azure.devops.v7_1.pipelines import PipelinesClient
from azure.devops.v7_1.pipelines.models import (
    Pipeline,
    PipelineConfiguration,
    CreatePipelineConfigurationParameters,
    CreatePipelineParameters
) 
from azure.devops.v7_0.git.models import GitRepositoryCreateOptions
from azure.devops.v7_1.core.models import TeamProjectCollection

import requests
import json
import base64
import os

# Prod org 
prod_organization_url = os.getenv("PROD_ORGANIZATION")
prod_project_name     = os.getenv("PROD_PROJECT")
prod_pat              = os.getenv("PROD_PAT")
prod_pipeline         = "eppo-reference-data"
prod_repo             = "eppo-bulk"

print(f"Production Org/Project       : {prod_organization_url} / {prod_project_name}")

# Sandbox org 
sandbox_organization_url = os.getenv("SANDBOX_ORGANIZATION")
sandbox_pat              = os.getenv("SANDBOX_PAT")
sandbox_project_name     = "CMS Fraud Case"
sandbox_url_project_name = "CMS%20Fraud%20Case"


print(f"SandBox Org/Project          : {sandbox_organization_url} / {sandbox_project_name}")

#azure_devops_url = f"https://dev.azure.com/{azure_organization}/{azure_project_name}"
username            = "dummy-username"
combined_pat_token  = username + ":" + str(sandbox_pat)

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

# Git sandbox client
git_sandbox_client = sandbox_connection.clients.get_git_client()
#print(f"SandBox git           :  {git_sandbox_client}")

# Policy prod client
policy_prod_client = prod_connection.clients.get_policy_client()

# Pipelines prod client
pipelines_prod_client = prod_connection.clients.get_pipelines_client()

# Pipelines sandbox client
pipelines_sandbox_client = sandbox_connection.clients.get_pipelines_client()

# Get core client in the Prod organization
projects_prod_client = core_prod_client.get_projects()

# Get core client in the Sandbox organization
projects_sandbox_client = core_sandbox_client.get_projects()

# Get builds from project in Prod organization
build_prod_client = prod_connection.clients.get_build_client()

# create project with requests 
def create_project_req(project_name, description, visibility):
    endpoint = f"{sandbox_organization_url}/_apis/projects?api-version=7.02-preview.4"
    headers  = {
        "Content-Type" : "application/json",
        "Authorization": b"Basic " + base64.b64encode(combined_pat_token.encode('utf-8'))
    }
    proxies = {
        "http"  : proxy,
        "https" : proxy_s
    }

    params = {
        "name": project_name,
        "description": description,
        "capabilities": {
          "versioncontrol": {
            "sourceControlType": "Git"
          },
          "processTemplate": {
            "templateTypeId": "6b724908-ef14-45cf-84f8-768b5384da45"
          } 
        },
        "visibility": visibility  
    }

    response = requests.post(endpoint, headers=headers, proxies=proxies, json=params)
    project_data = response.json()
    
    if response.status_code == 202:
        print(f"Projet {project_name} Queued successfully for creation.")
        return project_data
    else:
        print(f"Error creating project: {project_name}: {response.status_code} > {response.text}")

def create_repo_req(project,repo):
    
    git_repo = git_prod_client.get_repositories(project)
    repository= next((p for p in git_repo if p.name == repo), None)
          
    if repository:
      projects_sandbox = core_sandbox_client.get_projects()
      project_sand = next((p for p in projects_sandbox if p.name == project), None)
     
      repo_name   = repository.name
      repo_id     = repository.id
      project_id  = project_sand.id
      clone_url = repository.remote_url
     
      #endpoint = f"{sandbox_organization_url}/{project_id}/_apis/git/repositories/{repo_id}/importRequests?api-version=7.1-preview.1"
      endpoint = f"{sandbox_organization_url}/{project_id}/_apis/git/repositories?api-version=7.0"
      headers  = {
          "Content-Type" : "application/json",
          "Authorization": b"Basic " + base64.b64encode(combined_pat_token.encode('utf-8'))
      }
      proxies = {
          "http"  : proxy,
          "https" : proxy_s
      }
    
      data = {
        "name": repo_name,
        "project": {
           "id":  project_id
        }
              
     }

      repo_config_json = json.dumps(data)
     
      response = requests.post(endpoint, headers=headers, proxies=proxies, json=data)
      repository_data = response
      
      if response.status_code == 201:
          print(f"Repository {repository_data} Created successfully.")
          return repository_data
      else:
          print(f"Error creating Repository: {repository_data}   {sandbox_url_project_name}/{repository.name}: {response.status_code} > {response.text}")
    else:
         print(f"Repository Not Found.") 

def clone_repo_req(project,repo):
    
    git_repo = git_sandbox_client.get_repositories(project)
    repository= next((p for p in git_repo if p.name == repo), None)
          
    if repository:
      projects_sandbox = core_sandbox_client.get_projects()
      project_sand = next((p for p in projects_sandbox if p.name == project), None)

      git_prod_repo     = git_prod_client.get_repositories(project)
      repository_prod = next((p for p in git_prod_repo if p.name == repo), None)
     
      repo_name   = repository.name
      repo_id     = repository.id
      project_id  = project_sand.id
      clone_url = repository_prod.remote_url
     
      endpoint = f"{sandbox_organization_url}/{project_id}/_apis/git/repositories/{repo_id}/importRequests?api-version=7.0"
      #endpoint = f"{sandbox_organization_url}/{project_id}/_apis/git/repositories?api-version=7.0"
      headers  = {
          "Content-Type" : "application/json",
          "Authorization": b"Basic " + base64.b64encode(combined_pat_token.encode('utf-8'))
      }
      proxies = {
          "http"  : proxy,
          "https" : proxy_s
      }
    
      
    data = {
       "parameters": {
         "gitSource": {
            "url": clone_url 
          }
        }      
     }
     
    response = requests.post(endpoint, headers=headers, proxies=proxies, json=data)
    repository_data = response
      
    if response.status_code == 201:
        print(f"Repository {repository_data} Cloned uccessfully.")
        return repository_data
    else:
          print(f"Error cloning Repository: {repository_data} {endpoint} {repository.name}: {response.status_code} > {response.text}")

   # else:
    #   print(f"Repository Not Found.")                 

def create_pipeline_req(project_name, url,links, folder, name, id, revision):
    endpoint = f"{sandbox_organization_url}/{sandbox_url_project_name}/_apis/pipelines?api-version=7.0"
    headers  = {
        "Content-Type" : "application/json",
        "Authorization": b"Basic " + base64.b64encode(combined_pat_token.encode('utf-8'))
    }
    proxies = {
        "http"  : proxy,
        "https" : proxy_s
    }
    
    git_repo = git_sandbox_client.get_repositories(project_name)
    repository= next((p for p in git_repo if p.name == name), None)
    pipeline_url    = url 
    pipeline_folder = folder
    pipeline_name   = name
    pipeline_links  = links
    pipeline_id       =  id
    pipeline_revision = revision

    params = {
    "folder": pipeline_folder,
    "name": pipeline_name,
    "configuration":{
        "type":"yaml",
        "path": "azure-pipelines.yml",
        "repository":{
            "id"  : repository.id,
            "type": "azureReposGit",
            "name": repository.name
        }
    }
   }
    
    pipeline_config_json = json.dumps(params)

      
    response = requests.post(endpoint, headers=headers, proxies=proxies, data=pipeline_config_json)
    pipeline_data = response
    print(f"Pipeline data  {params} {headers}")
    
    if response.status_code == 200:
        print(f"Pipeline {pipeline_data} Created successfully for creation.")
        return pipeline_data
    else:
        print(f"Error creating Pipeline: {pipeline_data}   {sandbox_url_project_name}/{pipeline_name}: {response.status_code} > {response.text}")

# Create Project
def create_project(project,description, visibility):
     
    # First verify that the project does not exist in sandbox
    projects_sand = core_sandbox_client.get_projects()
    project_sand = next((p for p in projects_sand if p.name == project), None)
    
    # create project in sandbox
    if not project_sand:
       #new_project = core_sandbox_client.queue_create_project(project,"private")

       new_project = create_project_req(project,description,visibility)
       
       if new_project:    
          print(f"SandBox new Project info     :  {new_project}")
          return new_project
       else:
          print(f"No info of new Project info :  {new_project}")    
          return ""
    else:
       print(f"   WARNING : Project {project_sand.name} Exists in Sandbox")
       return ""

def get_prod_project(project):
    #for project in projects_prod_client:
    
    project_prod_get = core_prod_client.get_project(project)
    #print(f"Prod Project to get         :  {project_prod_get.description}")

    return project_prod_get

def get_sandbox_project(project):
    #for project in projects_prod_client:
    
    project_sandbox_get = core_sandbox_client.get_project(project)
    print(f"Sandbox Project to get      :  {project_sandbox_get.description}")

    return project_sandbox_get


# Create pipelines
def create_pipelines(project):
    pipelines = pipelines_prod_client.list_pipelines(project=project)
    #pipeline = next((p for p in pipelines_prod if p.name == prod_pipeline), None)

# Pipeline 
    if pipelines:
      for pipeline in pipelines:    
        pipeline_id    = pipeline.id
        pipeline_url   = pipeline.url
        pipeline_links = pipeline._links
        pipeline_folder = pipeline.folder
        pipeline_name  =  pipeline.name
        pipeline_revision = pipeline.revision
      
        pipeline_sandbox = create_pipeline_req(project, pipeline_url, pipeline_links, pipeline_folder, pipeline_name,pipeline_id,pipeline_revision )
    
        if pipeline_sandbox:
            print(f"SandBox new Pipeline: {pipeline_sandbox}")
            #return pipeline_sandbox 
        else:
              print(f"ERROR : Creating SandBox new Pipeline: {pipeline_sandbox}")
              return ""

# Create Repos
def create_repositories(project,repo):
          
    repository_sandbox = create_repo_req(project, repo )
    
    if repository_sandbox:
        print(f"SandBox new Repo: {repository_sandbox}")
        return repository_sandbox 
    else:
          print(f"ERROR : Creating SandBox new Repository: {repository_sandbox}")
          return ""    

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
        build_client.publish_build_artifacts(prod_project_name, artifact.build_id, artifact.name, artifact_content)

def main():

    # Extract Info from prod project before creating the new one
    prod_project_info = get_prod_project(sandbox_project_name) 
    if prod_project_info:
       project_prod_name        = prod_project_info.name
       
       project_prod_description = prod_project_info.description
       project_prod_visibility  = prod_project_info.visibility
       
       print (f"Prod Project Info            : {prod_project_name} / {project_prod_description} / {project_prod_visibility}") 
       # Create Project in Sandbox
       new_project_sand = create_project(project_prod_name,project_prod_description,project_prod_visibility)
       #if new_project_sand:
         # print (f"New project Sand        : {new_project_sand}")      
         
   # Get all repos from Prod and create them on sandbox
   # repositories = git_prod_client.get_repositories()

   # if repositories:
   #    for repository in repositories:
   #        repo_to_copy = repository.name
   #        new_repo = create_repositories(project_prod_name, repo_to_copy )
   #        if new_repo:
   #           print (f"New Sand Repository     : {project_prod_name}  {new_repo}") 
   # else:
   #     print (f"No repositories found in project: {project_prod_name} ") 

    # Get all repos from sandbox to be cloned from prod    
    #repositories = git_prod_client.get_repositories()
#
#    if repositories:
#       for repository in repositories:
#           repo_to_clone = repository.name
#           cloned_repo = clone_repo_req(project_prod_name, repo_to_clone )
#           if cloned_repo:
#              print (f"New cloned Repo     : {project_prod_name}  {cloned_repo}") 
#    else:
#        print (f"No repositories found in project: {project_prod_name} ") 
    

  # Get all pipelines
  
        
    if create_pipelines(prod_project_name):
      print (f"Pipelines Created for :  {prod_project_name}")  
    else:
      print (f"ERROR: Creating pipelines for :  {prod_project_name}")      

if __name__ == "__main__":
    main()
