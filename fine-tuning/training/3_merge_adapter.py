#!/usr/bin/env python3
"""
Merge LoRA/QLoRA Adapter with Base Model

Combines trained adapter weights with base model to create a standalone model for vLLM deployment.

Input:  checkpoints/{run_name}/checkpoint-{step}/  (adapter weights + config)
Output: merged_models/{model_name}/               (full model ready for inference)

Usage:
    # Activate finetune environment first
    source ~/.venvs/finetune/bin/activate
    
    # Merge specific checkpoint
    python 3_merge_adapter.py \
        --checkpoint ../checkpoints/qlora-style-pipeline-test/checkpoint-5 \
        --output ../merged_models/llama-3.1-8b-scifi-style
    
    # Auto-select best checkpoint
    python 3_merge_adapter.py \
        --checkpoint ../checkpoints/qlora-style-pipeline-test \
        --auto-select \
        --output ../merged_models/llama-3.1-8b-scifi-style
    
    # Quick merge with defaults
    python 3_merge_adapter.py --auto

Note: 
  - Merged model will be ~15GB for Llama-3.1-8B
  - Script disables AWQ (not needed for QLoRA/LoRA, uses bitsandbytes)
  - Handles vocab size mismatches from training-added special tokens
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Check if running in correct virtual environment
def check_venv():
    """Verify script is running in finetune venv."""
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    if 'finetune' not in venv_path:
        print("[ERROR] This script must run in the finetune virtual environment!")
        print("   Please run: source ~/.venvs/finetune/bin/activate")
        print(f"   Current env: {venv_path or 'None'}")
        sys.exit(1)

check_venv()

# Disable AWQ to avoid import conflicts (not needed for QLoRA/LoRA merge)
# AWQ is for quantized inference, not training/merging
import os
os.environ['DISABLE_AWQ'] = '1'

# Now import ML libraries (after venv check)
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig


def find_checkpoints(run_dir: Path) -> list[Path]:
    """Find all checkpoint directories in a training run.
    
    Returns sorted list of checkpoint paths (by step number).
    """
    checkpoints = []
    for item in run_dir.iterdir():
        if item.is_dir() and item.name.startswith('checkpoint-'):
            # Verify checkpoint has required files
            if (item / 'adapter_config.json').exists():
                checkpoints.append(item)
    
    # Sort by checkpoint number
    checkpoints.sort(key=lambda x: int(x.name.split('-')[1]))
    return checkpoints


def select_best_checkpoint(checkpoints: list[Path]) -> Optional[Path]:
    """Select best checkpoint based on training metadata.
    
    Strategy:
    1. Use final checkpoint if validation loss decreased
    2. Otherwise use checkpoint with lowest validation loss
    3. Fall back to final checkpoint if no validation data
    """
    if not checkpoints:
        return None
    
    # Try to find trainer_state.json in checkpoints
    checkpoint_losses = []
    for ckpt in checkpoints:
        trainer_state = ckpt / 'trainer_state.json'
        if trainer_state.exists():
            try:
                with open(trainer_state) as f:
                    state = json.load(f)
                    # Get validation loss from log history
                    val_losses = [
                        entry['eval_loss'] 
                        for entry in state.get('log_history', [])
                        if 'eval_loss' in entry
                    ]
                    if val_losses:
                        checkpoint_losses.append((ckpt, val_losses[-1]))
            except Exception as e:
                print(f"[WARN] Failed to read {trainer_state}: {e}")
    
    if checkpoint_losses:
        # Return checkpoint with lowest validation loss
        best_ckpt = min(checkpoint_losses, key=lambda x: x[1])
        print(f"[AUTO] Selected checkpoint with lowest val_loss: {best_ckpt[1]:.4f}")
        return best_ckpt[0]
    
    # Fall back to final checkpoint
    print(f"[AUTO] No validation data found, using final checkpoint")
    return checkpoints[-1]


def verify_checkpoint(checkpoint_path: Path) -> bool:
    """Verify checkpoint has required files."""
    required_files = ['adapter_config.json']
    
    # Check for weight files (either .safetensors or .bin)
    has_weights = (
        any(checkpoint_path.glob('adapter_model.safetensors')) or
        any(checkpoint_path.glob('adapter_model.bin')) or
        any(checkpoint_path.glob('*.safetensors'))
    )
    
    has_config = all((checkpoint_path / f).exists() for f in required_files)
    
    if not has_config:
        print(f"[ERROR] Missing adapter_config.json in {checkpoint_path}")
        return False
    
    if not has_weights:
        print(f"[ERROR] Missing adapter weight files in {checkpoint_path}")
        print(f"   Expected: adapter_model.safetensors or adapter_model.bin")
        return False
    
    return True


def get_base_model_from_config(checkpoint_path: Path) -> str:
    """Extract base model name from adapter config."""
    config_path = checkpoint_path / 'adapter_config.json'
    with open(config_path) as f:
        config = json.load(f)
    return config.get('base_model_name_or_path', 'meta-llama/Llama-3.1-8B-Instruct')


def merge_adapter(
    checkpoint_path: Path,
    output_path: Path,
    base_model: Optional[str] = None,
    dtype: str = 'bfloat16'
):
    """Merge LoRA/QLoRA adapter with base model.
    
    Args:
        checkpoint_path: Path to checkpoint directory with adapter weights
        output_path: Path to save merged model
        base_model: Base model name (auto-detected from config if None)
        dtype: Data type for merged model (bfloat16, float16, float32)
    """
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Merging LoRA Adapter with Base Model")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Verify checkpoint
    if not verify_checkpoint(checkpoint_path):
        print("[ERROR] Invalid checkpoint directory")
        sys.exit(1)
    
    # Get base model name
    if base_model is None:
        base_model = get_base_model_from_config(checkpoint_path)
    
    print(f"Checkpoint:  {checkpoint_path}")
    print(f"Base model:  {base_model}")
    print(f"Output:      {output_path}")
    print(f"Data type:   {dtype}")
    print("")
    
    # Set dtype
    torch_dtype = {
        'bfloat16': torch.bfloat16,
        'float16': torch.float16,
        'float32': torch.float32
    }[dtype]
    
    # Load base model
    print("[STEP 1/5] Loading base model...")
    print(f"   Model: {base_model}")
    print(f"   This may take 2-5 minutes for 8B models...")
    
    base_model_obj = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch_dtype,
        device_map='auto',
        low_cpu_mem_usage=True,
        quantization_config=None  # Explicitly disable quantization
    )
    print(f"[OK] Base model loaded ({base_model_obj.num_parameters():,} parameters)")
    
    # Load tokenizer
    print("\n[STEP 2/5] Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    
    # Load adapter tokenizer to check for vocab size differences
    adapter_tokenizer = AutoTokenizer.from_pretrained(str(checkpoint_path))
    
    # Resize embeddings if needed (handles added special tokens during training)
    if len(adapter_tokenizer) != len(tokenizer):
        print(f"[INFO] Vocab size mismatch detected:")
        print(f"   Base model: {len(tokenizer)} tokens")
        print(f"   Adapter: {len(adapter_tokenizer)} tokens")
        
        # Check if it's the common unk_token issue
        if len(adapter_tokenizer) == len(tokenizer) + 1:
            base_vocab = set(tokenizer.get_vocab().keys())
            adapter_vocab = set(adapter_tokenizer.get_vocab().keys())
            new_tokens = adapter_vocab - base_vocab
            if '<unk>' in new_tokens:
                print(f"   Cause: Training config added <unk> token (unnecessary for Llama 3.1)")
                print(f"   Impact: None (byte-level tokenizer won't use it)")
        
        print(f"   Resizing base model embeddings...")
        base_model_obj.resize_token_embeddings(len(adapter_tokenizer))
        tokenizer = adapter_tokenizer  # Use adapter's tokenizer
    
    print("[OK] Tokenizer loaded")
    
    # Load adapter
    print("\n[STEP 3/5] Loading LoRA adapter...")
    print(f"   Adapter: {checkpoint_path}")
    
    model_with_adapter = PeftModel.from_pretrained(
        base_model_obj,
        str(checkpoint_path),
        torch_dtype=torch_dtype,
        is_trainable=False  # Inference mode
    )
    print("[OK] Adapter loaded")
    
    # Merge weights
    print("\n[STEP 4/5] Merging adapter weights into base model...")
    print("   This combines LoRA deltas with base weights...")
    
    merged_model = model_with_adapter.merge_and_unload()
    print("[OK] Merge complete")
    
    # Save merged model
    print(f"\n[STEP 5/5] Saving merged model to {output_path}...")
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("   Saving model weights...")
    merged_model.save_pretrained(
        str(output_path),
        safe_serialization=True,  # Use safetensors format
        max_shard_size="5GB"      # Shard large models
    )
    
    print("   Saving tokenizer...")
    tokenizer.save_pretrained(str(output_path))
    
    # Save metadata
    metadata = {
        'base_model': base_model,
        'adapter_checkpoint': str(checkpoint_path),
        'dtype': dtype,
        'merged_with': '3_merge_adapter.py'
    }
    
    with open(output_path / 'merge_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[OK] Merged model saved to {output_path}")
    
    # Summary
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Merge Complete")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Model location: {output_path}")
    print(f"Model size:     ~15GB (for 8B model)")
    print("")
    print("Next steps:")
    print(f"  1. Test in vLLM:")
    print(f"     cd ~/scifi-llm")
    print(f"     ./serve_vllm.sh \"{output_path.relative_to(Path.cwd().parent.parent)}\" 8000 9 64000")
    print("")
    print(f"  2. Benchmark quality:")
    print(f"     cd fine-tuning/benchmarks")
    print(f"     python 1_voice_comparison.py --finetuned-port 8000")
    print("")
    print(f"  3. Deploy with RAG:")
    print(f"     ./serve_rag_proxy.sh scifi_world")


def main():
    parser = argparse.ArgumentParser(
        description="Merge LoRA adapter with base model for deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge specific checkpoint
  python 3_merge_adapter.py \\
      --checkpoint ../checkpoints/qlora-style-pipeline-test/checkpoint-5 \\
      --output ../merged_models/llama-3.1-8b-scifi-style
  
  # Auto-select best checkpoint from training run
  python 3_merge_adapter.py \\
      --checkpoint ../checkpoints/qlora-style-pipeline-test \\
      --auto-select \\
      --output ../merged_models/llama-3.1-8b-scifi-style
  
  # Quick merge with all defaults
  python 3_merge_adapter.py --auto
        """
    )
    
    parser.add_argument(
        '--checkpoint',
        type=str,
        help='Path to checkpoint directory or training run directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output directory for merged model'
    )
    parser.add_argument(
        '--base-model',
        type=str,
        default=None,
        help='Override base model (auto-detected from adapter config if not specified)'
    )
    parser.add_argument(
        '--dtype',
        type=str,
        default='bfloat16',
        choices=['bfloat16', 'float16', 'float32'],
        help='Data type for merged model (default: bfloat16)'
    )
    parser.add_argument(
        '--auto-select',
        action='store_true',
        help='Automatically select best checkpoint from training run'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto mode: use latest training run and auto-select best checkpoint'
    )
    
    args = parser.parse_args()
    
    # Auto mode: find latest training run
    if args.auto:
        checkpoint_base = Path(__file__).parent.parent / 'checkpoints'
        
        # Find all training runs
        runs = [d for d in checkpoint_base.iterdir() if d.is_dir()]
        if not runs:
            print("[ERROR] No training runs found in checkpoints/")
            print(f"   Checked: {checkpoint_base}")
            sys.exit(1)
        
        # Use most recent (by modification time)
        latest_run = max(runs, key=lambda x: x.stat().st_mtime)
        print(f"[AUTO] Using latest training run: {latest_run.name}")
        
        checkpoint_path = latest_run
        args.auto_select = True
        
        # Auto-generate output path
        output_name = f"llama-3.1-8b-{latest_run.name}"
        output_path = Path(__file__).parent.parent / 'merged_models' / output_name
    else:
        # Manual mode: validate arguments
        if not args.checkpoint:
            print("[ERROR] --checkpoint required (or use --auto)")
            parser.print_help()
            sys.exit(1)
        
        checkpoint_path = Path(args.checkpoint)
        
        if not args.output:
            # Auto-generate output from checkpoint name
            output_name = f"llama-3.1-8b-{checkpoint_path.parent.name}"
            output_path = Path(__file__).parent.parent / 'merged_models' / output_name
            print(f"[AUTO] Output path: {output_path}")
        else:
            output_path = Path(args.output)
    
    # Verify checkpoint path exists
    if not checkpoint_path.exists():
        print(f"[ERROR] Checkpoint path does not exist: {checkpoint_path}")
        sys.exit(1)
    
    # Auto-select best checkpoint if directory is a training run
    if args.auto_select or not (checkpoint_path / 'adapter_config.json').exists():
        print(f"\n[AUTO] Searching for checkpoints in {checkpoint_path}...")
        checkpoints = find_checkpoints(checkpoint_path)
        
        if not checkpoints:
            print(f"[ERROR] No valid checkpoints found in {checkpoint_path}")
            print("   Looking for directories like: checkpoint-1/, checkpoint-2/, ...")
            print("   With files: adapter_config.json, adapter_model.safetensors")
            sys.exit(1)
        
        print(f"[OK] Found {len(checkpoints)} checkpoint(s):")
        for ckpt in checkpoints:
            print(f"   - {ckpt.name}")
        
        checkpoint_path = select_best_checkpoint(checkpoints)
        if checkpoint_path is None:
            print("[ERROR] Failed to select checkpoint")
            sys.exit(1)
        print(f"[AUTO] Selected: {checkpoint_path.name}\n")
    
    # Perform merge
    merge_adapter(
        checkpoint_path=checkpoint_path,
        output_path=output_path,
        base_model=args.base_model,
        dtype=args.dtype
    )


if __name__ == '__main__':
    main()
