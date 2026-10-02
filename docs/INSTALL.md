# Installing Lyra

Lyra runs on Linux first (Arch, CachyOS, Debian/Ubuntu, Fedora) and also on
Windows and macOS. The core uses only the Python standard library, so there is
nothing to compile and no dependency to install by hand.

## Requirements

- Python 3.10 or newer.
- Optional: [Ollama](https://ollama.com) for a local model.
- Optional: a cloud API key for weak machines (see `docs/CLOUD_MODELS.md`).

## Quick install (Linux, recommended)

From the repository folder:

```bash
./install.sh
```

The script is guided and does only these things, asking before each optional
step:

1. checks Python 3.10+;
2. installs Lyra into an isolated venv at `~/.local/share/lyra/venv`;
3. puts a `lyra` launcher in `~/.local/bin`;
4. offers to install Ollama and pull the model it recommends for your machine;
5. offers to install a systemd user service to start the GUI at login;
6. runs `lyra --doctor` so you see exactly what is ready.

Non-interactive (accept all defaults):

```bash
./install.sh --yes
./install.sh --no-ollama --no-service   # minimal
```

If `~/.local/bin` is not in your `PATH`, add it:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

## Manual install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install .
lyra --doctor
```

Or run it without installing anything:

```bash
python -m lyra_app
```

## First run

```bash
lyra            # terminal
lyra --gui      # browser GUI on http://127.0.0.1:8000
```

The first run asks for language, the companion's name, how it should address
you, its personality, whether you want voice, and which model to use. The model
suggestion is based on your hardware; press Enter to accept it.

## Where things live

- The companion lives in `~/.lyra` (change with `--home` or `LYRA_HOME`).
  Copy that folder to another machine and the companion comes with it.
- The program lives in `~/.local/share/lyra/venv`.
- The launcher is `~/.local/bin/lyra`.

## Uninstall

```bash
rm -rf ~/.local/share/lyra ~/.local/bin/lyra
systemctl --user disable --now lyra.service 2>/dev/null || true
rm -f ~/.config/systemd/user/lyra.service
# Your companion folder (~/.lyra) is left untouched on purpose.
```
