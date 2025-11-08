#!/usr/bin/env python3
"""
Voice Comparison Benchmark for Fine-Tuning

Generates completions from baseline or fine-tuned models for style analysis.
Use compare_with_training.py to measure transfer effectiveness against training data.

Usage:
    # Generate baseline (before training)
    python 1_voice_comparison.py --baseline --port 8000
    
    # Generate fine-tuned (after training)
    python 1_voice_comparison.py --finetuned --port 8002
    
    # Compare both against training data
    python compare_with_training.py --latest

Outputs:
    - results/baseline_TIMESTAMP.json
    - results/finetuned_TIMESTAMP.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from openai import OpenAI

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))
from utils import style_metrics, comparison


def load_test_prompts(prompts_file: str = "test_prompts.json") -> List[Dict]:
    """Load test prompts from JSON file."""
    prompts_path = Path(__file__).parent / prompts_file
    
    if not prompts_path.exists():
        raise FileNotFoundError(f"Test prompts not found: {prompts_path}")
    
    with open(prompts_path, 'r') as f:
        data = json.load(f)
    
    return data.get("prompts", [])


def generate_completion(client: OpenAI, prompt: str, 
                       max_tokens: int = 200,
                       temperature: float = 0.85,
                       model_name: str = None) -> Dict:
    """
    Generate completion from model via OpenAI-compatible API.
    
    Args:
        client: OpenAI client instance
        prompt: Prompt text
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        model_name: Model name to use (fetched from API if None)
    
    Returns:
        Dict with 'text', 'finish_reason', 'tokens'
    """
    # Get model name from server if not provided
    if model_name is None:
        try:
            models = client.models.list()
            model_name = models.data[0].id
        except Exception as e:
            print(f"Warning: Could not fetch model name: {e}")
            model_name = "meta-llama/Llama-3.1-8B-Instruct"  # Fallback
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a skilled science fiction writer. Continue the story naturally."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.95
        )
        
        choice = response.choices[0]
        return {
            "text": choice.message.content,
            "finish_reason": choice.finish_reason,
            "tokens": response.usage.completion_tokens if response.usage else 0
        }
    
    except Exception as e:
        print(f"Error generating completion: {e}")
        return {
            "text": "",
            "finish_reason": "error",
            "tokens": 0,
            "error": str(e)
        }


def run_baseline(port: int, output_dir: Path) -> Dict:
    """
    Generate baseline completions from base model.
    
    Args:
        port: vLLM server port
        output_dir: Directory for results
    
    Returns:
        Results dictionary
    """
    print(f"\n=== Baseline Generation ===")
    print(f"Server: http://localhost:{port}")
    
    client = OpenAI(
        api_key="EMPTY",
        base_url=f"http://localhost:{port}/v1"
    )
    
    prompts = load_test_prompts()
    print(f"Loaded {len(prompts)} test prompts")
    
    # Get model name from server
    try:
        models = client.models.list()
        model_name = models.data[0].id
        print(f"Model: {model_name}\n")
    except Exception as e:
        print(f"Warning: Could not fetch model name: {e}")
        model_name = None
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "mode": "baseline",
        "port": port,
        "num_prompts": len(prompts),
        "completions": []
    }
    
    for i, prompt_data in enumerate(prompts, 1):
        prompt_id = prompt_data["id"]
        prompt_text = prompt_data["prompt"]
        category = prompt_data["category"]
        
        print(f"[{i}/{len(prompts)}] Generating: {prompt_id} ({category})")
        
        completion = generate_completion(client, prompt_text, model_name=model_name)
        
        # Analyze style
        if completion["text"]:
            metrics = style_metrics.analyze_text(completion["text"])
        else:
            metrics = {}
        
        results["completions"].append({
            "prompt_id": prompt_id,
            "prompt": prompt_text,
            "category": category,
            "output": completion["text"],
            "finish_reason": completion["finish_reason"],
            "tokens": completion["tokens"],
            "metrics": metrics
        })
        
        print(f"  → {completion['tokens']} tokens, finish: {completion['finish_reason']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"baseline_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Baseline results saved: {output_file}")
    return results


def run_finetuned(port: int, output_dir: Path) -> Dict:
    """
    Generate completions from fine-tuned model.
    
    Args:
        port: vLLM server port
        output_dir: Directory for results
    
    Returns:
        Results dictionary
    """
    print(f"\n=== Fine-Tuned Generation ===")
    print(f"Server: http://localhost:{port}")
    
    client = OpenAI(
        api_key="EMPTY",
        base_url=f"http://localhost:{port}/v1"
    )
    
    prompts = load_test_prompts()
    print(f"Loaded {len(prompts)} test prompts")
    
    # Get model name from server
    try:
        models = client.models.list()
        model_name = models.data[0].id
        print(f"Model: {model_name}\n")
    except Exception as e:
        print(f"Warning: Could not fetch model name: {e}")
        model_name = None
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "mode": "finetuned",
        "port": port,
        "num_prompts": len(prompts),
        "completions": []
    }
    
    for i, prompt_data in enumerate(prompts, 1):
        prompt_id = prompt_data["id"]
        prompt_text = prompt_data["prompt"]
        category = prompt_data["category"]
        
        print(f"[{i}/{len(prompts)}] Generating: {prompt_id} ({category})")
        
        completion = generate_completion(client, prompt_text, model_name=model_name)
        
        # Analyze style
        if completion["text"]:
            metrics = style_metrics.analyze_text(completion["text"])
        else:
            metrics = {}
        
        results["completions"].append({
            "prompt_id": prompt_id,
            "prompt": prompt_text,
            "category": category,
            "output": completion["text"],
            "finish_reason": completion["finish_reason"],
            "tokens": completion["tokens"],
            "metrics": metrics
        })
        
        print(f"  → {completion['tokens']} tokens, finish: {completion['finish_reason']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"finetuned_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Fine-tuned results saved: {output_file}")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Voice comparison benchmark for fine-tuning evaluation"
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--baseline', action='store_true',
                           help='Generate baseline completions')
    mode_group.add_argument('--finetuned', action='store_true',
                           help='Generate fine-tuned completions')
    
    # Port configuration
    parser.add_argument('--port', type=int, default=8000,
                       help='vLLM server port')
    
    # Output configuration
    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(__file__).parent / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run selected mode
    if args.baseline:
        run_baseline(args.port, output_dir)
    
    elif args.finetuned:
        run_finetuned(args.port, output_dir)


if __name__ == "__main__":
    main()
