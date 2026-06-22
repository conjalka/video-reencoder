# Video Reencoding Script

A Python script that automatically converts video files to HEVC/H.265 format using HandBrake, reducing file sizes while maintaining quality.

## Features

### Core Features
- 🔄 **Recursive Processing**: Scans directories and subdirectories for video files
- 🎯 **Smart Detection**: Automatically detects video codec, resolution, and framerate
- 📊 **Preset Matching**: Selects appropriate HandBrake preset based on video properties
- ⏭️ **Skip HEVC Files**: Automatically skips files already encoded in HEVC/H.265
- 📈 **Real-time Progress**: Shows encoding progress and status updates
- 📝 **Detailed Logging**: Maintains timestamped logs of all operations
- 💾 **Space Tracking**: Reports space saved after each conversion
- 🔒 **Safe Operation**: Creates temporary files and only replaces originals on success
- 🧪 **Dry Run Mode**: Test what would be processed without making changes

### Enhanced Features ⭐ NEW
- 🔄 **Resume Capability**: Continue from where you left off if interrupted
- 🎯 **Skip Encoded Files**: Detects `[*HEVC]` pattern in filenames
- 📊 **Progress Bar**: Visual progress tracking with tqdm
- 💾 **Backup Option**: Optional backup of original files before deletion
- ⚡ **Quality Presets**: Choose between fast, balanced, or best quality
- 🚀 **Parallel Processing**: Process multiple files simultaneously (2-4x faster!)
- ⚡ **GPU Acceleration**: Use NVIDIA/Intel/AMD/Apple GPU for 5-10x faster encoding!

See [`ENHANCEMENTS_GUIDE.md`](ENHANCEMENTS_GUIDE.md) for detailed information on new features.
See [`GPU_ACCELERATION_GUIDE.md`](GPU_ACCELERATION_GUIDE.md) for GPU setup and usage.

## Supported Video Formats

The script supports all video formats that HandBrake can process:
- `.mp4`, `.m4v`, `.mkv`
- `.avi`, `.mov`, `.wmv`
- `.flv`, `.mpg`, `.mpeg`
- `.m2ts`, `.ts`, `.vob`
- `.3gp`, `.webm`

## Prerequisites

### 1. Python 3.7 or higher

Check your Python version:
```bash
python --version
```

### 2. HandBrakeCLI

HandBrakeCLI must be installed on your system. See [HANDBRAKE_INSTALLATION.md](HANDBRAKE_INSTALLATION.md) for detailed installation instructions.

Quick install:
- **Windows (Chocolatey)**: `choco install handbrake-cli`
- **macOS (Homebrew)**: `brew install handbrake`
- **Ubuntu/Debian**: `sudo apt install handbrake-cli`

## Installation

1. Clone or download this repository

2. Install optional dependencies (recommended):
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install tqdm manually for progress bars:
   ```bash
   pip install tqdm
   ```
   
   **Note:** The script works without tqdm, but you'll get a better experience with it installed.

## Usage

### Basic Usage

Process all videos in a directory:
```bash
python video_reencoder.py /path/to/videos
```

### Windows Example
```powershell
python video_reencoder.py "C:\Users\YourName\Videos"
```

### macOS/Linux Example
```bash
python video_reencoder.py /home/username/Videos
```

### Command-Line Options

```bash
python video_reencoder.py [OPTIONS] SOURCE_DIRECTORY
```

**Core Options:**
- `--dry-run`: Preview what would be processed without making changes
- `--handbrake-path PATH`: Specify custom HandBrakeCLI path
- `--log-file NAME`: Custom log file name (default: reencoding.log)

**Enhanced Options:** ⭐ NEW
- `--quality {fast,balanced,best}`: Encoding quality preset (default: balanced)
- `--parallel N`: Process N files simultaneously (default: 1, max: CPU cores)
- `--gpu {nvenc,qsv,vce,videotoolbox,none}`: GPU encoder (default: none/CPU)
- `--backup-dir PATH`: Backup original files before deletion
- `--no-resume`: Don't resume from previous session (start fresh)
- `--no-skip-encoded`: Don't skip files with `[*HEVC]` in filename
- `--reset`: Clear state file and start fresh

