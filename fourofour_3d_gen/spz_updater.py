import requests
import platform
import tempfile
import zipfile

from pathlib import Path
from pydantic import BaseModel


class Asset(BaseModel):
    name: str
    browser_download_url: str


class SPZVersionResponse(BaseModel):
    tag_name: str
    assets: list[Asset]


class SPZUpdater:

    _REPOSITORY_URL: str = "https://api.github.com/repos/404-Repo/spz/releases/latest"
    _SPZ_VERSION_FILE: Path = Path(__file__).parent / "spz_version.txt"
    _OS_TO_ASSET_NAME: dict[str, str] = {
        "Windows": "spz-windows.zip",
        "Linux": "spz-linux.zip",
        "Darwin": "spz-macos.zip",
    }
    
    @classmethod
    def update(cls) -> None:
        try:
            latest_version_info = cls._get_latest_version_info()
            current_version = cls._get_current_version()
            print(f"Current SPZ version: {current_version}")
            print(f"Latest SPZ version: {latest_version_info.tag_name}")
            if current_version is None or current_version != latest_version_info.tag_name:
                print(f"Updating SPZ version: ... ")
                cls._download_spz(latest_version_info=latest_version_info)
                cls._write_version(latest_version_info.tag_name)
                print(f"SPZ version updated to {latest_version_info.tag_name}")
        except Exception as e:
            print(f"Error to update spz: {str(e)}")


    @classmethod
    def need_update(cls) -> bool:
        try:
            current_version = cls._get_current_version()
            latest_version_info = cls._get_latest_version_info()
            if current_version is None or current_version != latest_version_info.tag_name:
                return True
            return False
        except Exception as e:
            print(f"Error to check if spz need update: {str(e)}")
            return False
    
    @classmethod
    def _get_current_version(cls) -> str | None:
        if not cls._SPZ_VERSION_FILE.exists():
            return None
        with cls._SPZ_VERSION_FILE.open('r') as f:
            return f.read().strip()

    @classmethod
    def _write_version(cls, version: str) -> None:
        with cls._SPZ_VERSION_FILE.open('w') as f:
            f.write(version)

    @classmethod
    def _get_latest_version_info(cls) -> SPZVersionResponse:
        response = requests.get(cls._REPOSITORY_URL)
        response.raise_for_status()
        data = SPZVersionResponse.model_validate_json(response.text)
        return data

    @classmethod
    def _download_spz(cls, *, latest_version_info: SPZVersionResponse) -> None:
        os_type = platform.system()
        asset_name: str | None  = cls._OS_TO_ASSET_NAME.get(os_type, None)
        if asset_name is None:
            raise ValueError(f"Unknown OS: {os_type}")

        asset = next((asset for asset in latest_version_info.assets if asset.name == asset_name), None)
        if asset is None:
            raise ValueError(f"Asset not found: {asset_name}")

        target_directory: Path = Path(__file__).parent

        # Download the asset to a temporary zip file, then extract to the plugin directory
        temp_file_path: Path = Path(__file__).parent / asset_name
        print(temp_file_path)
        try:
            # Download the file first
            with requests.get(asset.browser_download_url, stream=True, timeout=60) as response:
                response.raise_for_status()
                with temp_file_path.open("wb") as tmp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            tmp_file.write(chunk)
            
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(target_directory)
                
        except Exception as e:
            raise RuntimeError(f"Error to download spz: {str(e)}")
        finally:
            try:
                if temp_file_path.exists():
                    temp_file_path.unlink()
            except Exception:
                pass
