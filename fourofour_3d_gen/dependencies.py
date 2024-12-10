import subprocess
import sys
import os
from pathlib import Path


def installed() -> bool:
    try:
        import numpy
        import pydantic
        import websocket
        import mixpanel

        return True
    except:
        return False


def install_pip():
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        import ensurepip

        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None)


def install_dependencies_from_requirements():
    env_var = dict(os.environ)
    # ensures pip installs dependencies on blender's python lib folder
    env_var["PYTHONNOUSERSITE"] = "1"

    requirements_path = Path(__file__).resolve().parent / "requirements.txt"

    if not requirements_path.exists():
        raise FileNotFoundError(
            f"requirements.txt not found in {requirements_path.as_posix()}"
        )

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", requirements_path.as_posix()],
        check=True,
        env=env_var,
    )


def install() -> None:
    install_pip()

    install_dependencies_from_requirements()


if __name__ == "__main__":
    if installed():
        print("dependencies installed")
    else:
        install()
