from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.core.models import TeamProjectCreateParameters

# Define your Azure DevOps organization URL and personal access token
organization_url = "https://dev.azure.com/your_organization"
personal_access_token = "your_personal_access_token"

# Create a connection to Azure DevOps
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Create a project with all information and dependencies
def create_project(project_name):
    core_client = connection.clients.get_core_client()
    parameters = TeamProjectCreateParameters(description="Your project description",
                                              visibility="private",  # You can change visibility as needed
                                              capabilities={"versioncontrol": {"sourceControlType": "Git"}})
    new_project = core_client.queue_create_project(parameters, project_name)
    return new_project

# Usage example
new_project = create_project("Your_Project_Name")
print("Project created:", new_project.name)
