# QS browser deployment package

This folder is the complete static preview website. Copy its contents to the document root of a static host; no repository-relative files are required.

This browser version is an experimental try-before-installing experience, not a replacement for the local G2S server. The local server remains the recommended production path and is expected to be roughly 5–10× faster for the current workloads.

The bundled `vendor/lottie.min.js` is lottie-web 5.12.2 under the MIT license; its license is included beside the file.

## Build and copy

From the G2S repository:

```sh
source /path/to/emsdk/emsdk_env.sh
make -C build wasm
cp -R browser/deploy/* /your/static-site/
```

Serve the site over HTTPS in production. The page must send:

- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Embedder-Policy: require-corp`
- `Cross-Origin-Resource-Policy: same-origin`

For local testing, use `python3 browser/serve.py`; it now serves both IPv4 and IPv6 localhost so a generic `python -m http.server` cannot silently shadow the page. Stop any older listener on port 8000 before starting it again.

The page CSP must allow `http://127.0.0.1:8129` in `connect-src`. Configure Python/MATLAB with the exact deployed origin using `-browserOrigin`; do not use wildcard CORS. The existing Python and MATLAB interfaces remain compatible with `-sa browser`, normal `-j`, progress, cancellation, and the finite communication timeout.

The in-page simulation uses the bundled Stone (200×200 continuous) or Strebelle (250×250 categorical) training image and the compiled QS Wasm worker. Each run generates a new random seed and creates a destination with the selected training image's original dimensions. It does not contact the G2S server.

## Cloudflare Pages

Connect the static-site repository to Cloudflare Pages and publish the directory containing this README as the site root. Use no framework preset, no build command, and `.` as the output directory. The included `_headers` file enables the COOP/COEP headers required by the threaded Wasm bundle. No Pages Function, Worker, API token, environment variable, or service-worker workaround is required.

Keep only one preview tab active when using Python or MATLAB; the page now warns and stands down in duplicate tabs so one command cannot be claimed twice.
