# Flash-Attention Installation: WSL Memory Issue Resolution

**Date:** November 2, 2025  
**Category:** Environment setup / WSL resource configuration  
**Impact:** Critical WSL configuration required for flash-attention compilation

## Problem

Flash-attention installation repeatedly crashed WSL2 during compilation phase.

**Symptoms:**
- WSL crash when attempting parallel compilation
- Occurs during `pip install flash-attn --no-build-isolation`
- Compilation phase requires significant memory/CPU resources

**Initial attempts:**
- Default WSL memory allocation insufficient
- Increasing parallelization (`MAX_JOBS > 1`) triggered crashes

## Root Cause

Flash-attention compiles C++/CUDA kernels from source when no pre-built wheel available. Compilation is:
- **Memory intensive:** Each compilation job uses ~2-4GB RAM
- **CPU intensive:** Ninja build system defaults to all available cores
- **WSL resource constrained:** Default WSL limits too low for parallel builds

**WSL default limits (insufficient):**
- Memory: 50% of system RAM (32GB on 64GB system)
- Processors: All logical cores (but memory becomes bottleneck)

## Solution

### Step 1: Configure WSL Resource Limits

Created/modified `C:\Users\<username>\.wslconfig` (Windows path):

```ini
[wsl2]
memory=48GB          # Increased from default 32GB
processors=12        # Explicit CPU allocation
```

**Rationale:**
- 48GB allows ~12 parallel jobs at 4GB each
- Leaves 16GB for Windows OS
- 12 processors balances compilation speed vs stability

### Step 2: Force Single-Threaded Compilation

Even with increased WSL resources, parallel compilation remained unstable.

**Modified `fine-tuning/setup/3_install_training_stack.sh`:**

```bash
export MAX_JOBS=1  # ULTRA-CONSERVATIVE: Single-threaded to prevent OOM
```

**Before (caused crashes):**
```bash
export MAX_JOBS=$(nproc)  # Used all cores (~24 threads)
```

### Step 3: Restart WSL

WSL requires full restart to apply `.wslconfig` changes:

```powershell
# Windows PowerShell (run as administrator)
wsl --shutdown
wsl
```

### Step 4: Install Flash-Attention

```bash
source ~/.venvs/finetune/bin/activate
cd fine-tuning/setup
./3_install_training_stack.sh
```

**Result:**
- Compilation succeeded with `MAX_JOBS=1`
- Installation time: ~15-20 minutes (vs ~3-5 minutes with parallel build)
- No WSL crashes
- Flash-attention functional after installation

## Technical Details

**Flash-attention compilation requirements:**
- CUDA toolkit 12.8
- Ninja build system
- GCC/G++ compiler
- PyTorch headers (for CUDA API compatibility)

**Memory consumption during build:**
- Single job: ~2-4GB RAM
- 4 parallel jobs: ~8-16GB RAM
- 8+ parallel jobs: Exceeded WSL limits, caused OOM crashes

**Why `MAX_JOBS=1` works:**
- Single compilation thread uses ~4GB max
- Well within 48GB WSL allocation
- Avoids memory fragmentation from parallel builds
- Stable but slower compilation

## Files Modified

**WSL configuration (Windows):**
- Created: `C:\Users\<username>\.wslconfig`
- Contents: 48GB memory, 12 processors

**Setup script:**
- Modified: `fine-tuning/setup/3_install_training_stack.sh`
- Changed: `export MAX_JOBS=1` (previously dynamic based on `nproc`)
- Added: Comment explaining ultra-conservative setting

## Verification

After installation, verify flash-attention works:

```bash
source ~/.venvs/finetune/bin/activate
python -c "import flash_attn; print(flash_attn.__version__)"
# Expected output: 2.x.x (version number)
```

## Lessons Learned

1. **WSL resource limits are critical** for memory-intensive builds
2. **Parallel compilation != always faster** when memory-constrained
3. **Single-threaded builds are reliable** even if slower
4. **`.wslconfig` requires WSL restart** to take effect
5. **Default WSL limits insufficient** for ML/AI development

## Alternative Solutions (Not Attempted)

If `MAX_JOBS=1` still fails:

1. **Use pre-built wheels:**
   ```bash
   pip install flash-attn --find-links https://github.com/Dao-AILab/flash-attention/releases
   ```
   - Faster installation (30 seconds vs 15-20 minutes)
   - Requires exact PyTorch/CUDA version match

2. **Increase swap space:**
   ```bash
   # In WSL
   sudo fallocate -l 32G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```
   - Allows memory overflow to disk
   - Much slower than RAM

3. **Install in native Linux** (not WSL):
   - No resource limits from Windows
   - Full hardware access
   - More stable for heavy compilation

## Impact on Other Components

**vLLM environment (`~/.venvs/llm`):**
- Already uses pre-built flash-attention wheel
- Not affected by this issue
- No recompilation needed

**RAG environment (`~/.venvs/rag`):**
- Doesn't use flash-attention
- Not affected

## Recommendations

**For future ML environments:**
1. Always configure `.wslconfig` before heavy compilation
2. Start with `MAX_JOBS=1`, increase if stable
3. Monitor memory usage: `watch -n 1 free -h`
4. Use pre-built wheels when available

**WSL configuration for ML development:**
```ini
[wsl2]
memory=48GB              # For 64GB system
processors=12            # Balance speed/stability  
swap=32GB                # Emergency overflow
localhostForwarding=true # For API servers
```

## Next Steps

Flash-attention now installed and functional. Resume training workflow:

```bash
source ~/.venvs/finetune/bin/activate
cd fine-tuning/training
./2_train_lora.sh
```

Expected: Training completes without flash-attention import errors.
