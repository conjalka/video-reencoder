# GPU Acceleration Guide

## 🚀 Overview

GPU acceleration can make video encoding **5-10x faster** than CPU encoding by offloading the work to your graphics card. This guide explains how to use GPU acceleration with the video reencoder.

## ⚡ Performance Comparison

| Method | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| **CPU (x265)** | 1x (baseline) | Excellent | Best quality, slower |
| **NVIDIA (nvenc)** | 5-8x faster | Very Good | NVIDIA GPUs |
| **Intel (qsv)** | 3-5x faster | Very Good | Intel CPUs with iGPU |
| **AMD (vce)** | 4-6x faster | Very Good | AMD GPUs |
| **Apple (videotoolbox)** | 6-10x faster | Very Good | Apple Silicon Macs |

### Example: 1-hour 1080p Video

| Encoder | Encoding Time | Speedup |
|---------|---------------|---------|
| CPU (x265) | ~35 minutes | 1x |
| NVIDIA GPU | ~5 minutes | 7x |
| Intel QSV | ~8 minutes | 4.4x |
| AMD VCE | ~6 minutes | 5.8x |
| Apple M1/M2 | ~4 minutes | 8.8x |

## 🎮 Supported GPU Encoders

### 1. NVIDIA (nvenc)
- **Requirements**: NVIDIA GPU (GTX 600 series or newer)
- **Best for**: NVIDIA graphics cards
- **Quality**: Excellent (near x265 quality)
- **Speed**: 5-8x faster than CPU

**Usage:**
```bash
python video_reencoder.py /path/to/videos --gpu nvenc
```

### 2. Intel QuickSync (qsv)
- **Requirements**: Intel CPU with integrated graphics (6th gen or newer)
- **Best for**: Intel systems with iGPU
- **Quality**: Very good
- **Speed**: 3-5x faster than CPU

**Usage:**
```bash
python video_reencoder.py /path/to/videos --gpu qsv
```

### 3. AMD VCE (vce)
- **Requirements**: AMD GPU (Radeon HD 7000 series or newer)
- **Best for**: AMD graphics cards
- **Quality**: Very good
- **Speed**: 4-6x faster than CPU

**Usage:**
```bash
python video_reencoder.py /path/to/videos --gpu vce
```

### 4. Apple VideoToolbox (videotoolbox)
- **Requirements**: macOS with Apple Silicon (M1/M2/M3) or Intel Mac
- **Best for**: Mac computers
- **Quality**: Excellent
- **Speed**: 6-10x faster than CPU

**Usage:**
```bash
python video_reencoder.py /path/to/videos --gpu videotoolbox
```

## 📋 How to Check Your GPU

### Windows
```powershell
# Check NVIDIA GPU
nvidia-smi

# Check AMD GPU
wmic path win32_VideoController get name

# Check Intel iGPU
wmic path win32_VideoController get name
```

### macOS
```bash
# Check GPU
system_profiler SPDisplaysDataType
```

### Linux
```bash
# Check NVIDIA GPU
lspci | grep -i nvidia

# Check AMD GPU
lspci | grep -i amd

# Check Intel iGPU
lspci | grep -i intel
```

## 🔧 Setup Instructions

### NVIDIA (nvenc)

**Windows:**
1. Install latest NVIDIA drivers from nvidia.com
2. Verify: `nvidia-smi` should show your GPU

**Linux:**
```bash
# Install NVIDIA drivers
sudo apt install nvidia-driver-XXX  # Replace XXX with version

# Verify
nvidia-smi
```

**macOS:**
Not applicable (NVIDIA GPUs not supported on modern Macs)

### Intel QuickSync (qsv)

**Windows:**
1. Install latest Intel graphics drivers
2. Enable iGPU in BIOS if you have dedicated GPU

**Linux:**
```bash
# Install Intel media driver
sudo apt install intel-media-va-driver

# Verify
vainfo
```

### AMD VCE (vce)

**Windows:**
1. Install latest AMD drivers from amd.com
2. Verify in Device Manager

**Linux:**
```bash
# Install AMD drivers
sudo apt install mesa-va-drivers

# Verify
vainfo
```

### Apple VideoToolbox (videotoolbox)

**macOS:**
- Built-in, no setup required
- Works on all Macs (Intel and Apple Silicon)
- Best performance on Apple Silicon (M1/M2/M3)

## 💡 Usage Examples

### Basic GPU Encoding

**NVIDIA:**
```bash
python video_reencoder.py /path/to/videos --gpu nvenc
```

**Intel:**
```bash
python video_reencoder.py /path/to/videos --gpu qsv
```

**AMD:**
```bash
python video_reencoder.py /path/to/videos --gpu vce
```

**Apple:**
```bash
python video_reencoder.py /path/to/videos --gpu videotoolbox
```

### Combined with Other Features

**GPU + Parallel Processing:**
```bash
# Process 2 files at once with GPU (super fast!)
python video_reencoder.py /path/to/videos --gpu nvenc --parallel 2
```

**GPU + Best Quality:**
```bash
python video_reencoder.py /path/to/videos --gpu nvenc --quality best
```

**GPU + Backup:**
```bash
python video_reencoder.py /path/to/videos --gpu nvenc --backup-dir ./backups
```

**Maximum Speed Setup:**
```bash
# GPU + parallel + fast quality = MAXIMUM SPEED
python video_reencoder.py /path/to/videos \
  --gpu nvenc \
  --parallel 2 \
  --quality fast
```

## 🎯 Recommendations

