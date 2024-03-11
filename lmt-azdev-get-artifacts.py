from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.build.models import BuildArtifactResource
import requests
import json

# Production organization details
prod_organization_url = "https://dev.azure.com/your-production-org"
prod_project_name = "YourProjectName"
prod_pat = "your_production_personal_access_token"

# Sandbox organization details
sandbox_organization_url = "https://dev.azure.com/your-sandbox-org"
sandbox_pat = "your_sandbox_personal_access_token"

# Initialize the Azure DevOps connections
prod_credentials = BasicAuthentication('', prod_pat)
prod_connection = Connection(base_url=prod_organization_url, creds=prod_credentials)

sandbox_credentials = BasicAuthentication('', sandbox_pat)
sandbox_connection = Connection(base_url=sandbox_organization_url, creds=sandbox_credentials)

# Get list of build artifacts from production organization
def get_build_artifacts(project_name):
    build_client = prod_connection.clients.get_build_client()
    artifacts = build_client.get_artifacts(project=project_name)

    return artifacts

# Copy artifacts to sandbox organization
def copy_artifacts_to_sandbox(artifacts):
    build_client = sandbox_connection.clients.get_build_client()
    for artifact in artifacts:
        # Download the artifact from production organization
        artifact_content = requests.get(artifact.resource.download_url).content

        # Publish the artifact to sandbox organization
        build_client.publish_build_artifacts(project=prod_project_name, build_id=artifact.build_id, artifact_name=artifact.name, artifact_stream=artifact_content)

def main():
    # Get artifacts from production organization
    artifacts = get_build_artifacts(prod_project_name)

    # Copy artifacts to sandbox organization
    copy_artifacts_to_sandbox(artifacts)

if __name__ == "__main__":
    main()
