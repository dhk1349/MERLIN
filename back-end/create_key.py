import os

from google.oauth2 import service_account
import googleapiclient.discovery  # type: ignore

def create_key(service_account_email: str) -> None:
    """Creates a key for a service account."""

    credentials = service_account.Credentials.from_service_account_file(
        filename=os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    service = googleapiclient.discovery.build("iam", "v1", credentials=credentials)

    key = (
        service.projects()
        .serviceAccounts()
        .keys()
        .create(name="projects/-/serviceAccounts/" + service_account_email, body={})
        .execute()
    )

    # The privateKeyData field contains the base64-encoded service account key
    # in JSON format.
    # TODO(Developer): Save the below key {json_key_file} to a secure location.
    #  You cannot download it again later.
    # import base64
    # json_key_file = base64.b64decode(key['privateKeyData']).decode('utf-8')

    if not key["disabled"]:
        print("Created json key")
