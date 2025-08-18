"""SPZ loader that loads the native library and exposes decompression.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import platform
from pathlib import Path
from typing import Optional


class SPZError(RuntimeError):
    pass


class SPZLoader:
    """Class that loads the native SPZ library and exposes decompression.

    Provides the `decompress` instance method. The constructor accepts either
    a path to a specific library file, a directory containing platform-
    specific variants, or `None` to search the package directory and system
    library paths.
    """

    def __init__(self, library_path: Optional[str] = None):
        self._lib: Optional[ctypes.CDLL] = None
        lib_path = self._resolve_library_path(library_path)
        self._lib = ctypes.CDLL(lib_path)

        # decompress_spz: int decompress_spz(const uint8_t *input, int inputSize,
        #                                     int includeNormals, uint8_t **outputPtr,
        #                                     int *outputSize)
        try:
            self._lib.decompress_spz.restype = ctypes.c_int
            self._lib.decompress_spz.argtypes = [
                ctypes.c_void_p,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)),
                ctypes.POINTER(ctypes.c_int),
            ]
        except AttributeError as e:
            raise RuntimeError("Loaded SPZ library missing 'decompress_spz' symbol") from e

        self._lib.get_error_string_spz.restype = ctypes.c_char_p
        self._lib.get_error_string_spz.argtypes = [ctypes.c_int]

        self._lib.free_buffer_spz.restype = None
        self._lib.free_buffer_spz.argtypes = [ctypes.POINTER(ctypes.c_uint8)]

    def _resolve_library_path(self, library_path: Optional[str]) -> str:
        pkg_dir = Path(__file__).resolve().parent
        system = platform.system()
        machine = platform.machine().lower()

        # If the user provided a specific path, prefer it (validate exists)
        if library_path:
            p = Path(library_path)
            if p.exists():
                # If a directory was passed, search inside it using platform rules
                if p.is_dir():
                    return self._search_candidates_in_dir(p, system, machine)
                return str(p)
            # if provided path doesn't exist, raise
            raise FileNotFoundError(f"Provided library path does not exist: {library_path}")

        # No explicit path: search package directory for platform specific names
        return self._search_candidates_in_dir(pkg_dir, system, machine)

    def _search_candidates_in_dir(self, directory: Path, system: str, machine: str) -> str:
        candidates = []
        is_arm = any(x in machine for x in ("arm64", "aarch64", "arm"))

        if system == "Windows":
            candidates.append(directory / "spz_shared.dll")
        elif system == "Darwin":
            # macOS supports Apple Silicon only
            if not is_arm:
                raise FileNotFoundError(
                    "Only Apple Silicon macOS builds are supported (libspz_shared.dylib)"
                )
            candidates.append(directory / "libspz_shared.dylib")
        else:
            candidates.append(directory / "libspz_shared.so")

        for p in candidates:
            if p.exists():
                return str(p)

        # fallback to system libs
        found = ctypes.util.find_library("spz") or ctypes.util.find_library("libspz_shared")
        if found:
            return found

        raise FileNotFoundError(f"Could not find a suitable SPZ library in {directory}")

    def _get_error_message(self, code: int) -> str:
        msg = self._lib.get_error_string_spz(code)
        try:
            return msg.decode() if msg is not None else f"Unknown error ({code})"
        except Exception:
            return str(msg)

    def decompress(self, data: bytes, include_normals: bool = False) -> bytes:
        """Decompress `data` using the loaded SPZ library."""
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("data must be bytes or bytearray")

        input_buf = ctypes.create_string_buffer(data)
        input_ptr = ctypes.cast(input_buf, ctypes.c_void_p)

        out_ptr = ctypes.POINTER(ctypes.c_uint8)()
        out_size = ctypes.c_int(0)

        res = self._lib.decompress_spz(
            input_ptr,
            ctypes.c_int(len(data)),
            ctypes.c_int(1 if include_normals else 0),
            ctypes.byref(out_ptr),
            ctypes.byref(out_size),
        )

        if res != 0:
            try:
                if out_ptr and bool(out_ptr.value):
                    self._lib.free_buffer_spz(out_ptr)
            except Exception:
                pass
            raise SPZError(f"decompress failed ({res}): {self._get_error_message(res)}")

        size = int(out_size.value)
        if size <= 0:
            try:
                self._lib.free_buffer_spz(out_ptr)
            except Exception:
                pass
            return b""

        addr = ctypes.cast(out_ptr, ctypes.c_void_p).value
        result = ctypes.string_at(addr, size)

        self._lib.free_buffer_spz(out_ptr)
        return result


def _get_error_message(code: int) -> str:
    """Return an error message for `code` using the global SPZLoader."""
    return get_spz()._get_error_message(code)


def decompress(data: bytes, include_normals: bool = False) -> bytes:
    """Decompress `data` using the global SPZLoader instance.

    This delegates to the `SPZLoader.decompress` instance method.
    """
    return get_spz().decompress(data, include_normals)


__all__ = ["SPZLoader", "SPZError"]

# SPZ global loader instance
_spz_loader_singleton: Optional[SPZLoader] = None


def init_spz(library_path: Optional[str] = None) -> None:
    """Initialize the global SPZLoader once. Safe to call multiple times.

    Args:
        library_path: Optional path or directory where library files live.
    """
    global _spz_loader_singleton
    if _spz_loader_singleton is None:
        _spz_loader_singleton = SPZLoader(library_path)


def get_spz() -> SPZLoader:
    """Return the initialized global SPZLoader. If not initialized, initialize it
    using default search rules (package directory).
    """
    global _spz_loader_singleton
    if _spz_loader_singleton is None:
        init_spz()

    return _spz_loader_singleton
