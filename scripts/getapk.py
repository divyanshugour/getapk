#!/usr/bin/env python3
"""Fetch the APK for a Google Play Store link.

Usage: getapk.py <play-store-url-or-package-id> [--out DIR] [--method auto|adb|mirror] [--serial SERIAL]

Methods:
  adb     Pull the installed APK(s) from a USB/emulator device via adb (works for any
          app installed on that device, including split APKs).
  mirror  Download the latest APK of a *free* app from the public APKPure endpoint.
  auto    Try adb first (if a device is connected and has the app), then mirror.
"""
import argparse
import os
import re
import shutil
import subprocess
import tempfile
import sys
import urllib.parse
import urllib.request
import zipfile

PKG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")
UA = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36"


def parse_package(arg: str) -> str:
    arg = arg.strip().strip("<>\"'")
    if PKG_RE.match(arg):
        return arg
    parsed = urllib.parse.urlparse(arg)
    if parsed.netloc and "play.google.com" not in parsed.netloc:
        sys.exit(f"error: not a Google Play link: {arg}")
    pkg = urllib.parse.parse_qs(parsed.query).get("id", [""])[0]
    if not PKG_RE.match(pkg):
        sys.exit("error: could not find a package id (?id=com.example.app) in the link")
    return pkg


def adb(*args, serial=None):
    cmd = ["adb"] + (["-s", serial] if serial else []) + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def via_adb(pkg: str, out: str, serial=None):
    if not shutil.which("adb"):
        return None, "adb not found in PATH"
    r = adb("shell", "pm", "path", pkg, serial=serial)
    paths = [l.split(":", 1)[1].strip() for l in r.stdout.splitlines() if l.startswith("package:")]
    if not paths:
        detail = (r.stderr or r.stdout).strip() or "app is not installed on the connected device"
        return None, f"adb: {detail}"
    dest_dir = os.path.join(out, pkg) if len(paths) > 1 else out
    os.makedirs(dest_dir, exist_ok=True)
    files = []
    for p in paths:
        name = "base.apk" if len(paths) > 1 and p.endswith("/base.apk") else os.path.basename(p)
        if len(paths) == 1:
            name = f"{pkg}.apk"
        dest = os.path.join(dest_dir, name)
        pull = adb("pull", p, dest, serial=serial)
        if pull.returncode != 0:
            return None, f"adb pull failed: {pull.stderr.strip()}"
        files.append(dest)
    return files, None


def via_mirror(pkg: str, out: str):
    url = f"https://d.apkpure.com/b/APK/{pkg}?version=latest"
    os.makedirs(out, exist_ok=True)
    dest = os.path.join(out, f"{pkg}.apk")
    tmp = dest + ".part"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as f:
            shutil.copyfileobj(resp, f)
    except Exception as e:  # network, 403, 404 (paid/unknown app) ...
        if os.path.exists(tmp):
            os.remove(tmp)
        return None, f"mirror download failed: {e}"
    try:
        with zipfile.ZipFile(tmp) as z:
            names = z.namelist()
        ok = "AndroidManifest.xml" in names or any(n.endswith(".apk") for n in names)
    except zipfile.BadZipFile:
        ok = False
    if not ok:
        os.remove(tmp)
        return None, "mirror returned something that is not an APK (app may be paid, region-locked or unavailable)"
    os.replace(tmp, dest)
    return [dest], None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("link", help="Play Store URL or package id")
    ap.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "getapk"),
                    help="staging dir (default: system temp dir, not your project)")
    ap.add_argument("--method", choices=["auto", "adb", "mirror"], default="auto")
    ap.add_argument("--serial")
    a = ap.parse_args()

    pkg = parse_package(a.link)
    print(f"package: {pkg}")
    errors, files = [], None
    if a.method in ("auto", "adb"):
        files, err = via_adb(pkg, a.out, a.serial)
        if err:
            errors.append(err)
    if not files and a.method in ("auto", "mirror"):
        files, err = via_mirror(pkg, a.out)
        if err:
            errors.append(err)
    if not files:
        print("FAILED:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)
    for f in files:
        print(f"saved: {os.path.abspath(f)} ({os.path.getsize(f) / 1e6:.1f} MB)")
    if len(files) > 1:
        print("note: split APK - install with `adb install-multiple <files>`")


if __name__ == "__main__":
    main()
