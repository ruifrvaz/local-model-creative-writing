# Automatic Retrieval Test Logging

**Date**: October 19, 2025  
**Context**: Enhanced Step 3 to automatically log test results for analysis  
**Goal**: Enable tracking and comparison of retrieval quality over time

---

## Problem

The original retrieval test script only displayed results to the terminal without saving them. This made it difficult to:
- Compare retrieval quality across different configurations
- Track improvements after re-embedding with different models
- Analyze which queries perform well vs poorly
- Share test results with others
- Debug retrieval issues retrospectively

---

## Solution Implemented

### 1. Created Test Results Directory

```bash
RAG/test_results/
├── retrieval_test_20251019_223236.json  # Timestamped
└── retrieval_test_latest.json           # Always latest
```

### 2. Enhanced Script: `3_test_retrieval.py`

**Updated Docstring**
```python
"""
Step 3: Test Retrieval Quality
Purpose: Run test queries and validate retrieval accuracy
Usage: ./3_test_retrieval.py [--collection my_docs] [--interactive]

Process:
  1. Load ChromaDB collection from Step 2
  2. Initialize same embedding model (bge-large-en-v1.5)
  3. Run test queries or interactive mode
  4. Display results with similarity scores
  5. Save test results to test_results/ folder (JSON format)    # ← NEW

Output:                                                          # ← NEW SECTION
  - test_results/retrieval_test_YYYYMMDD_HHMMSS.json (timestamped)
  - test_results/retrieval_test_latest.json (always latest)
```

**Key Changes**

1. **Added JSON Import**
   ```python
   import json
   ```

2. **Created Test Results Directory**
   ```python
   TEST_RESULTS_DIR = Path(__file__).parent / "test_results"
   TEST_RESULTS_DIR.mkdir(exist_ok=True)
   ```

3. **Modified `test_retrieval()` to Return Results**
   ```python
   def test_retrieval(collection, embedder, query, top_k=5):
       # ... existing code ...
       
       # Capture for logging
       retrieved_results = []
       for i, (doc, distance, metadata) in enumerate(...):
           # ... display code ...
           
           retrieved_results.append({
               "rank": i,
               "distance": float(distance),
               "source": metadata.get('source', 'unknown'),
               "length": metadata.get('length', 0),
               "content_preview": doc[:200],
               "full_content": doc
           })
       
       return retrieved_results  # ← NEW
   ```

4. **Enhanced `run_test_queries()` with Logging**
   ```python
   def run_test_queries(collection, embedder, top_k=5):
       # Capture all results
       test_results = {
           "timestamp": datetime.now().isoformat(),
           "collection": collection.name,
           "embedding_model": EMBEDDING_MODEL,
           "top_k": top_k,
           "total_queries": len(test_queries),
           "queries": []
       }
       
       for query in test_queries:
           results = test_retrieval(collection, embedder, query, top_k)
           if results:
               test_results["queries"].append({
                   "query": query,
                   "results": results
               })
       
       # Save results to JSON (timestamped + latest)
       timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
       results_file = TEST_RESULTS_DIR / f"retrieval_test_{timestamp}.json"
       
       with open(results_file, 'w', encoding='utf-8') as f:
           json.dump(test_results, f, indent=2, ensure_ascii=False)
       
       latest_file = TEST_RESULTS_DIR / "retrieval_test_latest.json"
       with open(latest_file, 'w', encoding='utf-8') as f:
           json.dump(test_results, f, indent=2, ensure_ascii=False)
       
       return test_results
   ```

5. **Added Statistics Summary Function**
   ```python
   def print_test_statistics(test_results):
       """Print summary statistics from test results"""
       all_distances = []
       for query_result in test_results["queries"]:
           for result in query_result["results"]:
               all_distances.append(result["distance"])
       
       if all_distances:
           avg_distance = sum(all_distances) / len(all_distances)
           min_distance = min(all_distances)
           max_distance = max(all_distances)
           
           print(f"\nDistance Scores (lower = better match):")
           print(f"   Average: {avg_distance:.4f}")
           print(f"   Best (min): {min_distance:.4f}")
           print(f"   Worst (max): {max_distance:.4f}")
           print(f"   Total retrievals: {len(all_distances)}")
   ```

