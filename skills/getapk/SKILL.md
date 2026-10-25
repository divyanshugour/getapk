---
name: getapk
description: Extract the APK of an Android app from its Google Play Store link or package id. Use when the user runs /getapk, pastes a play.google.com/store/apps/details?id=... link and wants the APK, or asks to download/pull/extract an APK.
---

# getapk

Turns a Play Store link into an APK file on disk.

## Steps

1. Get the link (`https://play.google.com/store/apps/details?id=<package>`) or a bare package id. The package id is the `id=` query parameter.
2. Run the helper (output defaults to `./apks`):
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/getapk.py" "<link>" [--out DIR] [--method auto|adb|mirror] [--serial SERIAL]
   ```
3. Report the saved path(s) and size. If several files were saved it is a split APK (base + config splits); tell the user to install with `adb install-multiple`.

## How it works

- **adb** (preferred, most reliable): `adb shell pm path <pkg>` then `adb pull`. Requires a connected device/emulator (USB debugging on) that already has the app installed. Handles split APKs. Check with `adb devices`.
- **mirror**: downloads the latest APK of a *free* app from the public APKPure endpoint. Used as fallback in `auto` mode.

## Troubleshooting

- `adb not found` → install Android platform-tools.
- `app is not installed` → install it from Play Store on the device first, or use `--method mirror`.
- Mirror failure / non-APK response → the app is likely paid, region-locked, or removed; use the adb method.
- Network errors in sandboxed environments → the mirror host may be blocked; use adb.

## Boundaries

Only use this for apps the user has the right to copy (their own apps, free apps, security research on apps they are permitted to analyze). Do not help circumvent payment, licensing or DRM: refuse to fetch paid apps via cracked/mirror sources, and don't modify or repackage APKs to bypass protections.
