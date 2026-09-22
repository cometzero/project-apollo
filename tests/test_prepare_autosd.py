from pathlib import Path
import json
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.prepare_autosd import parse_bls, select_images, verify_checksum
from scripts import prepare_autosd


def link(mode, identifier):
    return (f'<a href="https://download.autosd.sig.centos.org/test/'
            f'auto-osbuild-qemu-autosd10-developer-{mode}-aarch64-'
            f'{identifier}.qcow2.xz">image</a>')


def test_select_common_build_and_pin():
    html = (link("regular", "11.abcd") + link("regular", "9.1234")
            + link("ostree", "9.1234") + link("ostree", "8.abcd"))
    images = select_images(html, ["regular", "ostree"], None)
    assert all("9.1234" in url for url in images.values())
    assert "11.abcd" in select_images(html, ["regular"], None)["regular"]
    assert "8.abcd" in select_images(html, ["ostree"], "8.abcd")["ostree"]
    with pytest.raises(ValueError, match="No matching"):
        select_images(link("regular", "11.abcd"), ["regular", "ostree"], None)


def test_pinned_build_does_not_need_index():
    images = select_images("", ["regular", "ostree"], "2869696176.466d2e78")
    assert images["regular"] == (
        "https://download.autosd.sig.centos.org/AutoSD-10/nightly/sample-images/"
        "auto-osbuild-qemu-autosd10-developer-regular-aarch64-"
        "2869696176.466d2e78.qcow2.xz")
    for bad in ("../2869696176.466d2e78", "123", "123.abcdef?query", "12.xyz"):
        with pytest.raises(ValueError, match="Invalid build ID"):
            select_images("", ["regular"], bad)


def test_reject_unexpected_download_domain():
    html = link("regular", "11.abcd").replace("download.autosd.sig.centos.org", "example.com")
    with pytest.raises(ValueError, match="No matching"):
        select_images(html, ["regular"], None)


@pytest.mark.parametrize("initrd", ["/initramfs-6.12.img",
                                  "/boot/ostree/default-abc/initramfs-6.12.img"])
def test_bls_preserves_root_ostree_and_security_options(initrd):
    path, options = parse_bls(
        f"title AutoSD\ninitrd {initrd}\noptions root=UUID=abcd ro "
        "console=tty0 console=ttyS0,115200 rd.modules-load=virtio_pci "
        "quiet rhgb splash loglevel=4 systemd.show_status=auto rd.systemd.show_status=no "
        "ostree=/ostree/boot.1/default/abcd/0 selinux=1 enforcing=0\n")
    assert path == initrd
    assert options == ("root=UUID=abcd ro ostree=/ostree/boot.1/default/abcd/0 "
                       "selinux=1 enforcing=0 console=ttyAMA0 earlycon=pl011,0x1a400000 "
                       "loglevel=7 systemd.show_status=yes rd.systemd.show_status=yes")


@pytest.mark.parametrize("text", ["initrd /x\noptions ro", "options root=UUID=a",
                                  "initrd /../x\noptions root=UUID=a",
                                  "initrd /x\ninitrd /y\noptions root=UUID=a"])
def test_reject_incomplete_or_ambiguous_bls(text):
    with pytest.raises(ValueError):
        parse_bls(text)


def test_checksum_requires_matching_filename_and_content(tmp_path):
    path = tmp_path / "disk.qcow2.xz"
    path.write_bytes(b"abc")
    digest = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert verify_checksum(path, f"{digest}  {path.name}\n") == digest
    assert verify_checksum(path, f"{digest} *{path.name}\n") == digest
    with pytest.raises(ValueError, match="No SHA256 entry"):
        verify_checksum(path, f"{digest}  other-file\n")
    path.write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        verify_checksum(path, f"{digest}  {path.name}\n")


@pytest.mark.parametrize("mode", ["regular", "ostree"])
def test_extract_discovers_root_and_resolves_bls_initrd(monkeypatch, tmp_path, mode):
    source = ("/initramfs-6.12.img" if mode == "regular" else
              "/boot/ostree/default-abc/initramfs-6.12.img")
    actual = "/boot" + source if mode == "regular" else source
    calls = []

    def fake_guestfish(binary, disk, *command, device=None, image_format="qcow2"):
        assert image_format == "qcow2"
        calls.append((command, device))
        if command[0] == "list-filesystems":
            return "/dev/sda1: vfat\n/dev/sda4: ext4\n/dev/sda5: ext4"
        if command[0] == "glob-expand":
            return "" if device == "/dev/sda4" else "/boot/loader/entries/linux.conf"
        assert device == "/dev/sda5"
        if command[0] == "cat":
            return f"initrd {source}\noptions root=UUID=abcd ro"
        if command[0] == "is-file":
            return str(command[1] == actual).lower()
        if command[0] == "download":
            assert command[1] == actual
            Path(command[2]).write_bytes(b"initrd")
            return ""
        raise AssertionError(command)

    monkeypatch.setattr(prepare_autosd, "guestfish", fake_guestfish)
    options, entry, initrd = prepare_autosd.extract_boot(
        "guestfish", tmp_path / "disk.qcow2", tmp_path)
    assert initrd == actual
    assert entry == "/boot/loader/entries/linux.conf"
    assert "root=UUID=abcd" in options
    assert (tmp_path / "initrd.img").read_bytes() == b"initrd"
    assert calls[0] == (("list-filesystems",), None)


