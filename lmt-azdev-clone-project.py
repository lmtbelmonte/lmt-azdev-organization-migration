from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pprint

# Define your personal access token and organizations
personal_access_token = 'YOUR_PERSONAL_ACCESS_TOKEN'
production_organization_url = 'https://dev.azure.com/YOUR_PRODUCTION_ORG'
sandbox_organization_url = 'https://dev.azure.com/YOUR_SANDBOX_ORG'
project_to_copy_name = 'PROJECT_TO_COPY_NAME'

# Connect to production organization
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=production_organization_url, creds=credentials)

# Get project details
core_client = connection.clients.get_core_client()
project_to_copy = core_client.get_project(project_to_copy_name)

# Create project in sandbox organization
sandbox_core_client = Connection(base_url=sandbox_organization_url, creds=credentials).clients.get_core_client()
new_project = sandbox_core_client.queue_create_project(project_to_copy_name)

# Get list of repositories in the project
git_client = connection.clients.get_git_client()
repositories = git_client.get_repositories(project_to_copy.id)

# Clone repositories to sandbox organization
for repo in repositories:
    clone_url = repo.remote_url
    # Replace the production organization URL with the sandbox organization URL
    clone_url = clone_url.replace(production_organization_url, sandbox_organization_url)
    # Clone the repository
    # Here you can use any Git client library to clone the repository, such as GitPython
    # Example:
    # git.Repo.clone_from(clone_url, local_path)



print("Project copied successfully.")
