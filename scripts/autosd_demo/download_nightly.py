#!/usr/bin/env python3
"""Download/check/unpack an official nightly without requiring guestfish."""
import argparse
import json
import lzma
from pathlib import Path
import shutil
import sys
import tempfile
from urllib.parse import urlparse
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prepare_autosd as prepare


def fetch(output, build_id=None):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    receipt_path = output / "download.json"
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt["requested_build_id"] != build_id:
            raise ValueError("Nightly selection changed; use a new cache directory")
        for path, digest in ((receipt["image"], receipt["image_sha256"]),
                             (receipt["compressed"], receipt["compressed_sha256"])):
            if not Path(path).is_file() or prepare.sha256(Path(path)) != digest:
                raise ValueError(f"Nightly cache missing/corrupt: {path}; use a new cache directory")
        return receipt
    html = ""
    if not build_id:
        with urlopen(prepare.INDEX, timeout=120) as response:
            html = response.read().decode("utf-8")
    url = prepare.select_images(html, ["regular"], build_id)["regular"]
    compressed = output / Path(urlparse(url).path).name
    checksum = output / (compressed.name + ".sha256")
    prepare.download(url + ".sha256", checksum)
    prepare.download(url, compressed)
    digest = prepare.verify_checksum(compressed, checksum.read_text())
    image = compressed.with_suffix("")
    with tempfile.TemporaryDirectory(dir=output) as temporary:
        unpacked = Path(temporary) / "image.qcow2"
        with lzma.open(compressed, "rb") as source, unpacked.open("wb") as target:
            shutil.copyfileobj(source, target, length=8 * 1024 * 1024)
        unpacked.replace(image)
    receipt = {"requested_build_id": build_id, "source_url": url,
               "compressed": str(compressed), "compressed_sha256": digest,
               "image": str(image), "image_sha256": prepare.sha256(image)}
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--build-id")
    args = parser.parse_args()
    print(json.dumps(fetch(args.output, args.build_id), indent=2))


if __name__ == "__main__":
    main()
