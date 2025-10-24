#!/usr/bin/env -S bash -c 'source ~/.venvs/llm/bin/activate && exec python "$0" "$@"'

"""
Benchmark 4: Long Context Coherence Test
Purpose: Evaluate story continuity and character consistency over long contexts
Metrics: Character tracking, plot coherence, detail retention
Runtime: ~15 minutes
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
import re

API_URL = "http://localhost:8000"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Long story development test
STORY_PROMPTS = [
    {
        "stage": 1,
        "name": "setup",
        "prompt": """Write the opening chapter of a science fiction novel. Introduce:
- Captain Elena Vasquez, a 45-year-old veteran of deep space exploration
- Her second-in-command, Dr. Marcus Chen, a xenobiologist
- The ship 'Prometheus', a research vessel
- They are investigating unusual energy readings from an unexplored star system
Be specific about character details, the ship's specifications, and the mysterious readings.""",
        "max_tokens": 800
    },
    {
        "stage": 2,
        "name": "development",
        "prompt": """Continue the story. The crew discovers an ancient alien structure orbiting a dead star. 
Elena must decide whether to explore it despite regulations. Marcus argues for caution. 
Show their different perspectives based on their established personalities. 
Describe the structure in detail.""",
        "max_tokens": 800
    },
    {
        "stage": 3,
        "name": "escalation",
        "prompt": """Continue the story. They board the alien structure. Inside, they find evidence of a 
civilization that disappeared millions of years ago. Marcus makes a discovery about why they vanished.
Elena faces a critical decision. Maintain consistency with earlier character details and plot points.""",
        "max_tokens": 800
    },
    {
        "stage": 4,
        "name": "climax",
        "prompt": """Continue the story. The structure begins to activate. They realize the aliens' 
technology is still functional. Elena and Marcus must work together, using their complementary skills
(her leadership and his scientific expertise) to prevent a catastrophe. Reference specific earlier details.""",
        "max_tokens": 800
    },
    {
        "stage": 5,
        "name": "resolution",
        "prompt": """Conclude the story. How do Elena and Marcus's experiences change them? 
What do they report to their superiors? Reflect on the journey from the initial energy readings to now.
Maintain all character and plot consistency from previous sections.""",
        "max_tokens": 600
    }
]


def check_server():
    """Check if VLLM server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_model_name():
    """Get the current model name"""
    try:
        response = requests.get(f"{API_URL}/v1/models", timeout=5)
        return response.json()["data"][0]["id"]
    except:
        return "unknown"


def get_max_model_len():
    """Get the server's max_model_len configuration"""
    try:
        response = requests.get(f"{API_URL}/v1/models", timeout=5)
        return response.json()["data"][0]["max_model_len"]
    except:
        return "unknown"


def generate_continuation(conversation_history, new_prompt, max_tokens=800):
    """Generate text continuation with full conversation history"""
    start_time = time.time()
    
    # Build messages with full history
    messages = conversation_history + [{"role": "user", "content": new_prompt}]
    
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            json={
                "model": get_model_name(),
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
            timeout=180
        )
        
        elapsed = time.time() - start_time
        result = response.json()
        
        return {
            "text": result["choices"][0]["message"]["content"],
            "prompt_tokens": result["usage"]["prompt_tokens"],
            "completion_tokens": result["usage"]["completion_tokens"],
            "total_tokens": result["usage"]["total_tokens"],
            "time": elapsed,
            "tokens_per_sec": result["usage"]["completion_tokens"] / elapsed if elapsed > 0 else 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "text": "",
            "tokens": 0,
            "time": 0
        }


