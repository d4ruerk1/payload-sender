# Payload Sender

A lightweight, cross-platform GUI tool to send binary files over raw TCP
connections to any listening host — including embedded systems, custom
servers, and homebrew-enabled devices.

## Features

- Simple IP / Port / File interface
- Real-time log tab with copy support
- Multi-language UI (EN, IT, DE, FR, ZH, JA, RU, AR)
- Persistent settings saved locally in JSON
- Themed accent colors
- Compatible with Windows, macOS and Linux

## Requirements

- Python 3.10+
- tkinter (usually bundled with Python)

## Usage

1. Put your target device in payload-listening mode
   (refer to your device's homebrew documentation).
2. Run `Payload_Sender.pyw` with Python.
3. Enter the host IP and port, select your payload file and press **SEND**.

## Disclaimer

This tool is a generic TCP file transfer client intended for educational
and homebrew development purposes only.
Use it exclusively on hardware you own or are explicitly authorized to access.
The author is not responsible for any misuse, damage, or legal consequence
arising from the use of this software.
Provided "as is", without warranty of any kind.

## License

Apache-2.0
