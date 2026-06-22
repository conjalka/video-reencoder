#!/bin/bash
# Example Usage Scripts for Video Reencoder
# These examples show common use cases

echo "Video Reencoder - Example Usage"
echo "================================"
echo ""

# Example 1: Dry run to preview what would be processed
echo "Example 1: Dry Run (Preview Mode)"
echo "python video_reencoder.py /path/to/videos --dry-run"
echo ""

# Example 2: Basic usage - process all videos in a directory
echo "Example 2: Basic Usage"
echo "python video_reencoder.py /path/to/videos"
echo ""

# Example 3: Process videos with custom HandBrakeCLI path
echo "Example 3: Custom HandBrakeCLI Path"
echo "python video_reencoder.py /path/to/videos --handbrake-path /usr/local/bin/HandBrakeCLI"
echo ""

# Example 4: Custom log file name
echo "Example 4: Custom Log File"
echo "python video_reencoder.py /path/to/videos --log-file my_conversion.log"
echo ""

# Example 5: Windows path example
echo "Example 5: Windows Path"
echo "python video_reencoder.py \"C:\\Users\\YourName\\Videos\\Movies\""
echo ""

# Example 6: Process multiple directories (run separately)
echo "Example 6: Process Multiple Directories"
echo "python video_reencoder.py /path/to/movies"
echo "python video_reencoder.py /path/to/tv_shows"
echo "python video_reencoder.py /path/to/home_videos"
echo ""

# Example 7: Full command with all options
echo "Example 7: Full Command with All Options"
echo "python video_reencoder.py /path/to/videos \\"
echo "  --handbrake-path /usr/local/bin/HandBrakeCLI \\"
echo "  --log-file detailed_conversion.log \\"
echo "  --dry-run"
echo ""

echo "================================"
echo "For more information, see README.md"

# Made with Bob
