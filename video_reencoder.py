#!/usr/bin/env python3
"""
Video Reencoding Script
Automatically converts video files to HEVC/H.265 format using HandBrake
"""

__version__ = "0.6"

import os
import sys
import json
import queue
import subprocess
import logging
import argparse
import re
import shutil
import multiprocessing
import threading
import ctypes
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

# Try to import tqdm for progress bars
try:
    from tqdm import tqdm as tqdm_progress
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    tqdm_progress = None

# Supported video extensions (HandBrake compatible)
VIDEO_EXTENSIONS = {
    '.mp4', '.m4v', '.mkv', '.avi', '.mov', '.wmv', '.flv', 
    '.mpg', '.mpeg', '.m2ts', '.ts', '.vob', '.3gp', '.webm'
}

# HandBrake preset mapping based on resolution and framerate
PRESET_MAP = {
    # 4K presets
    (3840, 2160, 60): "H.265 MKV 2160p60 4K",
    (3840, 2160, 30): "H.265 MKV 2160p30 4K",
    (3840, 2160, 24): "H.265 MKV 2160p30 4K",
    # 1080p presets
    (1920, 1080, 60): "H.265 MKV 1080p30",
    (1920, 1080, 30): "H.265 MKV 1080p30",
    (1920, 1080, 24): "H.265 MKV 1080p30",
    # 720p presets
    (1280, 720, 60): "H.265 MKV 720p30",
    (1280, 720, 30): "H.265 MKV 720p30",
    (1280, 720, 24): "H.265 MKV 720p30",
    # 480p presets
    (720, 480, 30): "H.265 MKV 480p30",
    (720, 480, 24): "H.265 MKV 480p30",
}

# Quality presets
QUALITY_PRESETS = {
    'fast': {'crf': 28, 'preset': 'fast'},
    'balanced': {'crf': 23, 'preset': 'medium'},
    'best': {'crf': 20, 'preset': 'slow'}
}

# GPU encoder options
GPU_ENCODERS = {
    'nvenc': 'nvenc_h265',      # NVIDIA GPU
    'qsv': 'qsv_h265',           # Intel QuickSync
    'vce': 'vce_h265',           # AMD VCE
    'videotoolbox': 'vt_h265',   # Apple VideoToolbox (macOS)
    'none': 'x265'               # CPU encoding (default)
}


# Windows sleep prevention constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


def prevent_sleep():
    """Prevent system from sleeping (Windows only)"""
    if sys.platform == 'win32':
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            )
            return True
        except Exception:
            return False
    return False


def allow_sleep():
    """Allow system to sleep again (Windows only)"""
    if sys.platform == 'win32':
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            return True
        except Exception:
            return False
    return False


def _suspend_process(pid: int):
    """Suspend all threads of a process (Windows only)"""
    if sys.platform != 'win32':
        return
    THREAD_SUSPEND_RESUME = 0x0002
    kernel32 = ctypes.windll.kernel32
    h_snapshot = kernel32.CreateToolhelp32Snapshot(0x00000004, pid)  # TH32CS_SNAPTHREAD
    if h_snapshot == ctypes.c_void_p(-1).value:
        return
    class THREADENTRY32(ctypes.Structure):
        _fields_ = [
            ('dwSize',             ctypes.c_ulong),
            ('cntUsage',           ctypes.c_ulong),
            ('th32ThreadID',       ctypes.c_ulong),
            ('th32OwnerProcessID', ctypes.c_ulong),
            ('tpBasePri',          ctypes.c_long),
            ('tpDeltaPri',         ctypes.c_long),
            ('dwFlags',            ctypes.c_ulong),
        ]
    te = THREADENTRY32()
    te.dwSize = ctypes.sizeof(THREADENTRY32)
    if kernel32.Thread32First(h_snapshot, ctypes.byref(te)):
        while True:
            if te.th32OwnerProcessID == pid:
                h_thread = kernel32.OpenThread(THREAD_SUSPEND_RESUME, False, te.th32ThreadID)
                if h_thread:
                    kernel32.SuspendThread(h_thread)
                    kernel32.CloseHandle(h_thread)
            if not kernel32.Thread32Next(h_snapshot, ctypes.byref(te)):
                break
    kernel32.CloseHandle(h_snapshot)


def _resume_process(pid: int):
    """Resume all threads of a process (Windows only)"""
    if sys.platform != 'win32':
        return
    THREAD_SUSPEND_RESUME = 0x0002
    kernel32 = ctypes.windll.kernel32
    h_snapshot = kernel32.CreateToolhelp32Snapshot(0x00000004, pid)
    if h_snapshot == ctypes.c_void_p(-1).value:
        return
    class THREADENTRY32(ctypes.Structure):
        _fields_ = [
            ('dwSize',             ctypes.c_ulong),
            ('cntUsage',           ctypes.c_ulong),
            ('th32ThreadID',       ctypes.c_ulong),
            ('th32OwnerProcessID', ctypes.c_ulong),
            ('tpBasePri',          ctypes.c_long),
            ('tpDeltaPri',         ctypes.c_long),
            ('dwFlags',            ctypes.c_ulong),
        ]
    te = THREADENTRY32()
    te.dwSize = ctypes.sizeof(THREADENTRY32)
    if kernel32.Thread32First(h_snapshot, ctypes.byref(te)):
        while True:
            if te.th32OwnerProcessID == pid:
                h_thread = kernel32.OpenThread(THREAD_SUSPEND_RESUME, False, te.th32ThreadID)
                if h_thread:
                    kernel32.ResumeThread(h_thread)
                    kernel32.CloseHandle(h_thread)
            if not kernel32.Thread32Next(h_snapshot, ctypes.byref(te)):
                break
    kernel32.CloseHandle(h_snapshot)


