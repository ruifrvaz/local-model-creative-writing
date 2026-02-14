# Archives

This directory contains completed project artifacts, metadata, and documentation from major tasks. Archives preserve decision-making processes, session reports, and working files after tasks are complete.

## Purpose

- **Preserve context** - Keep detailed records of how work was completed
- **Enable replication** - Document methodology for future similar tasks
- **Reduce clutter** - Move completed metadata out of active working directories
- **Reference material** - Available for troubleshooting and validation

## Structure

Archives are organized by task number and description:

```
docs/archives/
├── README.md (this file)
└── NNN_task_description/
    ├── README.md (archive-specific documentation)
    └── [archived files]
```

## Naming Convention

**Format:** `NNN_task_description/`

- `NNN` - Zero-padded task number matching `.smaqit/tasks/NNN_*.md`
- `task_description` - Brief descriptor from task filename
- Example: `002_visions_of_gaea_curation/`

## Current Archives

### 002_visions_of_gaea_curation/
**Task:** `.smaqit/tasks/002_curate_visions_of_gaea_training_data.md`  
**Status:** Complete  
**Date:** November 21-24, 2025  

Manuscript curation metadata for Visions of Gaea (35 chunks, 63,302 words):
- Session reports (5 sessions)
- Curation analysis and quality validation
- Planning documents and working files
- Chunking scripts and temp files

**Output:** Training-ready chunks in `fine-tuning/data/raw/visions_of_gaea/`

## When to Archive

Archive materials when:
- ✅ Task status changes to "Completed"
- ✅ Files are no longer needed in active workflow
- ✅ Documentation is comprehensive and final
- ✅ Output artifacts are in their permanent locations

Do NOT archive:
- ❌ Active training data (chunks, JSONL files)
- ❌ Source manuscripts still in use
- ❌ Scripts still being executed
- ❌ Configuration files referenced by active processes

## Related Directories

- **`.smaqit/tasks/`** - Active and pending work items
- **`.smaqit/history/`** - Architectural changes and decisions
- **`docs/archives/`** - Completed task artifacts (this directory)

All three serve as "meta work folders" for project organization and knowledge preservation.