6. **Updated Main Function**
   ```python
   if args.interactive:
       interactive_mode(collection, embedder, args.top_k)
   else:
       # Run test queries and log results
       test_results = run_test_queries(collection, embedder, args.top_k)
       
       # Print statistics
       print_test_statistics(test_results)
   
   # ... completion message ...
   print(f"[INFO] Test results directory: {TEST_RESULTS_DIR}")
   print(f"[TIP] View results: cat {TEST_RESULTS_DIR}/retrieval_test_latest.json | jq")
   ```

---

## JSON Output Format

```json
{
  "timestamp": "2025-10-19T22:32:36.593487",
  "collection": "scifi_world",
  "embedding_model": "BAAI/bge-large-en-v1.5",
  "top_k": 5,
  "total_queries": 5,
  "queries": [
    {
      "query": "What are Elena's personality traits?",
      "results": [
        {
          "rank": 1,
          "distance": 0.781285120341555,
          "source": "/home/ruifrvaz/scifi-llm/RAG/data/example_vllm_reference.md",
          "length": 934,
          "content_preview": "Character Profile: Captain Elena Vasquez...",
          "full_content": "Character Profile: Captain Elena Vasquez..."
        },
        // ... more results ...
      ]
    },
    // ... more queries ...
  ]
}
```

---

## Test Results Summary

**First Run Statistics** (October 19, 2025):

```
Distance Scores (lower = better match):
   Average: 0.9600
   Best (min): 0.4686 (Arcturian homeworld atmosphere query)
   Worst (max): 1.3070 (FTL drive as rank #4)
   Total retrievals: 20

Queries tested: 5
Collection: scifi_world
Top-K per query: 5 (actual: 4 due to small dataset)
```

**Best Performing Query**: "Tell me about the Arcturian homeworld atmosphere" (0.4686)  
**Worst Performing Query**: Some rank #4 results with ~1.3 distance

---

## Benefits

1. ✅ **Historical Tracking**: Compare results before/after changes
2. ✅ **Reproducibility**: Re-run same queries and compare
3. ✅ **Analysis**: Calculate statistics (avg/min/max distances)
4. ✅ **Debugging**: Full content preserved for investigation
5. ✅ **Sharing**: JSON format easy to share and process
6. ✅ **Automation**: Runs automatically on every test
7. ✅ **Statistics**: Immediate summary of retrieval quality

---

## Usage Examples

### View Latest Results
```bash
cat test_results/retrieval_test_latest.json | jq
```

### Check Best Match for Query
```bash
cat test_results/retrieval_test_latest.json | jq '.queries[0].results[0]'
```

### Extract All Distance Scores
```bash
cat test_results/retrieval_test_latest.json | jq '.queries[].results[].distance'
```

### Compare Two Test Runs
```bash
# List all test runs
ls -lh test_results/

# Compare statistics
jq '.queries[].results[0].distance' test_results/retrieval_test_20251019_223236.json
```

---

## Files Modified

1. **`/home/ruifrvaz/scifi-llm/RAG/3_test_retrieval.py`**
   - Added JSON import
   - Created TEST_RESULTS_DIR constant
   - Modified test_retrieval() to return results
   - Enhanced run_test_queries() with logging
   - Added print_test_statistics() function
   - Updated main() to call statistics
   - Enhanced docstring with output information

---

## Directory Structure

```
RAG/
├── 3_test_retrieval.py          # Enhanced with logging
├── test_results/                # ← NEW FOLDER
│   ├── retrieval_test_20251019_223236.json
│   └── retrieval_test_latest.json
├── chunks/
├── chroma_db/
└── data/
```

---

## Next Steps

**Potential Enhancements**:
1. Add comparison mode: `./3_test_retrieval.py --compare file1.json file2.json`
2. Generate HTML reports with visualizations
3. Track metrics over time (plot distance trends)
4. Add custom query sets via command line or file
5. Export results to CSV for spreadsheet analysis
6. Add precision@k and recall@k metrics if ground truth available

**Current Status**: ✅ Fully functional with automatic logging and statistics

---

## Related Documentation

- **RAG Workflow**: `scifi-llm/RAG/QUICK_START.md`
- **Markdown Support**: `scifi-llm/docs/history/2025-10-19_rag_markdown_support.md`
- **Test Results**: `scifi-llm/RAG/test_results/retrieval_test_latest.json`
