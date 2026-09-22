"""Input validation. Pure functions: no I/O, no environment access."""

from terraform_cloud_init.config import Config

REQUIRED = {
    "aws": [
        "aws_region",
        "aws_role_arn",
        "backend_path",
    ],
    "azure": [
        "azure_client_id",
        "azure_tenant_id",
        "azure_subscription_id",
        "backend_path",
    ],
    "gcp": [
        "gcp_workload_identity_provider",
        "gcp_service_account",
        "backend_path",
    ],
}


class ConfigError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def validate(cfg: Config) -> list[str]:
    if not cfg.init_backend:
        return []

    if cfg.backend_provider not in REQUIRED:
        return [
            (
                f"backend-provider must be one of {sorted(REQUIRED)}, "
                f"got {cfg.backend_provider!r}"
            )
        ]

    errors = []
    required_fields = REQUIRED[cfg.backend_provider]

    for field_name in required_fields:
        value = getattr(cfg, field_name)
        if value is None:
            input_name = field_name.replace("_", "-")
            errors.append(
                f"missing required input for {cfg.backend_provider}: {input_name}"
            )

    return errors
