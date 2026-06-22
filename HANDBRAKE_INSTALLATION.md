# HandBrakeCLI Installation Guide

This guide will help you install HandBrakeCLI (the command-line version of HandBrake) on your system.

## What is HandBrakeCLI?

HandBrakeCLI is the command-line interface for HandBrake, a powerful video transcoding tool. This script uses HandBrakeCLI to convert videos to the HEVC/H.265 format for better compression and smaller file sizes.

## Installation Instructions

### Windows

#### Option 1: Using Chocolatey (Recommended)

If you have [Chocolatey](https://chocolatey.org/) installed:

```powershell
choco install handbrake-cli
```

#### Option 2: Manual Installation

1. Download HandBrake from the official website:
   - Visit: https://handbrake.fr/downloads.php
   - Download the Windows CLI version (HandBrakeCLI)

2. Extract the downloaded archive to a location of your choice (e.g., `C:\Program Files\HandBrake\`)

3. Add HandBrakeCLI to your system PATH:
   - Open System Properties → Advanced → Environment Variables
   - Under "System variables", find and select "Path"
   - Click "Edit" → "New"
   - Add the path to the HandBrakeCLI directory (e.g., `C:\Program Files\HandBrake\`)
   - Click "OK" to save

4. Verify installation by opening a new PowerShell/Command Prompt window and running:
   ```powershell
   HandBrakeCLI --version
   ```

### macOS

#### Option 1: Using Homebrew (Recommended)

If you have [Homebrew](https://brew.sh/) installed:

```bash
brew install handbrake
```

#### Option 2: Manual Installation

1. Download HandBrake from the official website:
   - Visit: https://handbrake.fr/downloads.php
   - Download the macOS CLI version

2. Install the downloaded package

3. Verify installation:
   ```bash
   HandBrakeCLI --version
   ```

### Linux

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install handbrake-cli
```

#### Fedora

```bash
sudo dnf install handbrake-cli
```

#### Arch Linux

```bash
sudo pacman -S handbrake-cli
```

#### Other Distributions

For other Linux distributions, check your package manager or visit the [HandBrake downloads page](https://handbrake.fr/downloads.php).

## Verifying Installation

After installation, verify that HandBrakeCLI is accessible:

```bash
HandBrakeCLI --version
```

You should see output similar to:
```
HandBrake 1.x.x
```

## Using Custom HandBrakeCLI Path

If HandBrakeCLI is not in your system PATH, or you want to use a specific version, you can specify the path when running the script:

```bash
python video_reencoder.py /path/to/videos --handbrake-path /path/to/HandBrakeCLI
```

### Example Paths

**Windows:**
```powershell
python video_reencoder.py C:\Videos --handbrake-path "C:\Program Files\HandBrake\HandBrakeCLI.exe"
```

**macOS/Linux:**
```bash
python video_reencoder.py /home/user/Videos --handbrake-path /usr/local/bin/HandBrakeCLI
```

## Troubleshooting

### "HandBrakeCLI not found" Error

If you get this error:
1. Verify HandBrakeCLI is installed: `HandBrakeCLI --version`
2. If not found, check your PATH environment variable
3. Try specifying the full path using `--handbrake-path`

### Permission Errors (Linux/macOS)

If you encounter permission errors:
```bash
sudo chmod +x /path/to/HandBrakeCLI
```

### Windows Execution Policy

If you have issues running commands in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Additional Resources

- [HandBrake Official Website](https://handbrake.fr/)
- [HandBrake Documentation](https://handbrake.fr/docs/)
- [HandBrake CLI Guide](https://handbrake.fr/docs/en/latest/cli/cli-guide.html)

## Next Steps

Once HandBrakeCLI is installed and verified, you can proceed to use the video reencoding script. See [README.md](README.md) for usage instructions.