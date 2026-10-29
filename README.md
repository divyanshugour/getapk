# getapk — Claude Code plugin

<p align="center"><img src="website/assets/logo.svg" alt="getapk logo" width="96"></p>

`/getapk <play-store-link>` extracts the APK of an Android app.

```
/getapk https://play.google.com/store/apps/details?id=com.whatsapp
/getapk com.whatsapp --method adb
```

Methods: `adb` (pull from a connected device that has the app; supports split APKs), `mirror` (free apps via APKPure), `auto` (adb, then mirror).
The APK is staged in the system temp dir and delivered in the chat (via `SendUserFile`) rather than saved in your project. Where the client can't attach files, the temp path is shown instead.
Requires Python 3; `adb` for the adb method.

Install locally: `claude --plugin-dir /path/to/getapk`

Use only for apps you have the right to copy. Paid apps are not supported.

## License

MIT, see [LICENSE](LICENSE).

Website: see [`website/`](website/) (static, open `website/index.html`).
