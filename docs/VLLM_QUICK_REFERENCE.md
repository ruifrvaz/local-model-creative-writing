# Quick Reference - vLLM Server

## 🚀 Common Commands

### Start Server (Default: Llama-3.1-8B-Instruct)
```bash
./serve_vllm.sh
```

### Start with Different Model
```bash
./serve_vllm.sh "Qwen/Qwen2.5-14B-Instruct"
./serve_vllm.sh "casperhansen/qwen2.5-14b-instruct-awq"
```

### Stop Server
```bash
./stop_vllm.sh
# or Ctrl+C if running in foreground
```

### Health Checks
```bash
./vllm/health_checks/9_health.sh          # API endpoint validation
./vllm/health_checks/10_concurrency.sh    # Parallel request testing
./vllm/health_checks/13_sanity_snapshot.sh # Environment snapshot
```

### Monitor GPU
```bash
watch -n 1 nvidia-smi
```

---

## 📡 API Endpoints

**Base URL:** http://localhost:8000

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Chat (OpenAI-compatible) |
| `/v1/completions` | POST | Text completion |
| `/docs` | GET | API documentation |
| `/metrics` | GET | Prometheus metrics |

---

## 🧪 Quick Tests

### Health Check
```bash
curl http://localhost:8000/health
```

### List Models
```bash
curl http://localhost:8000/v1/models
```

### Simple Chat
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

---

## 🔧 Configuration

### Installed Versions
```
Python:       3.12.3
PyTorch:      2.8.0 (CUDA 12.8)
vLLM:         0.10.2
FlashInfer:   0.3.0
Transformers: 4.55.4
NumPy:        1.26.4
```

### Environment Variables
```bash
VLLM_ATTENTION_BACKEND=FLASHINFER
PATH=/usr/local/cuda/bin:$PATH
LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

### Server Settings
```
Port:           8000
Max Context:    32,768 tokens
GPU Util:       90% (28.66GB / 32GB)
Max Concurrent: 16 requests
Backend:        FlashInfer
```

---

## 📁 Important Paths

```
Virtual Env:     ~/.venvs/llm
Scripts:         ~/scifi-llm/scripts
Model Cache:     ~/.cache/huggingface/hub
Torch Cache:     ~/.cache/torch_extensions
vLLM Cache:      ~/.cache/vllm/torch_compile_cache
HF Token:        ~/.cache/huggingface/token
```

---

## 🎯 Recommended Models

### English Fiction Writing
- `meta-llama/Llama-3.1-8B-Instruct` ⭐ (Default, 16GB VRAM)
- `Qwen/Qwen2.5-14B-Instruct` (28GB VRAM, best quality)
- `casperhansen/qwen2.5-14b-instruct-awq` (10GB VRAM, quantized)

### RAG Applications  
- `casperhansen/llama-3.1-8b-instruct-awq` (6GB VRAM)
- `Qwen/Qwen2.5-7B-Instruct` (14GB VRAM)

---

## 🔍 Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Kill existing process
pkill -f "vllm serve"

# Check GPU availability
nvidia-smi

# Activate virtual environment
source ~/.venvs/llm/bin/activate
```

### Out of Memory
```bash
# Use smaller model
./serve_vllm.sh "casperhansen/llama-3.1-8b-instruct-awq"

# Or reduce GPU utilization
# Edit serve_vllm.sh: --gpu-memory-utilization 0.80
```

### Slow First Run
- First run downloads model (~16GB for Llama-3.1-8B)
- Compiles CUDA kernels for RTX 5090 (~30-60s)
- Subsequent runs much faster (~30s)

---

## 📊 Performance Tips

1. **Use AWQ Quantized Models** - Same quality, 40-50% less VRAM
2. **FlashInfer Enabled** - 2-4x faster attention (already configured)
3. **Batch Requests** - Send multiple requests together
4. **Monitor Metrics** - Check `/metrics` endpoint

---

## 🆘 Getting Help

### Check Logs
Server runs in foreground - see output directly

### Common Issues

**"CUDA out of memory"**
→ Use smaller model or AWQ quantized version

**"Authentication required"**
→ Run `./0_hf_login.sh` first

**"Port 8000 already in use"**
→ `pkill -f "vllm serve"` then retry

**"FlashInfer not found"**
→ Check `echo $VLLM_ATTENTION_BACKEND` (should be FLASHINFER)

