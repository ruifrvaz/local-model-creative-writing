#!/usr/bin/env -S bash -c 'source ~/.venvs/llm/bin/activate && exec python "$0" "$@"'

"""
Benchmark 3: Creative Writing Quality Assessment
Purpose: Evaluate writing quality for science fiction content
Metrics: Coherence, creativity, vocabulary richness, prose quality
Runtime: ~10 minutes
Usage: ./3_creative_quality.py [TONE]
       TONE options: creative, technical, dramatic, poetic, gritty (default: technical)
"""

import json
import time
import requests
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter
import re

API_URL = "http://localhost:8000"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Get tone from command line argument or use default
WRITING_TONE = sys.argv[1].lower() if len(sys.argv) > 1 else "technical"

# Tone-specific generation parameters
TONE_CONFIGS = {
    "creative": {
        "temperature": 0.9,
        "top_p": 0.95,
        "presence_penalty": 0.7,
        "frequency_penalty": 0.5
    },
    "technical": {
        "temperature": 0.6,
        "top_p": 0.85,
        "presence_penalty": 0.3,
        "frequency_penalty": 0.7
    },
    "dramatic": {
        "temperature": 0.85,
        "top_p": 0.92,
        "presence_penalty": 0.6,
        "frequency_penalty": 0.6
    },
    "poetic": {
        "temperature": 1.0,
        "top_p": 0.98,
        "presence_penalty": 0.8,
        "frequency_penalty": 0.3
    },
    "gritty": {
        "temperature": 0.8,
        "top_p": 0.90,
        "presence_penalty": 0.5,
        "frequency_penalty": 0.8
    }
}

# System prompts for each tone
SYSTEM_PROMPTS = {
    "creative": "You are a creative science fiction writer. Use vivid imagery, sensory details, metaphors, and immersive descriptions. Show, don't tell. Always write complete, well-formed sentences and paragraphs.",
    "technical": "You are a technical science fiction writer. Focus on scientific accuracy, plausible mechanisms, and clear explanations while maintaining engaging prose. Always complete your sentences and thoughts fully.",
    "dramatic": "You are a dramatic science fiction writer. Create tension, emotional depth, compelling conflicts, and high stakes. Make readers feel the intensity. Write complete, powerful sentences.",
    "poetic": "You are a poetic science fiction writer. Use lyrical language, rhythm, metaphors, and evocative descriptions. Make every sentence beautiful and complete.",
    "gritty": "You are a gritty science fiction writer. Use realistic, harsh language with dark undertones, moral ambiguity, and unflinching detail. Write complete, hard-hitting sentences."
}

# Validate tone selection
if WRITING_TONE not in TONE_CONFIGS:
    print(f"[ERROR] Invalid tone '{WRITING_TONE}'. Must be one of: {', '.join(TONE_CONFIGS.keys())}")
    print(f"Usage: {sys.argv[0]} [TONE]")
    print(f"Example: {sys.argv[0]} creative")
    sys.exit(1)

# Get parameters for selected tone
GENERATION_PARAMS = TONE_CONFIGS[WRITING_TONE]

# Creative writing test prompts
TEST_PROMPTS = [
    {
        "name": "character_introduction",
        "prompt": "Introduce a starship captain who has been in deep space for 10 years. Use vivid sensory details and show their personality through actions, not just description.",
        "expected_elements": ["character name", "personality", "backstory", "motivation"],
        "max_tokens": 400  # Increased from 300 (+33%)
    },
    {
        "name": "world_building",
        "prompt": "Describe a futuristic city on Mars with advanced technology and social challenges. Include metaphors, sensory details (sights, sounds, smells), and make it immersive.",
        "expected_elements": ["visual details", "technology", "society", "atmosphere"],
        "max_tokens": 500  # Increased from 400 (+25%)
    },
    {
        "name": "action_scene",
        "prompt": "Write a tense scene where a crew must evacuate their damaged spacecraft. Show the chaos through sensory details - what they see, hear, feel, and smell. Make us feel the urgency.",
        "expected_elements": ["urgency", "sensory details", "character actions", "stakes"],
        "max_tokens": 450  # Increased from 350 (+29%)
    },
    {
        "name": "dialogue",
        "prompt": "Write a conversation between an AI and a human colonist about the meaning of consciousness. Give each character a distinct voice and use metaphors or analogies to explore the concepts.",
        "expected_elements": ["distinct voices", "philosophical depth", "natural flow", "conflict"],
        "max_tokens": 500  # Increased from 400 (+25%)
    },
    {
        "name": "technical_description",
        "prompt": "Explain how a faster-than-light drive works in a way that sounds plausible and scientific. Use creative analogies and vivid language to make it engaging, not just technical.",
        "expected_elements": ["technical terms", "logical explanation", "scientific tone", "creativity"],
        "max_tokens": 400  # Increased from 300 (+33%)
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


def generate_text(prompt, max_tokens=300):
    """Generate text from the model with tone configuration"""
    start_time = time.time()
    
    # Enhance prompt to encourage complete sentences
    enhanced_prompt = f"{prompt}\n\nIMPORTANT: End naturally with proper punctuation. Aim for approximately {max_tokens * 0.75:.0f} words."
    
    try:
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            json={
                "model": get_model_name(),
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPTS[WRITING_TONE]},
                    {"role": "user", "content": enhanced_prompt}
                ],
                "max_tokens": max_tokens,
                **GENERATION_PARAMS
            },
            timeout=120
        )
        
        elapsed = time.time() - start_time
        result = response.json()
        
        return {
            "text": result["choices"][0]["message"]["content"],
            "tokens": result["usage"]["completion_tokens"],
            "time": elapsed,
            "tokens_per_sec": result["usage"]["completion_tokens"] / elapsed if elapsed > 0 else 0,
            "finish_reason": result["choices"][0].get("finish_reason", "unknown")
        }
    except Exception as e:
        return {
            "error": str(e),
            "text": "",
            "tokens": 0,
            "time": 0,
            "tokens_per_sec": 0,
            "finish_reason": "error"
        }


