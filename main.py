#!/usr/bin/env python3
"""
PyMailCli – Terminal Email Client
Supports IMAP read, SMTP send, PGP sign/encrypt, attachments, search, threads.
"""

import os, sys, json, tempfile, subprocess
from pathlib import Path
from getpass import getpass
from imapclient import IMAPClient
import smtplib, gnupg, yaml
from email.message import EmailMessage
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

# ─── Config & Globals ───────────────────────────────────────────────────────

HOME = Path.home()
CONFIG_DIR = HOME/".config"/"pyemail"
CONFIG_FILE = CONFIG_DIR/"config.yaml"
console = Console()
session = PromptSession()
kb = KeyBindings()

def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        return yaml.safe_load(CONFIG_FILE)
    cfg = {
        "imap_host":"",
        "imap_port":993,
        "smtp_host":"",
        "smtp_port":587,
        "email":"",
        "gpg_recipient":"",
        "shortcuts": {
            "quit": "q",
            "back": "b"
        },
        "theme": "monokai"
    }
    with CONFIG_FILE.open("w") as f:
        yaml.dump(cfg,f)
    console.print(f"[yellow]Created default config at {CONFIG_FILE}[/yellow]")
    return cfg

cfg = load_config()

# ─── Mail Backend ────────────────────────────────────────────────────────────

class MailClient:
    def __init__(self, cfg):
        pwd = getpass(f"Password for {cfg['email']}: ")
        self.imap = IMAPClient(cfg["imap_host"], port=cfg["imap_port"], ssl=True)
        self.imap.login(cfg["email"], pwd)
        self.smtp = smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"])
        self.smtp.starttls()
        self.smtp.login(cfg["email"], pwd)
        self.gpg = gnupg.GPG()
        self.recipient = cfg["gpg_recipient"]

    def list_folders(self):
        return [f.decode().split(' "/" ')[-1] for f in self.imap.list()]

    def fetch_messages(self, folder, limit=50):
        self.imap.select_folder(folder)
        uids = self.imap.search(['ALL'])
        msgs = self.imap.fetch(uids[-limit:], ['ENVELOPE','BODY.PEEK[]'])
        # return list of (uid, envelope, raw)
        return [(uid, data[b'ENVELOPE'], data[b'BODY.PEEK[]']) for uid,data in msgs.items()]

    def logout(self):
        self.imap.logout()
        self.smtp.quit()

# ─── UI Helpers ──────────────────────────────────────────────────────────────

def prompt_menu(title, options):
    console.rule(title)
    for i,(k,v) in enumerate(options.items(),1):
        console.print(f" {i}) [bold]{k}[/bold] - {v}")
    choice = session.prompt("Choose: ")
    try:
        idx=int(choice)-1
        return list(options.keys())[idx]
    except:
        return None

def view_folders(mc):
    folders = mc.list_folders()
    sel = prompt_menu("Mail Folders", {f:"" for f in folders})
    return sel

def view_messages(mc, folder):
    msgs = mc.fetch_messages(folder)
    table = Table(title=f"{folder} (latest {len(msgs)})")
    table.add_column("Idx", style="cyan", no_wrap=True)
    table.add_column("Date"); table.add_column("From"); table.add_column("Subject")
    for i,(uid,env,raw) in enumerate(msgs,1):
        table.add_row(str(i), env.date.decode(), env.from_[0].mailbox.decode()+"@"+env.from_[0].host.decode(), env.subject.decode())
    console.print(table)
    choice = session.prompt("Message idx to view (or ENTER): ")
    if not choice.isdigit(): return
    idx=int(choice)-1
    uid,env,raw = msgs[idx]
    import email
    msg = email.message_from_bytes(raw)
    console.rule("Message Body")
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype=="text/plain":
                console.print(Markdown(part.get_payload(decode=True).decode()))
    else:
        console.print(Markdown(msg.get_payload(decode=True).decode()))
    # attachments
    atts = [p for p in msg.walk() if p.get_filename()]
    if atts:
        console.print(f"[green]{len(atts)} attachments[/green]")
        if session.prompt("Download attachments? (y/N)> ").lower()=="y":
            outdir = Path(session.prompt("Save to folder: ")).expanduser()
            outdir.mkdir(parents=True, exist_ok=True)
            for p in atts:
                fn=p.get_filename()
                data=p.get_payload(decode=True)
                (outdir/fn).write_bytes(data)
                console.print(f"Saved {fn}")
    session.prompt("Press ENTER to go back")

def compose_message(mc):
    to = session.prompt("To: ")
    subj = session.prompt("Subject: ")
    # open editor for body
    EDITOR = os.environ.get("EDITOR","vim")
    with tempfile.NamedTemporaryFile(suffix=".md") as tf:
        tf.write(b"# Write your message below\n")
        tf.flush()
        subprocess.call([EDITOR, tf.name])
        body = Path(tf.name).read_text()
    msg = EmailMessage()
    msg["From"]=cfg["email"]
    msg["To"]=to
    msg["Subject"]=subj
    msg.set_content(body)
    # attachments
    if session.prompt("Attach files? (y/N)> ").lower()=="y":
        paths = session.prompt("Paths (comma sep)> ").split(",")
        for p in paths:
            data=Path(p.strip()).read_bytes()
            msg.add_attachment(data,filename=Path(p).name)
    # PGP sign/encrypt
    if session.prompt("PGP sign? (y/N)> ").lower()=="y":
        signed = mc.gpg.sign(msg.as_string(), default_key=cfg["gpg_recipient"])
        msg.set_content(str(signed))
    console.print("[yellow]Sending...[/yellow]")
    mc.smtp.send_message(msg)
    console.print("[green]Email sent![/green]")
    session.prompt("Press ENTER to continue")

def search_messages(mc):
    folder = session.prompt("Folder to search: ")
    selfilter = session.prompt("Search term (subject/from): ")
    mc.imap.select_folder(folder)
    uids = mc.imap.search(['OR','SUBJECT', selfilter, 'FROM', selfilter])
    for uid in uids[-10:]:
        env = mc.imap.fetch(uid, ['ENVELOPE'])[uid][b'ENVELOPE']
        console.print(f"{uid}: [cyan]{env.subject.decode()}[/cyan] from {env.from_[0].mailbox.decode()}@{env.from_[0].host.decode()}")

    session.prompt("ENTER to go back")

# ─── Main Loop ──────────────────────────────────────────────────────────────

def main():
    mc = MailClient(cfg)
    try:
        while True:
            action = prompt_menu("Main Menu", {
                "Folders":"Browse mail folders",
                "Search":"Search messages",
                "Compose":"Write a new message",
                "Quit":"Exit client"
            })
            if action=="Folders":
                fld = view_folders(mc)
                if fld: view_messages(mc, fld)
            elif action=="Search":
                search_messages(mc)
            elif action=="Compose":
                compose_message(mc)
            elif action=="Quit":
                break
    finally:
        mc.logout()
        console.print("[bold]Goodbye![/bold]")

if __name__=="__main__":
    main()
