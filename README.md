# Pop Launcher Obsidian Plugin

![Screenshot](screenshot.png)

A pop-launcher plugin for managing your [Obsidian.md](https://obsidian.md/) vault. This plugin allows you to:
- Search notes by name
- Search notes by content
- Open daily notes
- Quick capture to notes

## Features

The plugin supports the following commands:
- `on <query>` - Search for notes by name
- `of <query>` - Search for notes by content
- `od` - Open today's daily note
- `oc <content>` - Quick capture to a note

## Installation

### Dependencies

First, install the required Python packages:

```bash
# For system-wide installation (recommended)
sudo apt install python3-fuzzywuzzy python3-levenshtein

# For user-local installation (if you don't have sudo access)
pip install --user fuzzywuzzy python-Levenshtein
```

### Plugin Installation

1. Create the plugin directory:
```bash
mkdir -p ~/.local/share/pop-launcher/plugins/obsidian
```

2. Copy the plugin files:
```bash
cp obsidian.py ~/.local/share/pop-launcher/plugins/obsidian/
cp plugin.ron ~/.local/share/pop-launcher/plugins/obsidian/
cp -r src ~/.local/share/pop-launcher/plugins/obsidian/
```

3. Make the plugin executable:
```bash
chmod +x ~/.local/share/pop-launcher/plugins/obsidian/obsidian.py
```

4. Set up environment variables in your shell configuration (e.g., `~/.bashrc` or `~/.zshrc`):
```bash
export OBSIDIAN_VAULT_PATH="/path/to/your/vault"
export OBSIDIAN_QUICK_CAPTURE_NOTE="Quick Capture.md"  # Optional
export OBSIDIAN_NUMBER_OF_NOTES=8  # Optional
```

## Configuration

The plugin can be configured through environment variables:

- `OBSIDIAN_VAULT_PATH` - Path to your Obsidian vault (required)
- `OBSIDIAN_QUICK_CAPTURE_NOTE` - Quick capture note (defaults to daily note if empty)
- `OBSIDIAN_NUMBER_OF_NOTES` - Number of notes to show in results (defaults to 8)

## Development

### Running Tests

The plugin uses doctest for testing the `functions` and `moment` modules. To run the tests:

1. Install test dependencies:
```bash
pip install time_machine
```

2. Run the tests:
```bash
python3 -m src.functions
python3 -m src.moment
```

### Development Mode

To run the plugin in development mode:

```bash
# Install development dependencies
pip install -r requirements.txt

# Run the plugin
./obsidian.py
```

## License

[Your License Here] 