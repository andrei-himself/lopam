# storage.py
from pathlib import Path
import os, json, tempfile, base64

from crypto import derive_key, aead_decrypt

def xdg_path(env_var, default):
    return Path(os.environ.get(env_var, default)).expanduser()

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    path.chmod(0o700)

def load_or_init_config(config_dir: Path, default_vaults: Path):
    cfg_path = config_dir / "config.json"
    if not cfg_path.exists():
        cfg = {
            "vaults_dir": str(default_vaults)
        }
        ensure_dir(default_vaults)
        cfg_path.write_text(json.dumps(cfg, indent=2))
        os.chmod(cfg_path, 0o600)
        return cfg
    cfg = json.loads(cfg_path.read_text())
    return cfg

def resolve_dirs():
    config_dir = xdg_path("XDG_CONFIG_HOME", "~/.config") / "lopam"
    data_dir = xdg_path("XDG_DATA_HOME", "~/.local/share") / "lopam"
    ensure_dir(config_dir)
    ensure_dir(data_dir)
    default_vaults = data_dir / "vaults"
    cfg = load_or_init_config(config_dir, default_vaults)
    vaults_dir = Path(cfg.get("vaults_dir", str(default_vaults))).expanduser()
    ensure_dir(vaults_dir)
    return config_dir, vaults_dir

def write_file_atomic(path: Path, data: bytes, mode: int = 0o600) -> None:
    path = Path(path)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(path.parent), delete=False) as temp_file:
            tmp = temp_file.name
            temp_file.write(data)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(tmp, str(path))
        os.chmod(str(path), mode)
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass

def read_vault(vault_path: Path, password:str):
    doc = json.loads(Path(vault_path).read_text())
    kdf = doc["kdf"]
    salt = base64.b64decode(doc["salt"])
    nonce = base64.b64decode(doc["nonce"])
    ct = base64.b64decode(doc["ciphertext"])
    ad_obj = {k : doc[k] for k in ("version", "kdf", "salt", "nonce")}
    ad = json.dumps(ad_obj, sort_keys=True, separators=(",", ":")).encode()
    key = derive_key(password.encode("utf-8"), salt, kdf["mem_mb"], kdf["iterations"], kdf["parallelism"])
    pt = aead_decrypt(key, nonce, ct, ad)
    vault = json.loads(pt.decode())
    return vault, doc, key