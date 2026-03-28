# payload-sender
A lightweight, cross-platform GUI tool to send binary payloads over TCP 
to PS4/PS5 consoles running a custom or homebrew-enabled firmware.

## Features
- Simple IP/Port/File interface
- Real-time log tab with copy support
- Multi-language UI (EN, IT, DE, FR, ZH, JA, RU, AR)
- Persistent settings (saved locally in JSON)
- Themed accent colors
- Compatible with Windows and macOS

## Requirements
- Python 3.x
- tkinter (usually bundled with Python)

## Usage
1. Put your PS4/PS5 in a state where it is listening for payloads 
   (e.g. via a supported exploit page on the console's browser).
2. Run `Payload_Sender.pyw` with Python.
3. Enter the console IP, port (default: 9020 for PS4, 9090 for PS5),
   select your `.bin` payload file and press SEND.

## Disclaimer
This tool is intended for educational and homebrew development purposes only.
Use it only on hardware you own. The authors are not responsible for any 
misuse or damage caused by this software.

## License
Apache-2.0
