---
description: Extract the APK of an app from its Google Play Store link
argument-hint: <play-store-link> [--out DIR] [--method auto|adb|mirror]
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/getapk.py:*), Bash(adb devices:*), SendUserFile
---

Use the `getapk` skill to fetch the APK for this Play Store link: $ARGUMENTS

If no link was given, ask the user for one. Run the helper script, then send the APK file(s) to the user in the chat with SendUserFile (do not leave them in the project folder), and mention size and any split-APK install note. If it fails, explain why and suggest the fix from the skill.