def analyze_character_consistency(text, character_name):
    """Check if character is mentioned and characterized consistently with title variations"""
    # Build pattern to match character name and common variations
    patterns = []
    
    if character_name.lower() == "elena":
        # Match: Elena, Captain, Captain Vasquez, the captain
        patterns = [
            r'\bElena\b',
            r'\bCaptain\b(?:\s+Vasquez)?',
            r'\bthe\s+captain\b'
        ]
    elif character_name.lower() == "marcus":
        # Match: Marcus, Chen, Dr. Chen, Doctor Chen, the doctor, the xenobiologist
        patterns = [
            r'\bMarcus\b',
            r'\bChen\b',
            r'\bDr\.\s+Chen\b',
            r'\bDoctor\s+Chen\b',
            r'\bthe\s+doctor\b',
            r'\bthe\s+xenobiologist\b'
        ]
    else:
        # Default: just match the name
        patterns = [rf'\b{character_name}\b']
    
    # Count all mentions across all patterns
    mentions = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in patterns)
    
    # Look for character actions/dialogue with expanded patterns
    dialogue_patterns = [f'"{pattern}' for pattern in patterns] + [f"'{pattern}" for pattern in patterns]
    has_dialogue = any(re.search(pattern, text, re.IGNORECASE) for pattern in dialogue_patterns)
    
    # Enhanced action detection with "she/he said" patterns
    action_words = ['said', 'replied', 'asked', 'thought', 'walked', 'ran', 'decided', 'realized', 
                    'whispered', 'shouted', 'murmured', 'exclaimed', 'muttered', 'explained']
    
    has_actions = False
    for pattern in patterns:
        for action in action_words:
            if re.search(rf'{pattern}\s+{action}', text, re.IGNORECASE):
                has_actions = True
                break
        if has_actions:
            break
    
    # Also check for "she/he said" patterns near character mentions
    pronoun_actions = len(re.findall(r'\b(she said|he said|she replied|he replied|she asked|he asked)\b', text, re.IGNORECASE))
    
    return {
        "mentions": mentions,
        "has_dialogue": has_dialogue,
        "has_actions": has_actions or pronoun_actions > 0,
        "pronoun_actions": pronoun_actions,
        "present": mentions > 0
    }


def analyze_plot_elements(text, expected_elements):
    """Check for presence of plot elements"""
    found_elements = {}
    for element in expected_elements:
        # Simple keyword matching
        pattern = element.replace(" ", ".*")
        found = bool(re.search(pattern, text, re.IGNORECASE))
        found_elements[element] = found
    
    coverage = sum(found_elements.values()) / len(expected_elements) if expected_elements else 0
    
    return {
        "elements": found_elements,
        "coverage": round(coverage, 2)
    }


def analyze_coherence(stages_data):
    """Analyze overall story coherence across all stages"""
    # Track character consistency across stages
    elena_consistency = []
    marcus_consistency = []
    
    for stage in stages_data:
        if "analysis" in stage:
            elena_consistency.append(1 if stage["analysis"]["elena"]["present"] else 0)
            marcus_consistency.append(1 if stage["analysis"]["marcus"]["present"] else 0)
    
    # Calculate consistency scores
    elena_score = sum(elena_consistency) / len(elena_consistency) if elena_consistency else 0
    marcus_score = sum(marcus_consistency) / len(marcus_consistency) if marcus_consistency else 0
    
    return {
        "elena_consistency": round(elena_score, 2),
        "marcus_consistency": round(marcus_score, 2),
        "overall_character_consistency": round((elena_score + marcus_score) / 2, 2)
    }


