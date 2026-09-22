import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    init_backend: bool
    backend_provider: str | None
    backend_path: str | None
    aws_region: str | None
    aws_role_arn: str | None
    azure_client_id: str | None
    azure_tenant_id: str | None
    azure_subscription_id: str | None
    gcp_workload_identity_provider: str | None
    gcp_service_account: str | None


def fail(message: str) -> None:
    print(f"::error::{message}")
    sys.exit(1)


def get_input(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def get_bool_input(name: str, default: bool) -> bool:
    value = get_input(name)
    if value is None:
        return default

    value = value.lower()
    if value not in ("true", "false"):
        fail(f"{name} must be 'true' or 'false', got '{value}'")
    return value == "true"


def load_config() -> Config:
    return Config(
        init_backend=get_bool_input("INIT_BACKEND", default=True),
        backend_provider=get_input("BACKEND_PROVIDER"),
        backend_path=get_input("BACKEND_PATH"),
        aws_region=get_input("AWS_REGION"),
        aws_role_arn=get_input("AWS_ROLE_ARN"),
        azure_client_id=get_input("AZURE_CLIENT_ID"),
        azure_tenant_id=get_input("AZURE_TENANT_ID"),
        azure_subscription_id=get_input("AZURE_SUBSCRIPTION_ID"),
        gcp_workload_identity_provider=get_input("GCP_WORKLOAD_IDENTITY_PROVIDER"),
        gcp_service_account=get_input("GCP_SERVICE_ACCOUNT"),
    )