def test_guestfish_opens_readonly_and_preserves_environment(monkeypatch, tmp_path):
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return type("Result", (), {"stdout": "true\n"})()

    monkeypatch.setattr(prepare_autosd.subprocess, "run", fake_run)
    prepare_autosd.guestfish("/custom/guestfish", tmp_path / "disk", "is-file",
                            "/boot/initrd", device="/dev/sda5")
    args, kwargs = calls[0]
    assert args == ["/custom/guestfish", "--ro", "--format=qcow2", "-a", str(tmp_path / "disk"),
                    "-m", "/dev/sda5:/:ro", "is-file", "/boot/initrd"]
    assert "env" not in kwargs


def local_tools(monkeypatch, image_format="qcow2", extra_info=None):
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        if args[1] == "info":
            return type("Result", (), {"stdout": json.dumps({"format": image_format, **(extra_info or {})})})()
        assert args[1] == "convert"
        Path(args[-1]).write_bytes(b"converted disk")

    def extract(fish, disk, stage, image_format):
        assert image_format == "raw"
        assert disk.parent == stage
        (stage / "initrd.img").write_bytes(b"original initrd")
        (stage / "entry.conf").write_text("initrd /initrd\noptions root=UUID=test\n")
        return "root=UUID=test console=ttyAMA0", "/boot/loader/entries/test.conf", "/boot/initrd"

    monkeypatch.setattr(prepare_autosd.subprocess, "run", run)
    monkeypatch.setattr(prepare_autosd, "extract_boot", extract)
    monkeypatch.setattr(prepare_autosd, "urlopen", lambda *args, **kwargs: pytest.fail("local image used network"))
    return calls


@pytest.mark.parametrize("image_format", ["raw", "qcow2"])
def test_local_image_provenance_and_source_preserved(tmp_path, monkeypatch, image_format):
    source = tmp_path / "custom.img"
    source.write_bytes(b"local source")
    output = tmp_path / "prepared"
    calls = local_tools(monkeypatch, image_format)
    manifest_path = prepare_autosd.prepare_local("regular", source, output, "guestfish", "qemu-img")
    manifest = json.loads(manifest_path.read_text())
    assert source.read_bytes() == b"local source"
    assert manifest["source_sha256"] == prepare_autosd.sha256(source)
    assert manifest["source_path"] == str(source)
    assert manifest["source_kind"] == "local"
    assert manifest["source_format"] == image_format
    assert "source_url" not in manifest and "checksum_url" not in manifest
    assert manifest["rootfs_sha256"] == prepare_autosd.sha256(Path(manifest["rootfs"]))
    assert Path(manifest["rootfs"]).stat().st_nlink == 1
    assert calls[1][2:6] == ["-f", image_format, "-O", "raw"]


@pytest.mark.parametrize("collision", ["regular.raw", "regular-initrd.img", "regular-entry.conf", "regular.json"])
def test_local_image_never_overwrites_existing_artifact(tmp_path, monkeypatch, collision):
    source = tmp_path / "custom.raw"
    source.write_bytes(b"source")
    output = tmp_path / "output"
    output.mkdir()
    existing = output / collision
    existing.write_bytes(b"preserved")
    calls = local_tools(monkeypatch)
    with pytest.raises(ValueError, match="already exist"):
        prepare_autosd.prepare_local("regular", source, output, "guestfish", "qemu-img")
    assert existing.read_bytes() == b"preserved"
    assert not calls


@pytest.mark.parametrize("image_format,extra", [("vmdk", {}), ("qcow2", {"backing-filename": "base.qcow2"}),
    ("qcow2", {"format-specific": {"data": {"data-file": "external.raw"}}})])
def test_local_rejects_unsupported_or_backed_images(tmp_path, monkeypatch, image_format, extra):
    source = tmp_path / "custom.img"
    source.touch()
    calls = local_tools(monkeypatch, image_format, extra)
    with pytest.raises(ValueError, match="self-contained"):
        prepare_autosd.prepare_local("ostree", source, tmp_path / "out", "guestfish", "qemu-img")
    assert len(calls) == 1


def test_local_source_change_does_not_publish_manifest(tmp_path, monkeypatch):
    source = tmp_path / "custom.raw"
    source.touch()
    local_tools(monkeypatch, "raw")
    original = prepare_autosd.sha256
    count = 0

    def changed(path):
        nonlocal count
        if path == source:
            count += 1
            return str(count)
        return original(path)

    monkeypatch.setattr(prepare_autosd, "sha256", changed)
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="changed during"):
        prepare_autosd.prepare_local("regular", source, output, "guestfish", "qemu-img")
    assert not list(output.iterdir())


@pytest.mark.parametrize("extra", [[], ["--mode", "all"], ["--mode", "regular", "--build-id", "123.abcd"]])
def test_local_cli_requires_explicit_mode_without_build_id(monkeypatch, extra):
    monkeypatch.setattr(sys, "argv", ["prepare_autosd.py", "--image", "custom.raw", *extra])
    with pytest.raises(SystemExit) as error:
        prepare_autosd.main()
    assert error.value.code == 2


def test_local_cli_skips_nightly_index(tmp_path, monkeypatch):
    source = tmp_path / "custom.raw"
    source.write_bytes(b"source")
    local_tools(monkeypatch, "raw")
    monkeypatch.setattr(prepare_autosd.shutil, "which", lambda binary: binary)
    monkeypatch.setattr(sys, "argv", ["prepare_autosd.py", "--image", str(source),
                                    "--mode", "ostree", "--output", str(tmp_path / "out")])
    prepare_autosd.main()
    assert (tmp_path / "out/ostree.json").is_file()


def test_guestfish_raw_format_is_explicit(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(prepare_autosd.subprocess, "run", lambda args, **kwargs:
                        (calls.append(args) or type("Result", (), {"stdout": ""})()))
    prepare_autosd.guestfish("guestfish", tmp_path / "copy.raw", "list-filesystems", image_format="raw")
    assert "--format=raw" in calls[0] and "--ro" in calls[0]
