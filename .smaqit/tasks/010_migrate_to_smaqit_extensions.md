# Migrate to smaqit-extensions and Clean Overlapping Instructions

**Status:** Completed
**Mode:** Autonomous
**Created:** 2026-02-14
**Started:** 2026-02-14
**Completed:** 2026-02-14

## Description

Migrate the local-llm project from custom session/task management instructions to the standardized smaqit-extensions framework. This involves moving existing task/history data to `.smaqit/` directories, removing duplicate instructions from copilot-instructions.md, and updating documentation to reference smaqit prompts.

## Background

smaqit-extensions was installed, creating overlaps with existing custom instructions:

**Conflicts Identified:**
1. **Directory duplication**: `tasks/` vs `.smaqit/tasks/`, `docs/history/` vs `.smaqit/history/`
2. **Command naming**: `session.recap` vs `session.start`, `session.wrap` vs `session.finish`
3. **Implementation conflicts**: Custom inline instructions vs separate skill files

**Benefits of Migration:**
- Standardized workflow ecosystem
- Task workflow modes (autonomous/assisted)
- Release management capabilities
- Future smaqit updates and improvements
- Cleaner separation of domain-specific vs workflow instructions

## Acceptance Criteria

### Phase 1: Data Migration
- [x] Move `tasks/PLANNING.md` → `.smaqit/tasks/PLANNING.md` (preserve all 9 tasks)
- [x] Move all task files: `tasks/NNN_*.md` → `.smaqit/tasks/NNN_*.md` (10 files total)
- [x] Create `.smaqit/history/` directory
- [x] Move all history files: `docs/history/*.md` → `.smaqit/history/*.md` (23+ files)
- [x] Verify no data loss (compare file counts, spot-check content)

### Phase 2: Instruction Cleanup
- [x] Remove "Session Commands" section from copilot-instructions.md
- [x] Remove "Task Commands" section from copilot-instructions.md
- [x] Preserve all domain-specific content (Hardware Specifications, Primary Use Case, Architecture, Essential Workflows, etc.)
- [x] Update any references from `tasks/` to `.smaqit/tasks/`
- [x] Update any references from `docs/history/` to `.smaqit/history/`

### Phase 3: Documentation Updates
- [x] Update README.md to reference smaqit prompts instead of custom commands
- [x] Update file structure diagrams to show `.smaqit/` directories
- [x] Create migration note in `.smaqit/history/2026-02-14_smaqit_migration.md`
- [x] Update any workflow examples in documentation

### Phase 4: Verification
- [x] Test `session.start` loads project context correctly
- [x] Test `task.list` shows all migrated tasks
- [x] Test `task.create` creates new task in `.smaqit/tasks/`
- [x] Test `session.finish` creates history in `.smaqit/history/`
- [x] Verify skills are loaded (check `.github/skills/` directory)
- [x] Confirm no broken references in documentation

## Migration Steps

1. **Backup** - Create git commit before migration
2. **Move data** - Relocate tasks and history files
3. **Update PLANNING.md** - Ensure all tasks present in `.smaqit/tasks/PLANNING.md`
4. **Clean instructions** - Remove overlapping sections from copilot-instructions.md
5. **Update docs** - Fix all references to new paths
6. **Test** - Verify all prompts work correctly
7. **Document** - Create history entry for migration

## Impact Assessment

**High Impact:**
- Task tracking location changes (`tasks/` → `.smaqit/tasks/`)
- History documentation location changes (`docs/history/` → `.smaqit/history/`)
- Command names change (`session.recap` → `session.start`, `session.wrap` → `session.finish`)

**Medium Impact:**
- Documentation references need updating
- New capabilities available (task.start with modes, release management)

**Low Impact:**
- Domain-specific instructions (vLLM, RAG, fine-tuning) remain unchanged
- Core project functionality unaffected

## Notes

**Preserved Content:**
- Hardware Specifications (RTX 5090, WSL2 config)
- Primary Use Case (VS Code science fiction writing)
- Architecture diagrams and workflows
- vLLM/RAG/fine-tuning specific instructions
- Virtual environment isolation strategy
- Script numbering conventions
- Project conventions and philosophy

**Deprecated Commands:**
- `session.recap` → use `session.start` or `/session.start`
- `session.wrap` → use `session.finish` or `/session.finish`

**New Capabilities:**
- `/task.start [id]` - Start task in assisted mode (default)
- `/task.start [id] --autonomous` - AI completes task automatically
- `/session.assess` - Analyze requests before implementation
- `/session.title` - Generate session titles
- Release management skills (future use)

## Related Files

- `.github/copilot-instructions.md` - Main instruction file
- `.github/skills/` - smaqit skill implementations
- `.github/prompts/` - smaqit prompt stubs
- `tasks/PLANNING.md` - Old task tracking (to be migrated)
- `.smaqit/tasks/PLANNING.md` - New task tracking location
- `docs/history/` - Old history location (to be migrated)
- `.smaqit/history/` - New history location