class VideoReencoder:
    """Main class for video reencoding operations"""
    
    def __init__(self, source_dir: str, log_file: str = "reencoding.log",
                 dry_run: bool = False, handbrake_path: str = "HandBrakeCLI",
                 resume: bool = True, skip_encoded: bool = True,
                 backup_dir: Optional[str] = None, quality: str = 'balanced',
                 parallel: int = 1, gpu_encoder: str = 'none'):
        self.source_dir = Path(source_dir).resolve()
        self.log_file = log_file
        self.dry_run = dry_run
        self.handbrake_path = handbrake_path
        self.resume = resume
        self.skip_encoded = skip_encoded
        self.backup_dir = Path(backup_dir) if backup_dir else None
        self.quality = quality
        self.parallel = max(1, min(parallel, multiprocessing.cpu_count()))
        self.gpu_encoder = gpu_encoder if gpu_encoder in GPU_ENCODERS else 'none'
        self.encoder = GPU_ENCODERS[self.gpu_encoder]
        self.state_file = self.source_dir / '.reencoding_state.json'
        self.processed_files = set()
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'skipped': 0,
            'skipped_encoded': 0,
            'skipped_larger': 0,
            'failed': 0,
            'space_saved': 0
        }
        self.stats_lock = multiprocessing.Lock() if parallel > 1 else None
        # Pause / quit control (set by the key-listener thread during encoding)
        self._paused = False
        self.quit_after_current = False

        # Setup logging first so all subsequent calls can use self.logger
        self._setup_logging()
        
        # Setup backup directory
        if self.backup_dir:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load state if resuming
        if self.resume:
            self._load_state()
        
    def _setup_logging(self):
        """Configure logging to both file and console"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = log_dir / f"{timestamp}_{self.log_file}"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Video Reencoder v{__version__} started - Log file: {log_path}")
        self.logger.info(f"Source directory: {self.source_dir}")
        self.logger.info(f"Encoder: {self.encoder} ({self.gpu_encoder})")
        if self.gpu_encoder != 'none':
            self.logger.info(f"GPU acceleration enabled: {self.gpu_encoder.upper()}")
        if self.dry_run:
            self.logger.info("DRY RUN MODE - No files will be modified")
    def _load_state(self):
        """Load previously processed files from state file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.processed_files = set(state.get('processed_files', []))
                    self.logger.info(f"Resuming: {len(self.processed_files)} files already processed")
            except Exception as e:
                self.logger.warning(f"Could not load state file: {e}")
                self.processed_files = set()
        else:
            self.processed_files = set()
    
    def _save_state(self):
        """Save processed files to state file"""
        try:
            state = {
                'processed_files': list(self.processed_files),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save state file: {e}")
    
    def _is_already_encoded(self, filename: str) -> bool:
        """Check if filename indicates it's already HEVC encoded"""
        # Old bracket style: [1080p30 HEVC]
        if re.search(r'\[.*HEVC\]', filename, re.IGNORECASE):
            return True
        # New dash style: - x265 (with optional audio codec after)
        if re.search(r'\bx265\b', filename, re.IGNORECASE):
            return True
        return False
    
    def _backup_file(self, file_path: Path) -> bool:
        """Backup file before deletion"""
        if not self.backup_dir:
            return True
        
        try:
            # Preserve directory structure in backup
            rel_path = file_path.relative_to(self.source_dir)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Backed up to: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to backup file: {e}")
            return False
    
    
    def check_handbrake(self) -> bool:
        """Verify HandBrakeCLI is installed and accessible"""
        try:
            result = subprocess.run(
                [self.handbrake_path, "--version"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                self.logger.info(f"HandBrakeCLI found: {version}")
                return True
            else:
                self.logger.error("HandBrakeCLI not found or not working properly")
                return False
        except FileNotFoundError:
            self.logger.error(f"HandBrakeCLI not found at: {self.handbrake_path}")
            self.logger.error("Please install HandBrakeCLI or specify the correct path")
            return False
        except Exception as e:
            self.logger.error(f"Error checking HandBrakeCLI: {e}")
            return False
    
    def _normalise_audio_codec(self, raw: str) -> str:
        """Normalise a raw audio codec string to a short filename-friendly label."""
        r = raw.lower()
        if 'truehd' in r:           return 'TrueHD'
        if 'dts-hd' in r or 'dts_hd' in r: return 'DTS-HD'
        if 'dts' in r:              return 'DTS'
        if 'eac3' in r or 'e-ac' in r: return 'EAC3'
        if 'ac3' in r or 'ac-3' in r:  return 'AC3'
        if 'aac' in r:              return 'AAC'
        if 'mp3' in r:              return 'MP3'
        if 'flac' in r:             return 'FLAC'
        if 'pcm' in r or 'lpcm' in r: return 'LPCM'
        return raw.upper() if raw else 'unknown'

    def _parse_info_from_stderr(self, stderr: str) -> Optional[Dict]:
        """
        Fallback: parse video properties from HandBrake's plain-text stderr.
        Used when HandBrake suppresses --json output, or when JSON TitleList is empty.

        HandBrake emits lines like:
          scan: 10 previews, 1920x1080, 23.976 fps, ...
          + codec: avc
          scan: audio 0x1: eac3, rate=48000Hz, ...
        """
        # Resolution + fps — allow optional space around 'x', optional comma before fps
        m = re.search(r'(\d{3,4})\s*[xX]\s*(\d{3,4})[, ]+\s*([\d.]+)\s*fps', stderr)
        if not m:
            return None
        width  = int(m.group(1))
        height = int(m.group(2))
        fps    = round(float(m.group(3)))

        # Video codec — HandBrake may say "avc", "avc1", "h264", "hevc", "mpeg4", etc.
        video_codec = 'unknown'
        for pat in [
            r'\+\s*codec:\s*(\S+)',                              # "+ codec: avc"
            r'\+ video track.*?codec[:\s]+(\S+)',
            r'scan:.*?video codec[:\s]+(\S+)',
            r'\b(hevc|h265|h\.265|avc1?|h264|h\.264|mpeg4|mpeg2|vp[89]|av1|vc-?1)\b',
        ]:
            mc = re.search(pat, stderr, re.IGNORECASE)
            if mc:
                video_codec = mc.group(1).lower()
                break

        # Normalise codec aliases to canonical names
        _codec_alias = {
            'avc': 'h264', 'avc1': 'h264',
            'h.264': 'h264', 'h.265': 'hevc', 'h265': 'hevc',
        }
        video_codec = _codec_alias.get(video_codec, video_codec)

        # Audio codec from "scan: audio 0x1: eac3, ..."
        audio_codec = 'unknown'
        ma = re.search(r'scan:\s*audio[^:]*:\s*(\S+),', stderr, re.IGNORECASE)
        if ma:
            audio_codec = self._normalise_audio_codec(ma.group(1))

        is_hevc = video_codec in ('hevc',)
        self.logger.debug(f"Text fallback: {width}x{height} {fps}fps codec={video_codec} audio={audio_codec}")
        return {'codec': video_codec, 'width': width, 'height': height,
                'fps': fps, 'audio_codec': audio_codec, 'is_hevc': is_hevc}

    def get_video_info(self, video_path: Path) -> Optional[Dict]:
        """Extract video information using HandBrakeCLI"""
        try:
            self.logger.debug(f"Scanning video: {video_path.name}")
            result = subprocess.run(
                [self.handbrake_path, "--scan", "--json", "-i", str(video_path)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=300  # Large files over network can take a while to scan
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Failed to scan {video_path.name}: return code {result.returncode}")
                return None
            
            # Parse JSON output
            try:
                # HandBrake may output JSON in either stdout or stderr
                # Try both, preferring stdout first
                # Guard against None (can happen on network share hiccups)
                stdout = result.stdout or ''
                stderr = result.stderr or ''
                output_to_check = stdout if stdout.strip() else stderr
                
                # HandBrake emits multiple JSON objects (e.g. a "Progress" object followed
                # by a "Version"/"TitleList" object).  Scan all top-level objects and use
                # the one that contains "TitleList".
                json_data = None
                search_pos = 0
                while search_pos < len(output_to_check):
                    json_start = output_to_check.find('{', search_pos)
                    if json_start == -1:
                        break
                    
                    # Walk forward counting braces to find the matching closing brace
                    brace_count = 0
                    json_end = json_start
                    for i in range(json_start, len(output_to_check)):
                        if output_to_check[i] == '{':
                            brace_count += 1
                        elif output_to_check[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i
                                break
                    
                    if brace_count != 0:
                        # Incomplete object — stop searching
                        break
                    
                    json_str = output_to_check[json_start:json_end + 1]
                    try:
                        candidate = json.loads(json_str)
                        if 'TitleList' in candidate:
                            json_data = candidate
                            break
                    except json.JSONDecodeError:
                        pass
                    
                    search_pos = json_end + 1
                
                if json_data is None:
                    # JSON not found — fall back to parsing plain-text stderr
                    self.logger.debug(f"JSON not found for {video_path.name}, trying text fallback")
                    info = self._parse_info_from_stderr(stderr)
                    if info is None:
                        self.logger.warning(f"Could not extract video info from HandBrake output for {video_path.name}")
                        return None
                    return info

                # JSON path succeeded — extract from TitleList
                title_info = json_data.get('TitleList', [{}])[0]
                video_codec = title_info.get('VideoCodec', 'unknown')
                geometry = title_info.get('Geometry', {})
                width  = geometry.get('Width', 0)
                height = geometry.get('Height', 0)
                if width == 0 or height == 0:
                    width  = title_info.get('Width', 0)
                    height = title_info.get('Height', 0)
                framerate = title_info.get('FrameRate', {})
                fps_num = framerate.get('Num', 30)
                fps_den = framerate.get('Den', 1)
                fps = round(fps_num / fps_den) if fps_den > 0 else 30
                audio_codec = 'unknown'
                audio_list = title_info.get('AudioList', [])
                if audio_list:
                    raw_audio = audio_list[0].get('CodecName', '') or audio_list[0].get('Codec', '')
                    audio_codec = self._normalise_audio_codec(raw_audio)
                self.logger.debug(f"JSON: {width}x{height} {fps}fps codec={video_codec} audio={audio_codec}")

                # If JSON returned zeros or unknown, the TitleList was likely empty
                # (can happen when HandBrake scans over SMB).  Try text fallback to fill gaps.
                if (width == 0 or height == 0 or video_codec == 'unknown') and stderr:
                    self.logger.debug(f"JSON TitleList incomplete for {video_path.name}, trying text fallback to fill gaps")
                    fallback = self._parse_info_from_stderr(stderr)
                    if fallback:
                        if width == 0 or height == 0:
                            width  = fallback['width']
                            height = fallback['height']
                            fps    = fallback['fps']
                        if video_codec == 'unknown':
                            video_codec = fallback['codec']
                        if audio_codec == 'unknown':
                            audio_codec = fallback['audio_codec']
                        self.logger.debug(f"After fallback merge: {width}x{height} {fps}fps codec={video_codec} audio={audio_codec}")

                return {
                    'codec': video_codec,
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'audio_codec': audio_codec,
                    'is_hevc': 'hevc' in video_codec.lower() or 'h265' in video_codec.lower() or 'h.265' in video_codec.lower()
                }
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                self.logger.warning(f"Failed to parse video info for {video_path.name}: {e}")
                return None

        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout scanning {video_path.name}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting video info for {video_path.name}: {e}")
            return None
    
    def select_preset(self, width: int, height: int, fps: int) -> str:
        """Select appropriate HandBrake preset based on video properties"""
        # Round fps to nearest common value
        if fps > 50:
            fps_key = 60
        elif fps > 25:
            fps_key = 30
        else:
            fps_key = 24
        
        # Try exact match first
        key = (width, height, fps_key)
        if key in PRESET_MAP:
            return PRESET_MAP[key]
        
        # Try resolution match with different fps
        for (w, h, f), preset in PRESET_MAP.items():
            if w == width and h == height:
                return preset
        
        # Fall back to closest resolution
        if height >= 2160:
            return "H.265 MKV 2160p30 4K"
        elif height >= 1080:
            return "H.265 MKV 1080p30"
        elif height >= 720:
            return "H.265 MKV 720p30"
        else:
            return "H.265 MKV 480p30"
    
    def _build_output_filename(self, stem: str, video_info: Dict) -> str:
        """Build the output filename stem using the naming convention.

        Rules:
        - Strip any old bracket-style suffix: [1080p30 HEVC]
        - Strip existing codec/resolution/audio tags in dash-separated segments
          so we can replace them with accurate detected values.
        - Preserve source tag (Bluray, WEBRip, HDTV, etc.) if present.
        - Append: - <source-if-present><resolution> - x265 <audio>
          e.g. "Movie (2020) - Bluray-1080p - x265 AC3"
               "Show - S01E01 - Title - 720p - x265 AAC"
        """
        # --- 1. Remove old bracket-style suffix ---
        stem = re.sub(r'\s*\[.*?HEVC\]', '', stem, flags=re.IGNORECASE).rstrip()

        # --- 2. Split into dash-separated segments and strip codec/resolution/audio ---
        # Patterns to recognise and remove from trailing segments
        VIDEO_CODEC_PAT  = re.compile(r'\bx26[45]\b|\bh\.?26[45]\b|\bxvid\b|\bdivx\b|\bmpeg[24]?\b|\bvc-?1\b|\bvp[89]\b|\bav1\b', re.IGNORECASE)
        AUDIO_CODEC_PAT  = re.compile(r'\b(truehd|dts[-_]?hd|dts|eac3|e[-\s]ac[-\s]?3|ac3|aac|mp3|flac|lpcm|pcm)\b', re.IGNORECASE)
        RESOLUTION_PAT   = re.compile(r'\b\d{3,4}p\b', re.IGNORECASE)
        # Source tags — keep the text but we'll rebuild the segment
        SOURCE_PAT       = re.compile(r'\b(bluray|blu-ray|bdrip|brrip|webrip|web-dl|webdl|web|hdtv|dvdrip|dvd|hdrip|remux|uhd)\b', re.IGNORECASE)

        segments = [s.strip() for s in stem.split(' - ')]

        # Walk from the end, dropping segments that are purely codec/resolution/audio info
        # Stop as soon as we hit a segment that looks like meaningful title content
        clean_segments = list(segments)
        while clean_segments:
            last = clean_segments[-1]
            # A segment is a "tag-only" segment if, after removing known tags, nothing meaningful remains
            stripped = VIDEO_CODEC_PAT.sub('', last)
            stripped = AUDIO_CODEC_PAT.sub('', stripped)
            stripped = RESOLUTION_PAT.sub('', stripped)
            stripped = SOURCE_PAT.sub('', stripped)
            stripped = re.sub(r'[-\s]', '', stripped).strip()
            if stripped == '':
                clean_segments.pop()
            else:
                break

        # --- 3. Determine source prefix for resolution segment ---
        # Look for a source tag in the last remaining segment or the one we just dropped
        source_prefix = ''
        # Check all original segments for a source tag
        for seg in segments:
            m = SOURCE_PAT.search(seg)
            if m:
                # Normalise capitalisation
                src_map = {
                    'bluray': 'Bluray', 'blu-ray': 'Blu-ray',
                    'bdrip': 'BDRip',   'brrip': 'BRRip',
                    'webrip': 'WEBRip', 'web-dl': 'WEB-DL',
                    'webdl': 'WEB-DL',  'web': 'WEB',
                    'hdtv': 'HDTV',     'dvdrip': 'DVDRip',
                    'dvd': 'DVD',       'hdrip': 'HDRip',
                    'remux': 'Remux',   'uhd': 'UHD',
                }
                source_prefix = src_map.get(m.group(0).lower(), m.group(0)) + '-'
                break

        # --- 4. Build resolution string from actual detected height ---
        # If scan failed to get height, try to read it from the original filename as a fallback
        if video_info['height'] > 0:
            resolution = f"{video_info['height']}p"
        else:
            fn_res = re.search(r'\b(\d{3,4}p)\b', stem, re.IGNORECASE)
            resolution = fn_res.group(1).lower() if fn_res else ''
        audio = video_info.get('audio_codec', 'unknown')

        # --- 5. Reassemble ---
        base = ' - '.join(clean_segments)
        res_seg = f"{source_prefix}{resolution}" if resolution else ''
        codec_seg = f"x265 {audio}" if audio and audio != 'unknown' else 'x265'

        parts = [base]
        if res_seg:
            parts.append(res_seg)
        parts.append(codec_seg)

        return ' - '.join(parts)

    def find_video_files(self) -> List[Path]:
        """Recursively find all video files in source directory"""
        self.logger.info(f"Scanning for video files in: {self.source_dir}")
        video_files = []
        skipped_encoded = 0
        skipped_processed = 0
        
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in VIDEO_EXTENSIONS:
                    # Skip if already in processed list (resume feature)
                    if str(file_path) in self.processed_files:
                        skipped_processed += 1
                        continue
                    
                    # Skip if filename indicates already encoded
                    if self.skip_encoded and self._is_already_encoded(file):
                        skipped_encoded += 1
                        self.logger.debug(f"Skipping already encoded: {file}")
                        continue
                    
                    video_files.append(file_path)
        
        self.logger.info(f"Found {len(video_files)} video files to process")
        if skipped_processed > 0:
            self.logger.info(f"Skipped {skipped_processed} already processed files (resume)")
        if skipped_encoded > 0:
            self.logger.info(f"Skipped {skipped_encoded} already encoded files")
        
        self.stats['skipped_encoded'] = skipped_encoded
        return video_files
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def reencode_video(self, video_path: Path,
                       file_index: int = 0, total_files: int = 0) -> bool:
        """Reencode a single video file to HEVC"""
        try:
            self.logger.info(f"\n{'='*80}")
            if file_index and total_files:
                self.logger.info(f"Processing file {file_index} of {total_files}: {video_path}")
            else:
                self.logger.info(f"Processing: {video_path}")
            
            # Get video information
            video_info = self.get_video_info(video_path)
            if not video_info:
                self.logger.error(f"Could not get video info, skipping: {video_path.name}")
                self.stats['failed'] += 1
                return False
            
            # Check if already HEVC
            if video_info['is_hevc']:
                self.logger.info(f"Already HEVC encoded, skipping: {video_path.name}")
                self.stats['skipped'] += 1
                return True
            
            # Log video properties
            self.logger.info(f"Codec: {video_info['codec']}")
            self.logger.info(f"Resolution: {video_info['width']}x{video_info['height']}")
            self.logger.info(f"FPS: {video_info['fps']}")
            
            # Select appropriate preset
            preset = self.select_preset(
                video_info['width'], 
                video_info['height'], 
                video_info['fps']
            )
            self.logger.info(f"Selected preset: {preset}")
            
            # Get quality settings
            quality_settings = QUALITY_PRESETS.get(self.quality, QUALITY_PRESETS['balanced'])
            self.logger.info(f"Quality: {self.quality} (CRF: {quality_settings['crf']}, Preset: {quality_settings['preset']})")
            
            # Get original file size
            original_size = video_path.stat().st_size
            self.logger.info(f"Original size: {self.format_size(original_size)}")
            
            if self.dry_run:
                self.logger.info("DRY RUN: Would reencode this file")
                self.stats['processed'] += 1
                return True
            
            # Create temporary output file
            output_path = video_path.parent / f"{video_path.stem}_temp.mkv"
            
            # Build HandBrake command with quality settings
            cmd = [
                self.handbrake_path,
                "-i", str(video_path),
                "-o", str(output_path),
                "--preset", preset,
                "--encoder", self.encoder
            ]
            
            # Add quality settings (CPU encoders only)
            if self.gpu_encoder == 'none':
                cmd.extend([
                    "--encoder-preset", quality_settings['preset'],
                    "--quality", str(quality_settings['crf'])
                ])
            else:
                # GPU encoders use different quality settings
                cmd.extend([
                    "--encoder-preset", "quality",  # or "speed" for faster
                    "--quality", str(quality_settings['crf'])
                ])
            
            self.logger.info("Starting reencoding...")
            self.logger.info(f"Command: {' '.join(cmd)}")

            # Print control instructions banner
            print()
            print("  Controls:  P = Pause    R = Resume    Q = Quit after this file")
            print()

            # Prevent system sleep during encoding
            sleep_prevented = prevent_sleep()
            if sleep_prevented:
                self.logger.info("Sleep prevention enabled during encoding")
            
            # Run HandBrake with real-time progress
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
            )

            # Reset pause state for this file
            self._paused = False

            # Build a queue-position prefix to show alongside HandBrake's own progress
            if file_index and total_files:
                progress_prefix = f"[{file_index}/{total_files}] "
            else:
                progress_prefix = ""

            # quit_now is set by Q keypress — kills HandBrake immediately.
            quit_now = threading.Event()
            # Lines from HandBrake stdout are put here by the reader thread.
            output_queue = queue.Queue()

            def stdout_reader():
                """Read HandBrake stdout into a queue so the main loop isn't blocked."""
                try:
                    for line in process.stdout:
                        output_queue.put(line)
                finally:
                    output_queue.put(None)  # sentinel — EOF

            reader_thread = threading.Thread(target=stdout_reader, daemon=True)
            reader_thread.start()

            # Key-listener thread — watches for P / R / Q while HandBrake runs.
            # Uses msvcrt.kbhit()/getwch() so keypresses are received even while
            # the reader thread is blocking on the stdout pipe.
            last_progress_line = ['']

            def key_listener():
                if sys.platform != 'win32':
                    return
                import msvcrt
                while not quit_now.is_set() and process.poll() is None:
                    if msvcrt.kbhit():
                        key = msvcrt.getwch().upper()
                        if key == 'P' and not self._paused:
                            self._paused = True
                            _suspend_process(process.pid)
                            print(f"\n  *** PAUSED ***  Press R to resume or Q to quit immediately", flush=True)
                        elif key == 'R' and self._paused:
                            self._paused = False
                            _resume_process(process.pid)
                            print(f"\r{progress_prefix}{last_progress_line[0]}", end='', flush=True)
                        elif key == 'Q':
                            quit_now.set()
                            if self._paused:
                                self._paused = False
                                _resume_process(process.pid)
                            print(f"\n  Quitting — terminating encode and keeping original...", flush=True)
                            process.kill()
                    else:
                        threading.Event().wait(0.05)

            listener_thread = threading.Thread(target=key_listener, daemon=True)
            listener_thread.start()

            # Main progress loop — drains the output queue.
            while True:
                try:
                    line = output_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                if line is None:  # EOF sentinel
                    break
                line = line.strip()
                if not line:
                    continue
                if "Encoding:" in line or "%" in line:
                    if not self._paused:
                        last_progress_line[0] = line
                        print(f"\r{progress_prefix}{line}", end='', flush=True)
                else:
                    self.logger.debug(line)

            listener_thread.join(timeout=0.2)
            print()  # New line after progress
            process.wait()

            # Q was pressed — clean up the partial output and stop.
            if quit_now.is_set():
                if output_path.exists():
                    output_path.unlink()
                allow_sleep()
                self.logger.info("Encoding cancelled by user — partial file deleted, original kept.")
                return False
            
            # Re-allow system sleep
            if sleep_prevented:
                allow_sleep()
                self.logger.debug("Sleep prevention disabled")
            
            if process.returncode != 0:
                self.logger.error(f"HandBrake failed with return code {process.returncode}")
                if output_path.exists():
                    output_path.unlink()
                self.stats['failed'] += 1
                # Make sure to re-allow sleep on error
                if sleep_prevented:
                    allow_sleep()
                return False
            
            # Check if output file was created
            if not output_path.exists():
                self.logger.error("Output file was not created")
                self.stats['failed'] += 1
                return False
            
            # Get new file size
            new_size = output_path.stat().st_size
            size_diff = original_size - new_size
            percent_saved = (size_diff / original_size) * 100 if original_size > 0 else 0
            
            self.logger.info(f"New size: {self.format_size(new_size)}")
            self.logger.info(f"Space saved: {self.format_size(size_diff)} ({percent_saved:.1f}%)")

            # If the re-encode is larger than the original, keep the original.
            # This happens when the source is already a high-quality encode and
            # x265 at the chosen CRF can't beat it.
            if new_size >= original_size:
                self.logger.warning(
                    f"Re-encoded file is {self.format_size(new_size - original_size)} "
                    f"larger than original — keeping original, deleting temp file"
                )
                output_path.unlink()
                self.stats['skipped_larger'] += 1
                return True

            # Replace original file with reencoded version
            self.logger.info("Replacing original file...")
            
            # Backup original if requested
            if self.backup_dir:
                if not self._backup_file(video_path):
                    self.logger.warning("Backup failed, but continuing with replacement")
            
            # Delete original
            video_path.unlink()
            
            # Build the new filename using the naming convention
            new_stem = self._build_output_filename(video_path.stem, video_info)
            final_path = video_path.parent / f"{new_stem}.mkv"
            output_path.rename(final_path)
            
            self.logger.info(f"Successfully reencoded: {final_path.name}")
            
            # Add to processed files and save state
            self.processed_files.add(str(video_path))
            self._save_state()
            
            self.stats['processed'] += 1
            self.stats['space_saved'] += size_diff
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error reencoding {video_path.name}: {e}")
            self.stats['failed'] += 1
            # Re-allow system sleep on exception
            allow_sleep()
            # Clean up temp file if it exists
            output_path = video_path.parent / f"{video_path.stem}_temp.mkv"
            if output_path.exists():
                try:
                    output_path.unlink()
                except:
                    pass
            return False
    
    def _process_single_file_wrapper(self, args):
        """Wrapper for parallel processing - unpacks arguments and processes file"""
        video_path, idx, total = args
        try:
            if not TQDM_AVAILABLE and self.parallel == 1:
                self.logger.info(f"\n[{idx}/{total}] Processing file {idx} of {total}")
            return self.reencode_video(video_path)
        except Exception as e:
            self.logger.error(f"Error processing {video_path}: {e}")
            return False
    
    def process_all(self):
        """Process all video files in the source directory"""
        # Check HandBrake installation
        if not self.check_handbrake():
            self.logger.error("Cannot proceed without HandBrakeCLI")
            return
        
        # Find all video files
        video_files = self.find_video_files()
        self.stats['total_files'] = len(video_files)
        
        if not video_files:
            self.logger.info("No video files found to process")
            return
        
        # Process files
        if self.parallel > 1:
            self._process_parallel(video_files)
        else:
            self._process_sequential(video_files)
        
        # Print final statistics
        self.print_statistics()
    
    def _process_sequential(self, video_files: List[Path]):
        """Process files one at a time (original behavior)"""
        self.logger.info(f"\nStarting sequential processing of {len(video_files)} files...")
        
        # Use tqdm progress bar if available
        if TQDM_AVAILABLE and tqdm_progress and not self.dry_run:
            video_iterator = tqdm_progress(video_files, desc="Processing videos", unit="file")
        else:
            video_iterator = video_files
        
        for idx, video_path in enumerate(video_iterator, 1):
            self.reencode_video(video_path, file_index=idx, total_files=len(video_files))
            if self.quit_after_current:
                self.logger.info("Quit requested by user — stopping after current file.")
                break
    
    def _process_parallel(self, video_files: List[Path]):
        """Process multiple files in parallel"""
        self.logger.info(f"\nStarting parallel processing of {len(video_files)} files...")
        self.logger.info(f"Using {self.parallel} parallel workers")
        
        # Prepare arguments for parallel processing
        args_list = [(video_path, idx, len(video_files))
                     for idx, video_path in enumerate(video_files, 1)]
        
        # Use ProcessPoolExecutor for parallel processing
        with ProcessPoolExecutor(max_workers=self.parallel) as executor:
            # Submit all tasks
            futures = {executor.submit(self._process_single_file_wrapper, args): args[0]
                      for args in args_list}
            
            # Use tqdm progress bar if available
            if TQDM_AVAILABLE and tqdm_progress:
                futures_iterator = tqdm_progress(
                    as_completed(futures),
                    total=len(futures),
                    desc="Processing videos",
                    unit="file"
                )
            else:
                futures_iterator = as_completed(futures)
            
            # Process results as they complete
            completed = 0
            for future in futures_iterator:
                completed += 1
                video_path = futures[future]
                try:
                    result = future.result()
                    if not TQDM_AVAILABLE:
                        self.logger.info(f"Completed {completed}/{len(video_files)}: {video_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to process {video_path.name}: {e}")
    
    def print_statistics(self):
        """Print final processing statistics"""
        self.logger.info(f"\n{'='*80}")
        self.logger.info("PROCESSING COMPLETE")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Total files found: {self.stats['total_files']}")
        self.logger.info(f"Successfully processed: {self.stats['processed']}")
        self.logger.info(f"Skipped (already HEVC): {self.stats['skipped']}")
        if self.stats['skipped_encoded'] > 0:
            self.logger.info(f"Skipped (already encoded in filename): {self.stats['skipped_encoded']}")
        if self.stats['skipped_larger'] > 0:
            self.logger.info(f"Skipped (x265 output larger than original): {self.stats['skipped_larger']}")
        self.logger.info(f"Failed: {self.stats['failed']}")
        self.logger.info(f"Total space saved: {self.format_size(self.stats['space_saved'])}")
        if self.backup_dir:
            self.logger.info(f"Backups saved to: {self.backup_dir}")
        self.logger.info(f"{'='*80}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Recursively reencode video files to HEVC/H.265 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all videos in a directory
  python video_reencoder.py /path/to/videos

  # Dry run to see what would be processed
  python video_reencoder.py /path/to/videos --dry-run

  # Use best quality preset with backup
  python video_reencoder.py /path/to/videos --quality best --backup-dir ./backups

  # Process 4 files in parallel (much faster!)
  python video_reencoder.py /path/to/videos --parallel 4

  # Use NVIDIA GPU acceleration (5-10x faster!)
  python video_reencoder.py /path/to/videos --gpu nvenc

  # Combine GPU + parallel for maximum speed
  python video_reencoder.py /path/to/videos --gpu nvenc --parallel 2

  # Resume previous session, skip encoded files
  python video_reencoder.py /path/to/videos --resume --skip-encoded

  # Specify custom HandBrakeCLI path
  python video_reencoder.py /path/to/videos --handbrake-path /usr/local/bin/HandBrakeCLI
        """
    )
    
    parser.add_argument(
        '--version', action='version', version=f'%(prog)s {__version__}'
    )

    parser.add_argument(
        'source_dir',
        help='Source directory containing video files to reencode'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without actually reencoding files'
    )
    
    parser.add_argument(
        '--handbrake-path',
        default='HandBrakeCLI',
        help='Path to HandBrakeCLI executable (default: HandBrakeCLI)'
    )
    
    parser.add_argument(
        '--log-file',
        default='reencoding.log',
        help='Name of the log file (default: reencoding.log)'
    )
    
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Do not resume from previous session (start fresh)'
    )
    
    parser.add_argument(
        '--no-skip-encoded',
        action='store_true',
        help='Do not skip files with [*HEVC] in filename'
    )
    
    parser.add_argument(
        '--backup-dir',
        help='Directory to backup original files before deletion'
    )
    
    parser.add_argument(
        '--quality',
        choices=['fast', 'balanced', 'best'],
        default='balanced',
        help='Encoding quality preset: fast (CRF 28), balanced (CRF 23), best (CRF 20) (default: balanced)'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset state file and start fresh (clears resume data)'
    )
    
    parser.add_argument(
        '--parallel',
        type=int,
        default=1,
        metavar='N',
        help='Number of files to process in parallel (default: 1, max: CPU cores)'
    )
    
    parser.add_argument(
        '--gpu',
        choices=['none', 'nvenc', 'qsv', 'vce', 'videotoolbox'],
        default='none',
        help='GPU encoder: nvenc (NVIDIA), qsv (Intel), vce (AMD), videotoolbox (Apple), none (CPU) (default: none)'
    )
    
    args = parser.parse_args()
    
    # Validate source directory
    if not os.path.isdir(args.source_dir):
        print(f"Error: Source directory does not exist: {args.source_dir}")
        sys.exit(1)
    
    # Handle reset flag
    if args.reset:
        state_file = Path(args.source_dir) / '.reencoding_state.json'
        if state_file.exists():
            state_file.unlink()
            print(f"Reset: Cleared state file")
    
    # Show warning if tqdm not available
    if not TQDM_AVAILABLE:
        print("Note: Install 'tqdm' for progress bars: pip install tqdm")
    
    # Validate parallel workers
    if args.parallel > 1:
        max_workers = multiprocessing.cpu_count()
        if args.parallel > max_workers:
            print(f"Warning: Requested {args.parallel} workers, but only {max_workers} CPU cores available")
            print(f"Using {max_workers} workers instead")
            args.parallel = max_workers
    
    # Create reencoder instance and process
    reencoder = VideoReencoder(
        source_dir=args.source_dir,
        log_file=args.log_file,
        dry_run=args.dry_run,
        handbrake_path=args.handbrake_path,
        resume=not args.no_resume,
        skip_encoded=not args.no_skip_encoded,
        backup_dir=args.backup_dir,
        quality=args.quality,
        parallel=args.parallel,
        gpu_encoder=args.gpu
    )
    
    try:
        reencoder.process_all()
    except KeyboardInterrupt:
        reencoder.logger.info("\n\nProcess interrupted by user")
        reencoder.print_statistics()
        sys.exit(0)
    except Exception as e:
        reencoder.logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