def main():
    print("━" * 80)
    print("VLLM Long Context Coherence Benchmark")
    print("━" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"API: {API_URL}")
    print()
    
    # Check server
    print("[TEST] Checking server availability...")
    if not check_server():
        print("[ERROR] Server not responding at", API_URL)
        print("Please start the server with: cd ../../ && ./serve_vllm.sh")
        return
    print("[OK] Server is running")
    print()
    
    model_name = get_model_name()
    max_model_len = get_max_model_len()
    print(f"[INFO] Testing model: {model_name}")
    print(f"[INFO] Server max_model_len: {max_model_len} tokens")
    print(f"[INFO] This test evaluates story continuity over ~3000-4000 tokens")
    print()
    
    # Run story development test
    results = {
        "benchmark": "long_context_coherence",
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "max_model_len": max_model_len,
        "api_url": API_URL,
        "stages": []
    }
    
    conversation_history = []
    total_context_tokens = 0
    
    print("[RUN] Generating multi-stage story...")
    print()
    
    for i, stage_prompt in enumerate(STORY_PROMPTS, 1):
        print("━" * 80)
        print(f"[STAGE {i}/{len(STORY_PROMPTS)}] {stage_prompt['name'].title()}")
        print(f"Context size: ~{total_context_tokens} tokens")
        print()
        
        # Generate continuation
        generation = generate_continuation(
            conversation_history,
            stage_prompt["prompt"],
            stage_prompt["max_tokens"]
        )
        
        if "error" in generation:
            print(f"[ERROR] {generation['error']}")
            break
        
        # Update context
        conversation_history.append({"role": "user", "content": stage_prompt["prompt"]})
        conversation_history.append({"role": "assistant", "content": generation["text"]})
        total_context_tokens = generation["total_tokens"]
        
        # Analyze this stage
        elena_analysis = analyze_character_consistency(generation["text"], "Elena")
        marcus_analysis = analyze_character_consistency(generation["text"], "Marcus")
        
        # Expected plot elements by stage
        plot_elements = {
            1: ["Prometheus", "energy readings", "star system"],
            2: ["alien structure", "decision", "regulations"],
            3: ["discovery", "civilization", "millions of years"],
            4: ["technology", "activate", "catastrophe"],
            5: ["report", "change", "journey"]
        }
        
        plot_analysis = analyze_plot_elements(generation["text"], plot_elements.get(stage_prompt["stage"], []))
        
        # Display results
        print(f"[RESULT] Generated: {generation['completion_tokens']} tokens in {generation['time']:.2f}s")
        print(f"[RESULT] Speed: {generation['tokens_per_sec']:.1f} tokens/sec")
        print(f"[RESULT] Total Context: {generation['total_tokens']} tokens")
        print(f"[RESULT] Elena Mentions: {elena_analysis['mentions']}")
        print(f"[RESULT] Marcus Mentions: {marcus_analysis['mentions']}")
        print(f"[RESULT] Plot Coverage: {plot_analysis['coverage'] * 100:.0f}%")
        print()
        print(f"[SAMPLE] {generation['text'][:300]}...")
        print()
        
        # Store stage results
        results["stages"].append({
            "stage": stage_prompt["stage"],
            "name": stage_prompt["name"],
            "prompt": stage_prompt["prompt"],
            "generation": generation,
            "analysis": {
                "elena": elena_analysis,
                "marcus": marcus_analysis,
                "plot": plot_analysis
            }
        })
        
        time.sleep(2)  # Brief pause between stages
    
    # Analyze overall coherence
    print("━" * 80)
    print("[COMPLETE] Long Context Coherence Benchmark Complete")
    print("━" * 80)
    print()
    
    coherence = analyze_coherence(results["stages"])
    
    avg_speed = sum(s["generation"]["tokens_per_sec"] for s in results["stages"]) / len(results["stages"])
    total_words = sum(len(s["generation"]["text"].split()) for s in results["stages"])
    max_context = max(s["generation"]["total_tokens"] for s in results["stages"])
    
    summary = {
        "total_stages": len(results["stages"]),
        "total_words_generated": total_words,
        "max_context_tokens": max_context,
        "average_speed_tokens_per_sec": round(avg_speed, 1),
        "character_coherence": coherence,
        "overall_coherence_score": round(coherence["overall_character_consistency"] * 100, 1)
    }
    
    results["summary"] = summary
    
    print(f"[SUMMARY] Total Story Length: {total_words} words ({max_context} tokens)")
    print(f"[SUMMARY] Character Consistency: {summary['overall_coherence_score']:.1f}/100")
    print(f"[SUMMARY] Elena Consistency: {coherence['elena_consistency'] * 100:.0f}%")
    print(f"[SUMMARY] Marcus Consistency: {coherence['marcus_consistency'] * 100:.0f}%")
    print(f"[SUMMARY] Average Speed: {summary['average_speed_tokens_per_sec']} tokens/sec")
    print()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"long_context_coherence_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"[INFO] Full results: {output_file}")
    print()
    print("[TIP] Read the full story: jq -r '.stages[].generation.text' " + str(output_file))
    print("[TIP] This is the most important benchmark for novel writing!")
    print()


if __name__ == "__main__":
    main()
