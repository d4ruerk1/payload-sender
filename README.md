# Payload Sender

A lightweight, cross-platform GUI tool to send binary files over raw TCP
connections to any listening host — including embedded systems, custom
servers, and homebrew-enabled devices.

## Features

- Simple IP / Port / File interface
- Real-time log tab with copy support
- Multi-language UI (EN, IT, ZH, RU)
- Persistent settings saved via self-modifying script (no external files)
- EULA screen on first launch (must be read in full before accepting)
- Themed accent colors (6 presets, cycle via long-press on ⓘ)
- DPI-aware rendering on Windows
- Compatible with Windows, macOS and Linux

## Requirements

- Python 3.10+
- tkinter (usually bundled with Python)

## Usage

1. Put your target device in payload-listening mode
   (refer to your device's homebrew documentation).
2. Run `Payload_Sender.pyw` with Python.
3. On first launch, scroll through and accept the Terms of Use.
4. Enter the host IP and port (defaults: `192.168.1.100` / `9020`),
   select your payload file and press **SEND**.

## Wire Protocol

The tool opens a raw TCP connection and sends:

1. **8 bytes** — file size as a little-endian unsigned 64-bit integer (`<Q`)
2. **N bytes** — raw file content, streamed in 64 KB chunks

After the transfer, the tool performs a graceful shutdown (`SHUT_WR`) and
waits up to **5 seconds** for an optional response from the server before
reporting success or a timeout warning.

## Settings Persistence

Settings (IP, port, last file, language, accent color, EULA acceptance) are
stored by rewriting the `CFG_DATA` line at the top of the script itself.
No external config file is created. This requires write permission on the
script file at runtime; if the file is read-only the app still runs but
settings will not be saved across sessions.

## Tips

- **Cycle accent color:** long-press (≥ 1.5 s) on the **ⓘ** button.
- **Open GitHub page:** short-click the **ⓘ** button.
- **Switch language:** click the language button (top-right) and select from
  English, Italian, Chinese, Russian.

## Disclaimer

This tool is a generic TCP file transfer client intended for educational
and homebrew development purposes only.
Use it exclusively on hardware you own or are explicitly authorized to access.
The author is not responsible for any misuse, damage, or legal consequence
arising from the use of this software.
Provided "as is", without warranty of any kind.

## Credits

Author: [d4ruerk1](https://github.com/d4ruerk1/payload-sender)

## License

Apache-2.0
