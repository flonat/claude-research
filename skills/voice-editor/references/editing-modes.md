# Editing Modes

Choose a mode based on content quality and source. Each mode runs a different set of editing passes.

## Light
**Use when:** Content is close to voice, just needs polish  
**Passes:** 3, 5, 6 (Slop Removal, Rhythm, Final Check)  
**Expected edit:** 10-20%

## Standard
**Use when:** Typical AI output with style guide  
**Passes:** All 6  
**Expected edit:** 30-40%

## Heavy
**Use when:** Generic AI output, no style guide used in generation  
**Passes:** All 6, possibly multiple iterations  
**Expected edit:** 50-70%  
**Consider:** Might be faster to rewrite with better prompts

## Rescue
**Use when:** Content is fundamentally off but has good bones  
**Approach:**
1. Extract the core ideas/structure only
2. Rewrite from scratch using voice profile
3. Incorporate any specific facts/examples from original
4. Run standard editing passes on new draft

This is not editing — it's salvage.
