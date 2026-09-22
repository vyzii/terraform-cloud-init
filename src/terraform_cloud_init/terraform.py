from terraform_cloud_init.config import Config
from terraform_cloud_init.validation import ConfigError, validate

STATE_FILENAME = "default.tfstate"


def build_backend_config_arg(provider: str, backend_path: str) -> str:
    folder = backend_path.strip("/")

    if provider == "gcp":
        return f"prefix={folder}"

    return f"key={folder}/{STATE_FILENAME}"


def build_init_command(cfg: Config) -> list[str]:
    errors = validate(cfg)
    if errors:
        raise ConfigError(errors)

    cmd = ["terraform", "init", "-input=false"]

    if not cfg.init_backend:
        cmd.append("-backend=false")
        return cmd

    if cfg.backend_provider is None or cfg.backend_path is None:
        raise ConfigError(["backend-provider and backend-path are required"])

    arg = build_backend_config_arg(cfg.backend_provider, cfg.backend_path)
    cmd.append(f"-backend-config={arg}")
    return cmd
