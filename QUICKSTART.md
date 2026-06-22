# Quick Start Guide

Get started with the Video Reencoding Script in 5 minutes!

## Step 1: Install HandBrakeCLI

Choose your platform:

### Windows (PowerShell as Administrator)
```powershell
choco install handbrake-cli
```

### macOS
```bash
brew install handbrake
```

### Linux (Ubuntu/Debian)
```bash
sudo apt install handbrake-cli
```

**Verify installation:**
```bash
HandBrakeCLI --version
```

## Step 2: Download the Script

Download or clone this repository to your computer.

## Step 3: Test with Dry Run

Before processing your videos, do a test run to see what would happen:

```bash
python video_reencoder.py /path/to/your/videos --dry-run
```

**Example output:**
```
2024-01-15 10:30:00 - INFO - Video Reencoder started
2024-01-15 10:30:00 - INFO - DRY RUN MODE - No files will be modified
2024-01-15 10:30:01 - INFO - Found 10 video files
...
Processing: movie1.mp4
Codec: h264
Resolution: 1920x1080
DRY RUN: Would reencode this file
...
```

## Step 4: Process Your Videos

If the dry run looks good, run the actual conversion:

```bash
python video_reencoder.py /path/to/your/videos
```

## Step 5: Monitor Progress

The script will:
- Show real-time encoding progress
- Display file sizes and space saved
- Create detailed logs in the `logs/` directory

## Common Use Cases

### Process a Single Folder
```bash
python video_reencoder.py "C:\Users\YourName\Videos\Movies"
```

### Process with Subfolders
The script automatically processes all subfolders:
```bash
python video_reencoder.py "C:\Users\YourName\Videos"
```
This will process:
- `C:\Users\YourName\Videos\Movies\`
- `C:\Users\YourName\Videos\TV Shows\`
- `C:\Users\YourName\Videos\Home Videos\`
- And all other subfolders

### Custom HandBrakeCLI Location
```bash
python video_reencoder.py /path/to/videos --handbrake-path "C:\Program Files\HandBrake\HandBrakeCLI.exe"
```

## What to Expect

### Processing Time
- **1080p video (1 hour)**: ~30-60 minutes to encode
- **4K video (1 hour)**: ~2-4 hours to encode
- Times vary based on CPU speed

### Space Savings
Typical results:
- **H.264 → HEVC**: 40-60% smaller
- **MPEG-2 → HEVC**: 60-80% smaller
- **Already HEVC**: Skipped automatically

### Example Results
```
Original: movie.mp4 (2.5 GB)
Encoded:  movie [1080p30 HEVC].mkv (1.2 GB)
Saved:    1.3 GB (52%)
```

**Filename Format:**
All reencoded files include encoding information in the filename:
- `vacation.mp4` → `vacation [1080p30 HEVC].mkv`
- `concert.avi` → `concert [720p60 HEVC].mkv`
- `movie.mov` → `movie [2160p30 HEVC].mkv`

## Tips for First-Time Users

1. **Start Small**: Test with a few files first
2. **Check Quality**: Watch a reencoded video to ensure quality is acceptable
3. **Monitor Logs**: Check `logs/` folder for detailed information
4. **Be Patient**: HEVC encoding is slow but worth it
5. **Free Space**: Ensure you have enough disk space (2x largest file)

## Stopping the Process

Press `Ctrl+C` to stop the script at any time. The current file being processed will be left as-is (original unchanged).

## Checking Results

After processing:
1. Check the final statistics in the console
2. Review the log file in `logs/` directory
3. Verify a few reencoded videos play correctly
4. Check the space saved

## Troubleshooting

### "HandBrakeCLI not found"
- Verify installation: `HandBrakeCLI --version`
- Use `--handbrake-path` to specify location

### "Permission denied"
- Ensure you have write access to the video directory
- On Windows, try running PowerShell as Administrator

### Encoding fails
- Check the log file for details
- Ensure the video file isn't corrupted
- Verify sufficient disk space

## Next Steps

- Read the full [README.md](README.md) for detailed information
- See [HANDBRAKE_INSTALLATION.md](HANDBRAKE_INSTALLATION.md) for installation help
- Customize settings in `config.json`

## Need Help?

1. Check the logs in `logs/` directory
2. Review the [README.md](README.md) troubleshooting section
3. Verify HandBrakeCLI is working: `HandBrakeCLI --version`

---

**Ready to save space? Let's go! 🚀**