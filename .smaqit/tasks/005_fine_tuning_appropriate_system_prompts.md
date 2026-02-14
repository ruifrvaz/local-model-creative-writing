# Analyze Visions of Gaea Manuscript Style

**Priority:** 2  
**State:** Open  
**Created:** 2025-11-29  
**Depends On:** Task 004

## Description

When parsing the chunks, i want to create also appropriate system prompts for the training data. for example "create an epilogue" points to creating an epilogue. "create an epigraph" points to creating an epigraph. "create start of memory, slow pace, etc.etc." creates start of memory

## Current Progress

- conceptual idea. 
- some suggestions on system insructions ("create an epilogue", "create an epigraph")

## Potential obstacles

- size of chunks might not be significant in some cases, assess feasibility case by case

## Acceptance Criteria

After fine tuning with properly parsed datasets, when user inputs "create an epigraph" the agent will generate an epigraph on the style of the actual chunk of data was trained with.


