from google.cloud import secretmanager_v1


class SecretManagerService:
    def __init__(self, project_id):
        self.project_id = project_id
        self.client = secretmanager_v1.SecretManagerServiceClient()
        
    def access_secret(self,secret_name: str, version_id: str = "latest") -> str:
        """
        Access a secret from Google Secret Manager.
        
        Args:
            project_id (str): Google Cloud project ID
            secret_name (str): Name of the secret to access
            version_id (str): Version of the secret (default: "latest")
        
        Returns:
            str: Secret value
        """
        try:
            # Build the resource name
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version_id}"
            
            # Access the secret version
            response = self.client.access_secret_version(request={"name": name})
            
            # Return the decoded payload
            return response.payload.data.decode('UTF-8')
        
        except Exception as e:
            print(f"Error accessing secret: {e}")
            raise
