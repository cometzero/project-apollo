from __future__ import annotations

import errno
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
    0,
    str(ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib"),
)

from oeqa.controllers import hsocfvp_copy as sparse_copy  # noqa: E402
from oeqa.controllers.hsocfvp_config import (  # noqa: E402
    RuntimeConfigRequest,
    prepare_runtime_config,
)


SPARSE_SIZE = 64 * 1024 * 1024
class FakeLogger:
    def debug(self, message: str, *values: str | Path) -> None:
        assert message
        assert values


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _sparse_file(path: Path, size: int = SPARSE_SIZE) -> None:
    with path.open("wb") as output:
        output.write(b"sparse-head")
        output.seek(size - len(b"sparse-tail"))
        output.write(b"sparse-tail")


def test_prepare_runtime_config_preserves_sparse_wic_extents(
    tmp_path: Path,
) -> None:
    # Given: a product config containing sparse WIC and dense flash inputs.
    deploy = tmp_path / "deploy"
    deploy.mkdir()
    sparse_source = deploy / "product.wic"
    _sparse_file(sparse_source)
    dense_source = deploy / "flash.bin"
    dense_source.write_bytes(b"dense flash payload")
    os.chmod(sparse_source, 0o640)
    os.utime(
        sparse_source,
        ns=(1_700_000_000_000_000_000, 1_700_000_000_000_000_000),
    )
    config = deploy / "product.fvpconf"
    config.write_text(
        json.dumps(
            {
                "parameters": {
                    "ros.flash_loader.fname": str(dense_source),
                    "ros.flash_loader.fnameWrite": str(dense_source),
                    "ros.virtio_block0.image_path": str(sparse_source),
                }
            }
        ),
        encoding="utf-8",
    )
    sparse_hash = _sha256(sparse_source)
    source_stat = sparse_source.stat()
    # When: the controller creates writable runtime images.
    runtime = prepare_runtime_config(
        RuntimeConfigRequest(
            source=config,
            bootlog=tmp_path / "run/logs/default.log",
            logger=FakeLogger(),
        )
    )

    # Then: bytes, metadata, dense data, and sparse allocation all match.
    resolved = json.loads(runtime.read_text(encoding="utf-8"))
    sparse_copy = Path(resolved["parameters"]["ros.virtio_block0.image_path"])
    dense_copy = Path(resolved["parameters"]["ros.flash_loader.fnameWrite"])
    copy_stat = sparse_copy.stat()
    assert copy_stat.st_size == source_stat.st_size
    assert copy_stat.st_blocks <= source_stat.st_blocks + 32
    assert _sha256(sparse_copy) == sparse_hash == _sha256(sparse_source)
    assert copy_stat.st_mode & 0o777 == source_stat.st_mode & 0o777
    assert copy_stat.st_mtime_ns == source_stat.st_mtime_ns
    assert dense_copy.read_bytes() == dense_source.read_bytes()


def test_copy_runtime_file_uses_sparse_content_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: SEEK_DATA is unavailable for a sparse source and destination is stale.
    source = tmp_path / "fallback.wic"
    destination = tmp_path / "runtime/fallback.wic"
    _sparse_file(source, 16 * 1024 * 1024)
    destination.parent.mkdir()
    destination.write_bytes(b"stale partial destination")
    source_hash = _sha256(source)
    source_stat = source.stat()
    original_lseek = sparse_copy.os.lseek

    def unsupported_lseek(file_descriptor: int, offset: int, whence: int) -> int:
        if whence in (os.SEEK_DATA, os.SEEK_HOLE):
            raise OSError(errno.EINVAL, "sparse seek unsupported")
        return original_lseek(file_descriptor, offset, whence)

    monkeypatch.setattr(sparse_copy.os, "lseek", unsupported_lseek)

    # When: the deterministic content-scanning fallback copies the image.
    sparse_copy.copy_runtime_file(source, destination)

    # Then: stale data is replaced without materializing logical holes.
    assert destination.stat().st_size == source_stat.st_size
    assert destination.stat().st_blocks <= source_stat.st_blocks + 32
    assert _sha256(destination) == source_hash == _sha256(source)
    assert list(destination.parent.glob(f".{destination.name}.*.tmp")) == []


def test_copy_runtime_file_preserves_fully_sparse_image(tmp_path: Path) -> None:
    # Given: an image containing no data extents at all.
    source = tmp_path / "empty-extents.wic"
    destination = tmp_path / "runtime/empty-extents.wic"
    with source.open("wb") as output:
        output.truncate(16 * 1024 * 1024)
    source_hash = _sha256(source)

    # When: the extent copier reaches SEEK_DATA ENXIO immediately.
    sparse_copy.copy_runtime_file(source, destination)

    # Then: apparent size and zero contents remain sparse.
    assert destination.stat().st_size == source.stat().st_size
    assert destination.stat().st_blocks <= source.stat().st_blocks + 8
    assert _sha256(destination) == source_hash == _sha256(source)


def test_copy_runtime_file_preserves_dense_bytes_and_metadata(tmp_path: Path) -> None:
    # Given: a normal dense flash file and an old destination.
    source = tmp_path / "flash.bin"
    destination = tmp_path / "runtime/flash.bin"
    source.write_bytes(b"dense payload" * 4096)
    os.chmod(source, 0o604)
    os.utime(
        source,
        ns=(1_710_000_000_000_000_000, 1_710_000_000_000_000_000),
    )
    destination.parent.mkdir()
    destination.write_bytes(b"stale")
    source_hash = _sha256(source)
    source_stat = source.stat()

    # When: the same copier handles a dense input.
    sparse_copy.copy_runtime_file(source, destination)

    # Then: content and copy2-compatible metadata are identical.
    destination_stat = destination.stat()
    assert _sha256(destination) == source_hash == _sha256(source)
    assert destination_stat.st_size == source_stat.st_size
    assert destination_stat.st_mode & 0o777 == source_stat.st_mode & 0o777
    assert destination_stat.st_mtime_ns == source_stat.st_mtime_ns


@pytest.mark.parametrize("error_number", [errno.ENOSPC, errno.EINTR])
def test_copy_runtime_file_cleans_partial_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error_number: int,
) -> None:
    # Given: an existing stale destination and an interrupted extent copy.
    source = tmp_path / "source.bin"
    destination = tmp_path / "runtime/source.bin"
    source.write_bytes(b"source remains immutable" * 4096)
    destination.parent.mkdir()
    destination.write_bytes(b"stale allocated destination")
    source_hash = _sha256(source)

    def fail_extent(*_args: object) -> None:
        raise OSError(error_number, "injected copy failure")

    monkeypatch.setattr(sparse_copy, "_copy_extent", fail_extent)

    # When/Then: failure removes both final and temporary partial copies.
    with pytest.raises(OSError) as failure:
        sparse_copy.copy_runtime_file(source, destination)
    assert failure.value.errno == error_number
    assert not destination.exists()
    assert list(destination.parent.glob(f".{destination.name}.*.tmp")) == []
    assert _sha256(source) == source_hash


def test_copy_runtime_file_rejects_same_path_without_mutation(tmp_path: Path) -> None:
    # Given: source and destination resolve to the same image.
    source = tmp_path / "same.wic"
    source.write_bytes(b"do not modify")
    source_hash = _sha256(source)

    # When/Then: the copy is rejected before unlink or write.
    with pytest.raises(shutil.SameFileError):
        sparse_copy.copy_runtime_file(source, source)
    assert _sha256(source) == source_hash