### For NVIDIA Users
```bash
# Recommended: GPU + 2 parallel workers
python video_reencoder.py /path/to/videos --gpu nvenc --parallel 2
```
- Use 2 parallel workers (GPU can handle multiple streams)
- Balanced quality is fine (GPU quality is already good)

### For Intel Users
```bash
# Recommended: GPU only (QSV doesn't benefit much from parallel)
python video_reencoder.py /path/to/videos --gpu qsv
```
- Use single worker (QSV has limited parallel capability)
- Quality preset doesn't affect GPU much

### For AMD Users
```bash
# Recommended: GPU + 2 parallel workers
python video_reencoder.py /path/to/videos --gpu vce --parallel 2
```
- Similar to NVIDIA recommendations
- 2 parallel workers for best throughput

### For Apple Users
```bash
# Recommended: GPU + parallel (Apple Silicon is very fast)
python video_reencoder.py /path/to/videos --gpu videotoolbox --parallel 3
```
- Apple Silicon can handle 3-4 parallel streams
- VideoToolbox is extremely efficient

## ⚠️ Important Notes

### Quality Considerations
- GPU encoding is slightly lower quality than CPU (x265)
- Difference is usually imperceptible for most content
- File sizes may be 5-15% larger than CPU encoding
- Trade-off: Much faster speed for slightly larger files

### When to Use CPU vs GPU

**Use CPU (x265) when:**
- Maximum quality is critical
- Smallest possible file size needed
- Archival/preservation purposes
- You have time to wait

**Use GPU when:**
- Speed is important
- Processing large libraries
- Quality is "good enough"
- You want faster turnaround

### Limitations

**NVIDIA nvenc:**
- Requires GTX 600 series or newer
- Some older GPUs have encoding limits (3 streams max)
- Quality presets work differently than CPU

**Intel QSV:**
- Requires 6th gen Intel or newer
- Must have iGPU enabled in BIOS
- Limited parallel capability

**AMD VCE:**
- Requires Radeon HD 7000 or newer
- Driver support varies by Linux distro
- Quality can vary by GPU generation

**Apple VideoToolbox:**
- macOS only
- Best on Apple Silicon
- Intel Macs are slower but still faster than CPU

## 🔍 Troubleshooting

### "Encoder not found" Error

**Problem:** HandBrake can't find the GPU encoder

**Solutions:**
1. Update GPU drivers
2. Verify GPU is detected by system
3. Try CPU encoding first to verify HandBrake works
4. Check HandBrake supports your GPU model

### Poor Quality Output

**Problem:** GPU encoded videos look worse than expected

**Solutions:**
1. Use `--quality best` for better quality
2. Try different GPU encoder if available
3. Fall back to CPU encoding for critical content

### Slow GPU Encoding

**Problem:** GPU encoding isn't faster than CPU

**Solutions:**
1. Update GPU drivers
2. Close other GPU-intensive applications
3. Check GPU isn't thermal throttling
4. Verify GPU is actually being used (check GPU usage)

### Out of Memory Errors

**Problem:** GPU runs out of memory

**Solutions:**
1. Reduce parallel workers
2. Close other applications using GPU
3. Process lower resolution videos first
4. Fall back to CPU encoding

## 📊 Performance Tips

### Maximize GPU Performance

1. **Update Drivers**: Always use latest GPU drivers
2. **Close Other Apps**: Free up GPU memory
3. **Monitor Temperature**: Ensure good cooling
4. **Use Parallel**: GPU can handle 2-3 streams
5. **Batch Processing**: Process overnight for large libraries

### Optimal Settings by GPU

**High-End NVIDIA (RTX 3000/4000):**
```bash
python video_reencoder.py /path/to/videos --gpu nvenc --parallel 3 --quality balanced
```

**Mid-Range NVIDIA (GTX 1000/2000):**
```bash
python video_reencoder.py /path/to/videos --gpu nvenc --parallel 2 --quality balanced
```

**Intel iGPU:**
```bash
python video_reencoder.py /path/to/videos --gpu qsv --quality balanced
```

**AMD GPU:**
```bash
python video_reencoder.py /path/to/videos --gpu vce --parallel 2 --quality balanced
```

**Apple Silicon:**
```bash
python video_reencoder.py /path/to/videos --gpu videotoolbox --parallel 4 --quality balanced
```

## 🎓 Advanced Usage

### Test GPU Performance

```bash
# Test with single file first
python video_reencoder.py /path/to/single/video --gpu nvenc --dry-run

# Then process full library
python video_reencoder.py /path/to/videos --gpu nvenc
```

### Compare CPU vs GPU

```bash
# Encode with CPU
python video_reencoder.py /path/to/test --quality balanced

# Encode with GPU
python video_reencoder.py /path/to/test --gpu nvenc --quality balanced

# Compare file sizes and quality
```

### Monitor GPU Usage

**Windows:**
- Task Manager → Performance → GPU
- GPU-Z for detailed monitoring

**Linux:**
```bash
# NVIDIA
nvidia-smi -l 1

# AMD
radeontop

# Intel
intel_gpu_top
```

**macOS:**
- Activity Monitor → GPU History
- iStat Menus for detailed monitoring

## 📝 Summary

- **GPU encoding is 5-10x faster** than CPU
- **Quality is very good** (slightly lower than CPU)
- **File sizes are 5-15% larger** than CPU encoding
- **Perfect for large libraries** where speed matters
- **Use `--gpu nvenc/qsv/vce/videotoolbox`** to enable

**Recommended command for most users:**
```bash
python video_reencoder.py /path/to/videos --gpu nvenc --parallel 2
```

---

**Happy fast encoding! 🚀**