### Examples

**Basic processing:**
```bash
python video_reencoder.py /path/to/videos
```

**Dry run to preview processing:**
```bash
python video_reencoder.py /path/to/videos --dry-run
```

**GPU acceleration (NVIDIA):**
```bash
python video_reencoder.py /path/to/videos --gpu nvenc
```

**Parallel processing (4 files at once):**
```bash
python video_reencoder.py /path/to/videos --parallel 4
```

**Maximum speed (GPU + parallel):**
```bash
python video_reencoder.py /path/to/videos --gpu nvenc --parallel 2
```

**Best quality with backup:**
```bash
python video_reencoder.py /path/to/videos --quality best --backup-dir ./backups
```

**Custom HandBrakeCLI path:**
```bash
python video_reencoder.py /path/to/videos --handbrake-path /usr/local/bin/HandBrakeCLI
```

**Reset and start fresh:**
```bash
python video_reencoder.py /path/to/videos --reset
```

## How It Works

1. **Scan**: Recursively scans the source directory for video files
2. **Analyze**: For each video file:
   - Extracts codec, resolution, and framerate information
   - Checks if already encoded in HEVC/H.265 (skips if yes)
3. **Select Preset**: Chooses appropriate HandBrake preset based on video properties:
   - 4K (2160p) → H.265 MKV 2160p30/60 4K
   - 1080p → H.265 MKV 1080p30
   - 720p → H.265 MKV 720p30
   - 480p → H.265 MKV 480p30
4. **Encode**: Converts video using HandBrake with selected preset
5. **Replace**: Replaces original file with reencoded version
6. **Report**: Logs file size reduction and space saved

## Output

### Console Output

The script provides real-time status updates:
```
2024-01-15 10:30:00 - INFO - Video Reencoder started
2024-01-15 10:30:00 - INFO - Source directory: /path/to/videos
2024-01-15 10:30:01 - INFO - HandBrakeCLI found: HandBrake 1.7.0
2024-01-15 10:30:02 - INFO - Found 15 video files

================================================================================
Processing: /path/to/videos/movie.mp4
Codec: h264
Resolution: 1920x1080
FPS: 30
Selected preset: H.265 MKV 1080p30
Original size: 2.50 GB
Starting reencoding...
Encoding: task 1 of 1, 45.23 % (25.50 fps, avg 24.89 fps, ETA 00h15m30s)
New size: 1.20 GB
Space saved: 1.30 GB (52.0%)
Successfully reencoded: movie [1080p30 HEVC].mkv
================================================================================
```

### Log Files

Detailed logs are saved in the `logs/` directory with timestamps:
```
logs/
  └── 20240115_103000_reencoding.log
```

Each log contains:
- Start/end times
- Files processed
- Encoding details
- Errors and warnings
- Final statistics

### Final Statistics

At the end of processing:
```
================================================================================
PROCESSING COMPLETE
================================================================================
Total files found: 15
Successfully processed: 12
Skipped (already HEVC): 2
Failed: 1
Total space saved: 15.75 GB
================================================================================
```

## File Handling

### What Happens to Original Files

1. **Temporary File**: Creates `filename_temp.mkv` during encoding
2. **Success**: Original file is deleted, temp file renamed with encoding info
3. **Failure**: Temp file is deleted, original file remains unchanged

### Output Format

- All reencoded videos are saved as `.mkv` files
- Filename includes encoding information: `original_name [resolution fps HEVC].mkv`
- Examples:
  - `movie.mp4` → `movie [1080p30 HEVC].mkv`
  - `vacation.avi` → `vacation [720p30 HEVC].mkv`
  - `concert.mov` → `concert [2160p60 HEVC].mkv`
- Files remain in their original directory location

## Preset Selection Logic

The script automatically selects the best preset based on video properties:

| Resolution | FPS | Selected Preset |
|------------|-----|-----------------|
| 3840x2160 | 60 | H.265 MKV 2160p60 4K |
| 3840x2160 | 30 | H.265 MKV 2160p30 4K |
| 1920x1080 | Any | H.265 MKV 1080p30 |
| 1280x720 | Any | H.265 MKV 720p30 |
| 720x480 | Any | H.265 MKV 480p30 |

For non-standard resolutions, the script selects the closest matching preset.

## Configuration

You can customize the script by editing `config.json`:

```json
{
  "handbrake": {
    "path": "HandBrakeCLI",
    "encoder": "x265"
  },
  "video_extensions": [".mp4", ".mkv", ".avi", ...],
  "processing": {
    "skip_hevc": true,
    "output_format": "mkv",
    "delete_original": true
  }
}
```

## Troubleshooting

### HandBrakeCLI Not Found

**Error**: `HandBrakeCLI not found`

**Solution**:
1. Verify installation: `HandBrakeCLI --version`
2. Add to PATH or use `--handbrake-path` option
3. See [HANDBRAKE_INSTALLATION.md](HANDBRAKE_INSTALLATION.md)

### Permission Errors

**Error**: Permission denied when accessing files

**Solution**:
- Ensure you have read/write permissions for the source directory
- On Linux/macOS, you may need to use `sudo` (not recommended)
- Check file ownership and permissions

### Encoding Failures

**Error**: HandBrake fails to encode a file

**Possible causes**:
- Corrupted video file
- Unsupported codec or container
- Insufficient disk space
- File in use by another program

**Solution**:
- Check the log file for detailed error messages
- Try encoding the file manually with HandBrake GUI
- Ensure sufficient free disk space (at least 2x the original file size)

### Slow Encoding

**Issue**: Encoding takes a very long time

**Explanation**: HEVC encoding is CPU-intensive and can take time, especially for:
- High-resolution videos (4K)
- Long videos
- Older/slower CPUs

**Tips**:
- Be patient - quality encoding takes time
- Close other CPU-intensive applications
- Consider processing overnight or during off-hours
- Modern CPUs with more cores will encode faster

## Safety Features

- ✅ Creates temporary files during encoding
- ✅ Only deletes original on successful encoding
- ✅ Skips files already in HEVC format
- ✅ Detailed logging of all operations
- ✅ Dry-run mode for testing
- ✅ Graceful handling of interruptions (Ctrl+C)

## Performance Considerations

### Encoding Speed

Encoding speed depends on:
- **CPU**: More cores = faster encoding
- **Resolution**: 4K takes ~4x longer than 1080p
- **Video length**: Proportional to duration
- **Source codec**: Some codecs decode faster than others

### Disk Space

During encoding, you need:
- Original file size
- Temporary file size (usually smaller)
- Minimum: 2x largest video file size free

### Expected Compression

Typical space savings with HEVC:
- **H.264 to HEVC**: 40-60% reduction
- **MPEG-2 to HEVC**: 60-80% reduction
- **Already HEVC**: Skipped (no benefit)

## Best Practices

1. **Start with a test**: Use `--dry-run` first to preview
2. **Backup important files**: Keep originals of irreplaceable content
3. **Check disk space**: Ensure adequate free space
4. **Monitor first few files**: Watch the first conversions to ensure quality
5. **Review logs**: Check logs for any errors or warnings
6. **Test playback**: Verify reencoded files play correctly

## Limitations

- Only processes video files (skips audio-only files)
- Requires HandBrakeCLI to be installed
- Cannot process DRM-protected content
- Encoding is CPU-intensive and time-consuming
- Output format is always MKV

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This script is provided as-is for personal use. HandBrake is licensed under GPLv2.

## Support

For issues with:
- **This script**: Check the logs and troubleshooting section
- **HandBrake**: Visit [HandBrake documentation](https://handbrake.fr/docs/)
- **Video codecs**: Consult video encoding resources

## Acknowledgments

- [HandBrake](https://handbrake.fr/) - The excellent video transcoding tool
- HEVC/H.265 codec developers for efficient video compression

---

**Happy encoding! 🎬**