def analyze_vocabulary(text):
    """Analyze vocabulary richness"""
    # Remove punctuation and convert to lowercase
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    if not words:
        return {
            "total_words": 0,
            "unique_words": 0,
            "lexical_diversity": 0,
            "avg_word_length": 0
        }
    
    unique_words = set(words)
    lexical_diversity = len(unique_words) / len(words) if words else 0
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    return {
        "total_words": len(words),
        "unique_words": len(unique_words),
        "lexical_diversity": round(lexical_diversity, 3),
        "avg_word_length": round(avg_word_length, 2)
    }


def analyze_sentence_structure(text):
    """Analyze sentence complexity"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {
            "sentence_count": 0,
            "avg_sentence_length": 0,
            "sentence_variety": 0
        }
    
    sentence_lengths = [len(s.split()) for s in sentences]
    avg_length = sum(sentence_lengths) / len(sentence_lengths)
    
    # Measure variety (standard deviation of sentence lengths)
    variance = sum((x - avg_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
    variety = variance ** 0.5
    
    return {
        "sentence_count": len(sentences),
        "avg_sentence_length": round(avg_length, 2),
        "sentence_variety": round(variety, 2)
    }


def analyze_creativity(text, prompt_name):
    """Analyze creative elements with improved scoring"""
    # Expanded descriptive word list
    descriptive_patterns = [
        r'\b(glowing|shimmering|vast|ancient|mysterious|peculiar|strange|unusual|ethereal|luminous|radiant|pristine|desolate|sprawling|towering|crystalline)\b',
        r'\b(pulsing|flickering|gleaming|rippling|cascading|swirling|churning|blazing)\b'
    ]
    descriptive_words = sum(len(re.findall(pattern, text.lower())) for pattern in descriptive_patterns)
    
    # Better metaphor detection
    metaphor_patterns = [
        r'\b(like|as if|seemed|appeared to be|reminded|resembled|echoed|mirrored)\b',
        r'\b(was a|were|became)\b.*\b(ocean|sea|mountain|storm|fire|ice|dream|nightmare)\b'
    ]
    metaphors = sum(len(re.findall(pattern, text.lower())) for pattern in metaphor_patterns)
    
    # Comprehensive sensory details
    sensory_patterns = {
        'visual': r'\b(saw|looked|watched|gazed|stared|glimpsed|appeared|visible|color|light|dark|shadow|bright)\b',
        'auditory': r'\b(heard|sound|noise|whisper|roar|hum|buzz|silent|quiet|echo|voice)\b',
        'tactile': r'\b(felt|touch|texture|smooth|rough|cold|hot|warm|sharp|soft|hard)\b',
        'olfactory': r'\b(smell|scent|odor|aroma|fragrance|stench|whiff)\b',
        'gustatory': r'\b(taste|flavor|bitter|sweet|sour|savory)\b',
        'emotional': r'\b(fear|hope|dread|joy|anger|wonder|awe|despair|relief)\b'
    }
    sensory_details = sum(len(re.findall(pattern, text.lower())) for pattern in sensory_patterns.values())
    
    # Improved dialogue detection with "said" patterns
    has_dialogue = '"' in text or "'" in text
    dialogue_count = text.count('"') + text.count("'")
    # Check for dialogue attribution patterns
    dialogue_attribution = len(re.findall(r'\b(said|replied|asked|whispered|shouted|murmured|yelled|exclaimed|muttered)\b', text.lower()))
    # Check for "she/he said" patterns specifically
    said_patterns = len(re.findall(r'\b(she said|he said|they said|she replied|he replied|she asked|he asked)\b', text.lower()))
    
    # Additional creative indicators
    unique_verbs = len(set(re.findall(r'\b(whispered|murmured|gasped|surged|cascaded|rippled|twisted|shattered|bloomed)\b', text.lower())))
    show_not_tell = len(re.findall(r'(trembled|shivered|smiled|frowned|clenched|gripped|stared)', text.lower()))
    
    return {
        "descriptive_words": descriptive_words,
        "metaphors": metaphors,
        "sensory_details": sensory_details,
        "has_dialogue": has_dialogue,
        "dialogue_markers": dialogue_count,
        "dialogue_attribution": dialogue_attribution,
        "said_patterns": said_patterns,
        "unique_verbs": unique_verbs,
        "show_not_tell": show_not_tell
    }


def score_quality(analysis, generation_data, prompt_data):
    """Calculate quality scores with improved creativity weighting"""
    vocab = analysis["vocabulary"]
    sentences = analysis["sentence_structure"]
    creativity = analysis["creativity"]
    
    # Vocabulary score (0-100)
    vocab_score = min(100, int(
        vocab["lexical_diversity"] * 100 +
        min(vocab["avg_word_length"] - 3, 2) * 10
    ))
    
    # Structure score (0-100)
    structure_score = min(100, int(
        min(sentences["avg_sentence_length"] / 20 * 50, 50) +
        min(sentences["sentence_variety"] / 10 * 50, 50)
    ))
    
    # Improved creativity score (0-100) - more generous scoring
    creativity_score = min(100, int(
        creativity["descriptive_words"] * 3 +
        creativity["metaphors"] * 5 +
        creativity["sensory_details"] * 2 +
        creativity["unique_verbs"] * 4 +
        creativity["show_not_tell"] * 3 +
        (15 if creativity["has_dialogue"] else 0) +
        min(creativity["dialogue_markers"] * 2, 20)
    ))
    
    # Overall score (weighted average)
    overall = int(
        vocab_score * 0.25 +
        structure_score * 0.25 +
        creativity_score * 0.5
    )
    
    return {
        "vocabulary_score": vocab_score,
        "structure_score": structure_score,
        "creativity_score": creativity_score,
        "overall_score": overall
    }


def main():
    print("━" * 80)
    print("VLLM Creative Writing Quality Benchmark")
    print("━" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"API: {API_URL}")
    print(f"Writing Tone: {WRITING_TONE.upper()}")
    print(f"Generation Params: temp={GENERATION_PARAMS['temperature']}, "
          f"top_p={GENERATION_PARAMS['top_p']}, "
          f"presence_penalty={GENERATION_PARAMS['presence_penalty']}, "
          f"frequency_penalty={GENERATION_PARAMS['frequency_penalty']}")
    print(f"System Prompt: {SYSTEM_PROMPTS[WRITING_TONE][:60]}...")
    print(f"Token Limits: 400-500 (increased for better completion)")
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
    print()
    
    # Run tests
    results = {
        "benchmark": "creative_quality",
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "max_model_len": max_model_len,
        "api_url": API_URL,
        "writing_tone": WRITING_TONE,
        "generation_params": GENERATION_PARAMS,
        "system_prompt": SYSTEM_PROMPTS[WRITING_TONE],
        "tests": []
    }
    
    print("[RUN] Running creative writing tests...")
    print()
    
    for i, test_prompt in enumerate(TEST_PROMPTS, 1):
        print("━" * 80)
        print(f"[TEST {i}/{len(TEST_PROMPTS)}] {test_prompt['name'].replace('_', ' ').title()}")
        print(f"Prompt: {test_prompt['prompt'][:60]}...")
        print(f"Max tokens: {test_prompt['max_tokens']}")
        print()
        
        # Generate text
        generation = generate_text(test_prompt["prompt"], test_prompt["max_tokens"])
        
        if "error" in generation:
            print(f"[ERROR] {generation['error']}")
            continue
        
        # Analyze
        text = generation["text"]
        vocab_analysis = analyze_vocabulary(text)
        sentence_analysis = analyze_sentence_structure(text)
        creativity_analysis = analyze_creativity(text, test_prompt["name"])
        
        full_analysis = {
            "vocabulary": vocab_analysis,
            "sentence_structure": sentence_analysis,
            "creativity": creativity_analysis
        }
        
        scores = score_quality(full_analysis, generation, test_prompt)
        
        # Display results with finish_reason
        print(f"[RESULT] Generated: {generation['tokens']} tokens in {generation['time']:.2f}s")
        print(f"[RESULT] Speed: {generation['tokens_per_sec']:.1f} tokens/sec")
        print(f"[RESULT] Finish reason: {generation.get('finish_reason', 'unknown')}", end="")
        
        if generation.get('finish_reason') == 'stop':
            print(" ✓ (natural completion)")
        elif generation.get('finish_reason') == 'length':
            print(" ⚠️  (hit max_tokens limit)")
        else:
            print()
            
        print(f"[RESULT] Vocabulary Score: {scores['vocabulary_score']}/100")
        print(f"[RESULT] Structure Score: {scores['structure_score']}/100")
        print(f"[RESULT] Creativity Score: {scores['creativity_score']}/100")
        print(f"[RESULT] Overall Quality: {scores['overall_score']}/100")
        print()
        print(f"[SAMPLE] {text[:200]}...")
        print()
        
        # Store results
        results["tests"].append({
            "name": test_prompt["name"],
            "prompt": test_prompt["prompt"],
            "max_tokens": test_prompt["max_tokens"],
            "generation": generation,
            "analysis": full_analysis,
            "scores": scores
        })
        
        time.sleep(1)
    
    # Calculate summary
    print("━" * 80)
    print("[COMPLETE] Creative Writing Quality Benchmark Complete")
    print("━" * 80)
    print()
    
    avg_overall = sum(t["scores"]["overall_score"] for t in results["tests"]) / len(results["tests"])
    avg_vocab = sum(t["scores"]["vocabulary_score"] for t in results["tests"]) / len(results["tests"])
    avg_structure = sum(t["scores"]["structure_score"] for t in results["tests"]) / len(results["tests"])
    avg_creativity = sum(t["scores"]["creativity_score"] for t in results["tests"]) / len(results["tests"])
    avg_speed = sum(t["generation"]["tokens_per_sec"] for t in results["tests"]) / len(results["tests"])
    
    # Calculate completion statistics
    natural_completions = sum(1 for t in results["tests"] if t["generation"].get("finish_reason") == "stop")
    truncated = sum(1 for t in results["tests"] if t["generation"].get("finish_reason") == "length")
    completion_rate = (natural_completions / len(results["tests"])) * 100 if results["tests"] else 0
    
    summary = {
        "writing_tone": WRITING_TONE,
        "average_overall_score": round(avg_overall, 1),
        "average_vocabulary_score": round(avg_vocab, 1),
        "average_structure_score": round(avg_structure, 1),
        "average_creativity_score": round(avg_creativity, 1),
        "average_speed_tokens_per_sec": round(avg_speed, 1),
        "test_count": len(results["tests"]),
        "natural_completions": natural_completions,
        "truncated_completions": truncated,
        "completion_rate_percent": round(completion_rate, 1)
    }
    
    results["summary"] = summary
    
    print(f"[SUMMARY] Writing Tone: {WRITING_TONE.upper()}")
    print(f"[SUMMARY] Overall Quality Score: {summary['average_overall_score']}/100")
    print(f"[SUMMARY] Vocabulary: {summary['average_vocabulary_score']}/100")
    print(f"[SUMMARY] Structure: {summary['average_structure_score']}/100")
    print(f"[SUMMARY] Creativity: {summary['average_creativity_score']}/100")
    print(f"[SUMMARY] Average Speed: {summary['average_speed_tokens_per_sec']} tokens/sec")
    print(f"[SUMMARY] Completion Rate: {summary['completion_rate_percent']}% natural completions")
    print(f"[SUMMARY]   ✓ Natural stops: {natural_completions}/{len(results['tests'])}")
    print(f"[SUMMARY]   ⚠️  Hit token limit: {truncated}/{len(results['tests'])}")
    print()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RESULTS_DIR / f"creative_quality_{WRITING_TONE}_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"[INFO] Full results: {output_file}")
    print()
    print("[TIP] View results: cat", output_file, "| jq")
    print(f"[TIP] Test different tones: ./3_creative_quality.py [TONE]")
    print(f"[TIP] Available tones: {', '.join(TONE_CONFIGS.keys())}")
    print(f"[TIP] Examples:")
    print(f"      ./3_creative_quality.py creative")
    print(f"      ./3_creative_quality.py dramatic")
    print(f"      ./3_creative_quality.py poetic")
    print()
    print(f"[TIP] Higher completion rate = better prompt following!")
    print(f"[TIP] Goal: >80% natural completions for production writing")
    print()


if __name__ == "__main__":
    main()
