import pytest

from terraform_cloud_init.config import Config

PROVIDER_INPUTS = {
    "aws": {
        "aws_region": "us-east-1",
        "aws_role_arn": "arn:aws:iam::123456789012:role/terraform",
    },
    "azure": {
        "azure_client_id": "client-id",
        "azure_tenant_id": "tenant-id",
        "azure_subscription_id": "subscription-id",
    },
    "gcp": {
        "gcp_workload_identity_provider": (
            "projects/1/locations/global/workloadIdentityPools/pool/providers/github"
        ),
        "gcp_service_account": "terraform@my-project.iam.gserviceaccount.com",
    },
}


@pytest.fixture
def make_config():
    def _make(**overrides) -> Config:
        values = {
            "init_backend": True,
            "backend_provider": None,
            "backend_path": None,
            "aws_region": None,
            "aws_role_arn": None,
            "azure_client_id": None,
            "azure_tenant_id": None,
            "azure_subscription_id": None,
            "gcp_workload_identity_provider": None,
            "gcp_service_account": None,
        }
        values.update(overrides)
        return Config(**values)

    return _make


@pytest.fixture
def valid_config(make_config):
    def _valid(provider: str, **overrides) -> Config:
        values = {
            "backend_provider": provider,
            "backend_path": "myrepo/dev-network",
            **PROVIDER_INPUTS[provider],
        }
        values.update(overrides)
        return make_config(**values)

    return _valid
