from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.core.models import TeamProject
from azure.devops.v6_0.core.models import TeamProjectCreateParameters

# Replace these variables with your Azure DevOps organization URL and personal access token
organization_url = "https://dev.azure.com/your_organization"
personal_access_token = "your_personal_access_token"

# Create a connection to Azure DevOps using personal access token authentication
credentials = BasicAuthentication('', personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Get a client to interact with the Projects API
project_client = connection.clients.get_project_client()

# Define parameters for creating a new project
new_project_name = "New_Project"
new_project_description = "This is a new project created via Azure DevOps Python API"
new_project_capabilities = {
    "versioncontrol": {"sourceControlType": "Git"},
    "processTemplate": {"templateTypeId": "6b724908-ef14-45cf-84f8-768b5384da45"}  # Default Agile process template
}

# Create a new project
project_parameters = TeamProjectCreateParameters(
    name=new_project_name,
    description=new_project_description,
    capabilities=new_project_capabilities
)
created_project = project_client.create_project(project_parameters)

print(f"Project '{created_project.name}' created successfully under organization '{organization_url}'.")
