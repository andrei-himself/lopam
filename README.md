# lopam 🔐

A command-line password manager for Linux that stores encrypted vaults locally, using Argon2id for key derivation and XChaCha20-Poly1305 through established cryptographic libraries.

---

## Motivation

Every password manager I tried was either cloud-based (your vault lives on someone else's server) or bloated with a UI I didn't need. I wanted something that stores passwords _locally_, uses _real_ modern cryptography, and works entirely from the terminal.

So I built lopam. It keeps your vaults as encrypted JSON files on your own machine, derives encryption keys from your master password using Argon2id (the winner of the Password Hashing Competition), and authenticates every byte with XChaCha20-Poly1305 so tampering is detected immediately. No cloud, no accounts, no tracking.

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/andrei-himself/lopam.git
cd lopam
chmod +x install.sh
./install.sh
```

The installer creates a virtual environment, installs dependencies, and adds the `lopam` command to `~/.local/bin`. Make sure that directory is in your `PATH`, then:

```bash
# Create your first vault
lopam init MyVault

# Add a password
lopam add MyVault github

# Copy it to clipboard (auto-clears after 30 seconds)
lopam show MyVault github
```

**Requires:** Python 3.10+, Linux with Wayland (`wl-clipboard`)

---

## Usage

### Initialize a vault

```bash
lopam init <vault_name>
```

Creates an encrypted vault file. You'll be prompted to set a master password. The vault is initialized with Argon2id key derivation (256 MB memory, 3 iterations) and a fresh random salt and nonce.

### Add an entry

```bash
lopam add <vault_name> <entry_name>
```

Unlocks the vault with your master password, then prompts for a username and password to store. Each save re-encrypts the entire vault with a fresh nonce.

### List entries

```bash
lopam list <vault_name>              # show all entries
lopam list <vault_name> <keyword>    # filter by name
```

### Show an entry

```bash
lopam show <vault_name> <entry_name>
```

Prints the username and copies the password to your clipboard. The clipboard is automatically cleared after 30 seconds.

---

## How the Encryption Works

Each vault is a JSON file with this structure:

```json
{
  "version": 1,
  "kdf": {
    "name": "argon2id",
    "mem_mb": 256,
    "iterations": 3,
    "parallelism": 1
  },
  "salt": "<base64>",
  "nonce": "<base64>",
  "ciphertext": "<base64>"
}
```

**Key derivation** — Argon2id turns your master password + a random 32-byte salt into a 32-byte encryption key. The high memory cost (256 MB) makes brute-force attacks expensive even with GPUs.

**Encryption** — XChaCha20-Poly1305 encrypts the vault contents and authenticates the header metadata as additional data (AD). This means if anyone tampers with the salt, nonce, or KDF parameters on disk, decryption fails immediately.

**Atomic writes** — Vault updates are written to a temporary file in the same directory, flushed to disk, and moved into place with os.replace().

**File permissions** — Vault files are created with mode `0o600` (owner read/write only).

---

## Contributing

### Clone and set up

```bash
git clone https://github.com/andrei-himself/lopam.git
cd lopam
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run directly (without installing)

```bash
python main.py init TestVault
```

### Submit a pull request

Fork the repo, create a feature branch, and open a pull request to `main`. Please describe what you changed and why.

---

## License

MIT — see [LICENSE](LICENSE) for details.
