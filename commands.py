# commands.py
from pathlib import Path
from storage import *
from crypto import *
from clipboard import copy_with_timeout
import getpass
import base64, json

def init_vault(vault_name: str):
    config_dir, vaults_dir = resolve_dirs()
    vault_path = vaults_dir / f"{vault_name}.json"
    
    if vault_path.exists():
        raise SystemExit(f"Vault {vault_name} already exists")
    
    pw1 = getpass.getpass(f"Create master password for vault {vault_name}:")
    print("------------------------------")
    pw2 = getpass.getpass("Confirm master password:")
    
    if pw1 != pw2:
        raise SystemExit("Passwords do not match")

    print(f"Initializing new vault '{vault_name}'...")

    pw = pw1.encode('utf-8')
    kdf = {
        "name": "argon2id",
        "mem_mb": 256,
        "iterations": 3,
        "parallelism": 1
    }
    salt = random_bytes(32)
    key = derive_key(pw, salt, kdf["mem_mb"], kdf["iterations"], kdf["parallelism"])
    nonce = random_bytes(24)
    
    header_wo_ciphertext = {
        "version": 1,
        "kdf": kdf,
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii")
    }

    ad = json.dumps(header_wo_ciphertext, sort_keys=True, separators=(",", ":")).encode()

    plaintext = json.dumps({"entries": []}).encode()
    ciphertext = aead_encrypt(key, nonce, plaintext, ad)

    doc = dict(header_wo_ciphertext)
    doc["ciphertext"] = base64.b64encode(ciphertext).decode("ascii")
    write_file_atomic(vault_path, json.dumps(doc, indent=2).encode(), mode=0o600)

    print(f"Vault {vault_name} created!")

def add_entry(vault_name, entry_name):
    _, vaults_dir = resolve_dirs()
    path = vaults_dir / f"{vault_name}.json"
    
    pw = getpass.getpass("Enter vault password:")
    try: 
        vault, header, key = read_vault(path, pw)
    except Exception:
        print("Unlock failed.")
        return
    print("Vault unlocked.")
    
    username = input("Enter entry username: ")
    pwd = getpass.getpass("Enter entry password (leave empty to cancel):")
    if not pwd:
        print("Aborted.")
        return

    print(f"Adding '{entry_name}' to vault '{vault_name}'...")
    vault.setdefault("entries", []).append(
        {"name": entry_name, "username": username, "password": pwd}
    )

    nonce = random_bytes(24)
    header["nonce"] = base64.b64encode(nonce).decode("ascii")
    
    ad_obj = {k : header[k] for k in ("version", "kdf", "salt", "nonce")}
    ad = json.dumps(ad_obj, sort_keys=True, separators=(",", ":")).encode()
    
    plaintext = json.dumps(vault).encode()
    ct = aead_encrypt(key, nonce, plaintext, ad)
    header["ciphertext"] = base64.b64encode(ct).decode("ascii")
    
    write_file_atomic(path, json.dumps(header, indent=2).encode(), mode = 0o600)
    print("Entry added.")
    

def list_entries(vault_name, keyword=""):
    _, vaults_dir = resolve_dirs()
    path = vaults_dir / f"{vault_name}.json"
    
    pw = getpass.getpass("Enter vault password:")
    try:
        vault, header, key = read_vault(path, pw)
    except Exception:
        print("Unlock failed.")
        return
    print(f"Vault unlocked.")
    
    if keyword:
        print(f"Listing '{keyword}' entries...")
    else:
        print("Listing all entries...")
    
    kw = keyword.lower()
    for e in vault.get("entries", []):
        name = e.get("name", "")
        if kw in name.lower():
            print(name)

def show_entry(vault_name, entry_name):
    _, vaults_dir = resolve_dirs()
    path = vaults_dir / f"{vault_name}.json"

    pw = getpass.getpass("Enter vault password:")
    try:
        vault, header, key = read_vault(path, pw)
    except Exception:
        print("Unlock failed")
        return
    print("Vault unlocked.")

    entry = next((e for e in vault.get("entries", []) if e.get("name") == entry_name), None)
    if not entry:
        print("Entry not found.")
        return
    
    print(f"Username: {entry.get('username', '')}")
    pwd = entry.get("password", "")
    if not pwd:
        print("No password stored.")
        return
    print("Password copied to clipboard for 30s.")
    copy_with_timeout(pwd)