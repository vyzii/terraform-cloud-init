from types import SimpleNamespace

import pytest

from terraform_cloud_init.main import run_init, run_validate


class FakeRun:
    def __init__(self, returncode: int = 0):
        self.returncode = returncode
        self.commands = []

    def __call__(self, cmd, **kwargs):
        self.commands.append(cmd)
        return SimpleNamespace(returncode=self.returncode)


@pytest.fixture
def fake_run(monkeypatch):
    fake = FakeRun()
    monkeypatch.setattr("terraform_cloud_init.main.subprocess.run", fake)
    return fake


class TestRunValidate:
    def test_valid_config_returns_zero(self, valid_config, capsys):
        assert run_validate(valid_config("aws")) == 0
        assert "Inputs are valid." in capsys.readouterr().out

    def test_backend_disabled_returns_zero(self, make_config):
        assert run_validate(make_config(init_backend=False)) == 0

    def test_invalid_config_returns_one(self, valid_config, capsys):
        cfg = valid_config("azure", azure_tenant_id=None, backend_path=None)

        assert run_validate(cfg) == 1

        out = capsys.readouterr().out
        assert out.count("::error::") == 2
        assert "azure-tenant-id" in out
        assert "backend-path" in out


class TestRunInit:
    def test_runs_terraform_and_returns_its_exit_code(self, valid_config, fake_run):
        assert run_init(valid_config("aws")) == 0

        assert fake_run.commands == [
            [
                "terraform",
                "init",
                "-input=false",
                "-backend-config=key=myrepo/dev-network/default.tfstate",
            ]
        ]

    def test_propagates_terraform_failure(self, valid_config, fake_run):
        fake_run.returncode = 1

        assert run_init(valid_config("gcp")) == 1

    def test_backend_disabled_runs_without_backend(self, make_config, fake_run):
        assert run_init(make_config(init_backend=False)) == 0

        assert fake_run.commands == [
            ["terraform", "init", "-input=false", "-backend=false"]
        ]

    def test_invalid_config_never_runs_terraform(
        self, valid_config, fake_run, capsys
    ):
        cfg = valid_config("aws", aws_region=None)

        assert run_init(cfg) == 1

        assert fake_run.commands == []
        assert "::error::" in capsys.readouterr().out