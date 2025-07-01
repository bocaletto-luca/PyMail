# PyMail

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE) [![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/bocaletto-luca/PyMail)

A terminal-based email client with IMAP reading, SMTP sending, PGP/GPG inline signing & encryption, attachment handling, folder navigation, search, and a customizable menu interface.

---

## Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Shortcuts & Themes](#shortcuts--themes)  
- [Contributing](#contributing)  
- [License](#license)  
- [Author](#author)  

---

## Overview

**PyMail** is a single-file, interactive CLI application for reading and composing email entirely in your terminal. It leverages:

- **IMAPClient** for folder navigation, threaded message lists, and search  
- **smtplib** for sending new messages with attachments  
- **python-gnupg** for inline PGP/GPG signing and encryption  
- **prompt_toolkit** for menu navigation and customizable keybindings  
- **Rich** for beautiful tables, syntax-highlighted markdown, and notifications  

No GUI required—just your favorite shell, editor, and PGP key.

---

## Features

- **Folder Navigation**: Browse and select any IMAP folder  
- **Threaded View & Search**: List latest messages, search by subject or sender  
- **Compose with Editor**: Draft mail in your `$EDITOR`, add attachments  
- **PGP/GPG Support**: Inline sign or encrypt outgoing messages  
- **Attachment Handling**: Download or upload attachments seamlessly  
- **Customizable Shortcuts**: Define your own key bindings in config  
- **Color Themes**: Select from built-in themes or create your own  
- **Config Persistence**: All settings stored in `~/.config/pyemail/config.yaml`  

---

## Prerequisites

- Python 3.8 or newer  
- A working IMAP account (Gmail, Office365, self-hosted, etc.)  
- A working SMTP account for sending mail  
- GPG (`gnupg`) installed and a keypair available  
- (Optional) A modern terminal with 256-color support  

---

## Installation

```bash
git clone https://github.com/bocaletto-luca/PyMail.git
cd PyMail
pip install -r requirements.txt
chmod +x pymail.py
```

---

## Configuration

On first run, PyMail creates a default config:

```bash
./pymail.py
```

Edit `~/.config/pyemail/config.yaml` to add your settings:

```yaml
# ~/.config/pyemail/config.yaml

imap_host: imap.example.com
imap_port: 993
smtp_host: smtp.example.com
smtp_port: 587

email: user@example.com
gpg_recipient: YOUR_GPG_KEYID

shortcuts:
  quit: q
  back: b

theme: monokai
```

- **imap_host / imap_port**: your IMAP server  
- **smtp_host / smtp_port**: your SMTP server  
- **email**: your email address (used for both IMAP login and SMTP from)  
- **gpg_recipient**: the key ID or fingerprint for signing/encryption  
- **shortcuts**: customize menu keys  
- **theme**: choose a prompt_toolkit color palette  

---

## Usage

```bash
./pymail.py
```

You will be prompted for your account password once per session. Main menu options:

1. **Folders**  
   - Select a folder, view the latest messages  
   - Enter message index to read, download attachments  
2. **Search**  
   - Enter a search term (subject or sender) across a chosen folder  
3. **Compose**  
   - Specify recipient, subject  
   - Edit body in your `$EDITOR`  
   - Add attachments (comma-separated paths)  
   - Optionally sign or encrypt with PGP/GPG  
4. **Quit**  
   - Exit the client  

---

## Shortcuts & Themes

- Define custom keys in your config under `shortcuts`  
- Use one of the bundled themes (e.g. `monokai`, `native`) by setting `theme`  
- To add new themes, modify the prompt_toolkit style definitions in the code  

---

## Contributing

Contributions are welcome:

1. Fork the repo  
2. Create a feature branch  
3. Write clear, documented code and tests under `tests/`  
4. Submit a pull request  

Please follow and include meaningful commit messages.

---

## License

This project is licensed under the **GNU GPL v3**. See the [LICENSE](LICENSE) file for details.

---

## Author

**Luca Bocaletto**  
- Website: https://bocaletto-luca.github.io  
- GitHub: https://github.com/bocaletto-luca  
- Portfolio: https://bocalettoluca.altervista.org  

---
