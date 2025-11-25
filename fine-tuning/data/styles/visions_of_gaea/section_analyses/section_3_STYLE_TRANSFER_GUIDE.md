# Style Transfer Guide: Visions of Gaea - Section 3

**Section Coverage:** Memory 10 through Epilogue (Prelude to Ascension)  
**Narrative Phase:** Climax & Resolution  
**Word Count:** 20,459  
**Analysis Date:** 2025-11-25  
**Analyst:** style-analyzer-unbiased agent

---

## Executive Summary

Section 3 of Visions of Gaea represents the climactic arc of the narrative, encompassing intense action sequences, emotional confrontations, and a transcendent epilogue. The writing maintains the manuscript's signature second-person POV ("you") throughout the main narrative before shifting dramatically to third-person feminine ("she") in the mystical epilogue.

The section demonstrates high dialogue density (~50% of text), varied sentence rhythm that accelerates during combat sequences, and sophisticated handling of both intimate social scenes (The Gathering) and visceral body-horror combat (Wollen confrontations). The italicized internal monologue format (...text...) provides philosophical narrator commentary that punctuates action with reflection.

**Core Style Pillars:**
1. Second-person POV with immersive present-moment narration
2. Italicized narrator/soul commentary in ellipsis format
3. Scene breaks (***) for POV shifts, location changes, and temporal gaps
4. Emotional restraint even in violent/traumatic scenes
5. Seamless worldbuilding integration through natural dialogue and action

**Replication Priority:**
- CRITICAL: Second-person POV consistency ("you looked," "you felt")
- CRITICAL: Italicized internal monologue format (...text...)
- CRITICAL: Scene break markers (***) for structural transitions
- HIGH: Dialogue tag variety (said/asked/answered/conveyed)
- HIGH: Physical manifestation of emotion (not telling, showing through body)
- MEDIUM: Technical term density (Units, sentinels, Mother)
- LOW: Specific character names (replaceable in new content)

---

## 1. Narrative Voice & POV

### POV Configuration
- **Type:** Second-person ("you")
- **Tense:** Past dominant with present in commentary
- **Distance:** Close/intimate (character thoughts accessible)

### Voice Characteristics
- Direct address creates reader immersion ("you felt your skull being crushed")
- Narrator exists as separate philosophical entity (italicized passages)
- POV shift to third-person "she" only in transcendent epilogue
- Thoughts conveyed through telepathy or direct prose, not thought tags

### Second-Person Pronoun Density
- Total second-person pronouns: 1,076 occurrences
- Third-person pronouns: 867 occurrences (supporting characters)
- Ratio indicates protagonist-centric narrative with substantial ensemble action

### Epilogue POV Shift
The epilogue ("Prelude to Ascension") breaks from second-person to introduce a transcendent feminine entity:
> "It was then that the entity became aware of herself. Her senses awoke, and she felt the warm embrace of the light surrounding her..."

This shift is UNIQUE to the epilogue and should not occur in main narrative sections.

### Implementation Rules for Generator
✅ ALWAYS: Use "you" for protagonist thoughts, actions, perceptions  
✅ ALWAYS: Past tense for action ("you looked"), present for narrator commentary  
✅ ALWAYS: Italicized format for internal/narrator passages  
⚠️ TYPICALLY: Third-person for supporting character solo scenes (Haji fighting alone)  
❌ NEVER: First-person ("I") except within italicized soul commentary  
❌ NEVER: Third-person for protagonist except in transcendent sequences  

---

## 2. Prose Rhythm & Sentence Structure

### Sentence Metrics
- **Average length:** 15.87 words
- **Range:** 1-88 words
- **Distribution:**
  - Short (<10 words): 34.1%
  - Medium (10-24 words): 46.1%
  - Long (25+ words): 19.9%

### Rhythm Patterns

**Combat/Action Sequences:**
Sentences shorten dramatically. Staccato rhythm creates urgency:
> "He coughed once, his lungs drew one last meager breath, and his heart gave out. Then, there was nothingness."

**Social/Dialogue Scenes:**
Medium sentences dominate with flowing exchanges:
> "She grabbed his left paw and pulled him away into the hall. Before leaving, she turned to you and asked, 'Alan, will you keep Cathy company?'"

**Introspective/Transcendent Passages:**
Long, flowing sentences with multiple clauses:
> "Beleaguered by the unrelenting clamor, an entity began its sluggish awakening, slowly becoming aware of the resonance that threatened to destroy the dark foundations where it had slept for an eternity."

### Paragraph Patterns
- Action paragraphs: 2-4 sentences (rapid pacing)
- Dialogue paragraphs: 1-3 sentences with action beats
- Introspective paragraphs: 3-6 sentences (deeper exploration)
- Transcendent passages: Extended single paragraphs (dreamlike flow)

### Punctuation Style
- **Questions:** 79 occurrences (interrogative dialogue common)
- **Exclamations:** 45 occurrences (restrained use, impactful moments)
- **Ellipses (...):** 69 occurrences (internal monologue marker, trailing thoughts)
- **Scene breaks (\*\*\*):** 7 occurrences (major transitions)

### Implementation Rules for Generator
✅ ALWAYS: Vary sentence length based on scene intensity  
✅ ALWAYS: Use short sentences in combat, longer in reflection  
⚠️ TYPICALLY: Keep dialogue paragraphs concise (1-3 sentences)  
⚠️ TYPICALLY: Use comma-heavy long sentences for transcendence  
❌ NEVER: Uniform sentence length throughout a scene  
❌ NEVER: Exclamation marks in narration (reserve for dialogue)  

---

## 3. Dialogue Dynamics

### Dialogue Ratio
- **Dialogue word count:** 10,161 words
- **Total word count:** 20,459 words
- **Dialogue ratio:** 49.67%

This section has very high dialogue density, especially in the Gathering social scene.

### Dialogue Tag Patterns
| Tag | Count | Usage Context |
|-----|-------|---------------|
| said | 97 | Neutral statements |
| asked | 33 | Direct questions |
| answered | 30 | Response to questions |
| spoke | 19 | Formal/emotional speech |
| conveyed | 12 | Telepathic communication |
| whispered | 8 | Intimate/secret dialogue |
| shouted | 6 | Urgent/distant communication |

### Telepathy Convention
Telepathic communication uses "conveyed the thought" construction:
> "'There are hardly any sentinels to be seen,' you conveyed the thought to Haji."

Unit-based communication (linking to technology):
> "Re-establishing the link to his Unit, you conveyed the thought to him, 'Let's go.'"

### Dialogue Punctuation
- Single quotes for all dialogue: 'text'
- Em-dash not used for interruption
- Ellipsis (...) for trailing speech
- Dialogue tags after comma: 'Text,' he said.

### Character Voice Differentiation

**Alan (Protagonist):**
- Impulsive, questioning authority
- Short, decisive statements in crisis
- Emotional but restrained expression
> "'No,' you said imposingly."
> "'You will never find her,' you uttered in a coarse voice."

**Haji (Loyal Friend):**
- Logical, cautious reasoning
- Longer explanatory sentences
- Formal darmian vocabulary
> "'Entertainment leads to disorder. And that is directly against our Prime Directive.'"

**Wollen (Antagonist):**
- Sardonic, threatening
- Rhetorical questions
- Crude humor mixed with menace
> "'Haven't you had enough?' he asked."
> "'My, my...she is fast to work her charm,' he mocked."

**Cathy (Romantic Interest):**
- Vulnerable, direct emotion
- Questions seeking connection
- Confession-style dialogue
> "'I've always liked you, Alan,' she confessed with some effort."

### Implementation Rules for Generator
✅ ALWAYS: Use single quotes for dialogue  
✅ ALWAYS: Vary dialogue tags (not only "said")  
✅ ALWAYS: Include action beats between dialogue lines  
✅ ALWAYS: Use "conveyed" for telepathic communication  
⚠️ TYPICALLY: Keep dialogue exchanges short in action scenes  
❌ NEVER: Double quotes for dialogue  
❌ NEVER: Said-bookisms (no "ejaculated," "exclaimed" excessively)  

---

## 4. Description Style

### Sensory Balance
- **Visual:** Primary (appearances, movements, expressions)
- **Tactile:** High (pain, cold, physical contact)
- **Auditory:** Moderate (footsteps, voices, clanking)
- **Olfactory:** Rare but impactful (burnt circuits, blood)

### Physical Description Approach

**Character Introduction:**
Detailed physical description for new/transformed characters:
> "His appearance was grotesque, a tall long-limbed body made of decayed flesh and silvery metal, all bound together by screws and sutures."

**Action Description:**
Movement-focused, sparse adjectives:
> "With two simple hops he covered the distance between you and sunk a knee in your ribs."

**Setting Description:**
Environmental details woven into action:
> "The Manufacturing Sector was nothing more than a dark quiet place, whose empty streets and tall shadowy buildings resembled more the surreal constructs of nightmares."

### Metaphor/Simile Patterns
Limited but effective use:
> "...like a hammer striking solid metal"
> "...like an agile animal"
> "...like the last drops of rain in an everlasting night"

### Show-Don't-Tell Execution

**Emotion through Body:**
> "Your innocent young features shifted from gentleness to somberness as if you had become a grim, proud pyrean."

**Pain through Sensation:**
> "The freezing wind pierced his face as he curled up in pain, his eyelids shut, his teeth clenched in agony."

### Implementation Rules for Generator
✅ ALWAYS: Show emotion through physical manifestation  
✅ ALWAYS: Weave setting details into character movement  
⚠️ TYPICALLY: Use metaphors sparingly (1-2 per major scene)  
⚠️ TYPICALLY: Prioritize visual and tactile description  
❌ NEVER: Tell emotion directly ("he felt sad")  
❌ NEVER: Purple prose (excessive adjective stacking)  

---

## 5. Pacing & Information Flow

### Scene Pacing Analysis

**Social/Romance Scene (Gathering):**
- Slow, introspective pacing
- Long dialogue exchanges
- Internal emotional processing
- Scene length: Extended (multiple pages)

**Combat Sequences (Wollen Fight):**
- Rapid, staccato pacing
- Short paragraphs, short sentences
- Minimal internal thought
- Physical action dominates

**Transformation Scene:**
- Building tension through physical change
- Sentence rhythm accelerates
- Climactic moment followed by abrupt silence

**Transcendent Epilogue:**
- Dreamlike, flowing pace
- Long compound sentences
- No dialogue, pure narration
- Time perception stretched

### Information Delivery

**Worldbuilding Exposition:**
Delivered through character knowledge and dialogue:
> "'Games, like any other form of entertainment, are not allowed in Darm because they are disruptive to the state of mind necessary to uphold darmian productivity.'"

**Technical Details:**
Natural integration during action:
> "You hastily removed the strange object from her neck; its tip was filled with a single drop of her blood. You pulled the exoderm of your forearm back and allowed the drop to fall onto your Unit..."

### Scene Transitions

**Scene Break (\*\*\*) Usage:**
1. POV shift from protagonist to other character
2. Time skip (hours/days)
3. Location change to distant setting
4. Consciousness shift (death/awakening)

**Within-Scene Transitions:**
New paragraph, no marker, for minor time/location shifts

### Implementation Rules for Generator
✅ ALWAYS: Match sentence length to scene intensity  
✅ ALWAYS: Use *** for major transitions  
✅ ALWAYS: Deliver worldbuilding through dialogue/action  
⚠️ TYPICALLY: Slow pacing for emotional scenes  
❌ NEVER: Info-dumps in narrator voice  
❌ NEVER: Scene breaks within continuous action  

---

## 6. Chapter/Scene Structure

### Section 3 Structure
- **The Gathering (Memory 10):** Social/romantic scene
- **Pursuit & Combat:** Escape from Hub, Wollen confrontation
- **Transformation:** Alan's rage-induced physical change
- **Death & Silence:** Haji's death, Alan's wounding
- **Epilogue:** Transcendent awakening

### Scene Break Count: 7

### Scene Opening Patterns

**Action Opening:**
> "Standing next to Haji's lifeless body, Wollen turned to look at you."

**Transitional Opening:**
> "A chilling wind blew on your face as your consciousness sunk into an ever-darker abyss."

**Atmospheric Opening:**
> "A single resounding boom echoed in a darkened void."

### Scene Closing Patterns

**Cliffhanger Close:**
> "Then, you were struck by a shock wave of pain..."

**Ellipsis/Silence Close:**
> "...not even after a thousand deaths would I spare you from retribution..."

**Finality Close:**
> "Then, there was nothingness."

### Implementation Rules for Generator
✅ ALWAYS: Use *** for scene breaks  
✅ ALWAYS: Vary scene opening types  
⚠️ TYPICALLY: End action scenes on cliffhangers  
⚠️ TYPICALLY: End emotional scenes with reflection  
❌ NEVER: Abrupt scene end without closure  

---

## 7. Worldbuilding Integration

### Technical Terminology Density

| Category | Unique Terms | Top Terms |
|----------|-------------|-----------|
| Technology | 16 | Mother (31), facemask (18), sentinels (14), Unit (14), droids (12) |
| Society | 19 | Companion (25), Specialists (18), Darm (16), Apprentices (15) |
| Concepts | 9 | existence (18), Torment (9), Gathering (8), Directive (6) |
| Locations | 9 | Field (17), Hub (13), Boulevard (11), Shelter (9) |

### Integration Methods

**Natural Dialogue:**
> "'You sound just like a Mentalist,' you said with discomfort."

**Action Context:**
> "Through their featureless visages came the automated voice of Mother in unison..."

**Character Knowledge:**
> "They were Stalkers, droids designed for the sole purpose of capturing darmians who had strayed too far from Darm's directives..."

### Term Introduction Pattern
First use includes brief contextual explanation, subsequent uses assume reader familiarity.

### Implementation Rules for Generator
✅ ALWAYS: Introduce terms through context/action  
✅ ALWAYS: Use consistent terminology  
⚠️ TYPICALLY: 3-5 technical terms per paragraph maximum  
❌ NEVER: Define terms in narrator exposition  
❌ NEVER: Overload single scene with new terminology  

---

## 8. Tone & Emotional Register

### Emotional Spectrum in Section 3
1. **Vulnerability** (Gathering romance scene)
2. **Tension** (Sentinel avoidance)
3. **Horror** (Wollen's grotesque appearance)
4. **Rage** (Transformation scene)
5. **Grief** (Haji's death)
6. **Transcendence** (Epilogue awakening)

### Intensity Management

**Restraint in Violence:**
Even brutal combat maintains prose restraint:
> "Wollen delivered a crushing blow to his face, his feet were lifted off the ground, his body spun in midair and he fell face down on the snow."

**Emotion Through Action:**
> "His words filled your mind with anger and your eyes were kindled with rage. You growled through gritted teeth..."

### Physical Manifestation of Emotion
- **Fear:** Pounding heart, frozen body
- **Anger:** Burning sensation, convulsing muscles
- **Grief:** Tears, desperate cries
- **Wonder:** Wide eyes, awe-stricken tone

### Melodrama Avoidance
- No excessive exclamation marks in narration
- Characters don't monologue their feelings
- Physical reactions replace emotional statements
- Understatement at climactic moments

### Implementation Rules for Generator
✅ ALWAYS: Show emotion through body  
✅ ALWAYS: Maintain restraint in violent scenes  
✅ ALWAYS: Use environmental mirroring (cold = isolation)  
⚠️ TYPICALLY: Build intensity gradually  
❌ NEVER: Tell reader character emotions directly  
❌ NEVER: Melodramatic exclamations in narration  

---

## 9. Character Voice Differentiation

### Alan (Protagonist)
- **Traits:** Impulsive, questioning, protective
- **Speech:** Direct, short sentences in crisis
- **Thought:** Drawn to mystery, rebels against rules
> "'No,' you said imposingly."
> "'We have to help her,' you pleaded to him."

### Haji (Best Friend)
- **Traits:** Logical, loyal, cautious
- **Speech:** Longer explanatory sentences, formal
- **Thought:** Analytical, concerned for consequences
> "'I don't think we should,' Haji shouted. 'I have a bad feeling about helping her.'"

### Wollen (Antagonist)
- **Traits:** Grotesque, sardonic, cruel
- **Speech:** Mocking, rhetorical questions
- **Markers:** "chuckled," "sneered," "mocked"
> "'Haven't you had enough?' he asked."
> "'My, my...she is fast to work her charm,' he mocked."

### Cathy (Romantic Interest)
- **Traits:** Vulnerable, hopeful, direct
- **Speech:** Emotional confession style
> "'I've always liked you, Alan,' she confessed with some effort."

### Sophie (Mysterious)
- **Traits:** Playful, connected to Haji
- **Speech:** Teasing, affectionate
> "'You two have been here all evening,' said Sophie, frowning at Haji."

### Narrator/Soul Voice
- **Format:** Italicized passages in ellipsis format
- **Tone:** Philosophical, omniscient, poetic
> "...not even after a thousand deaths would I spare you from retribution..."
> "...your future is, and will always be, a reflection of your past..."

### Implementation Rules for Generator
✅ ALWAYS: Differentiate character speech patterns  
✅ ALWAYS: Match vocabulary to character education/role  
⚠️ TYPICALLY: Give antagonists distinctive speech markers  
❌ NEVER: Give all characters identical speech patterns  

---

## 10. Technical Writing Choices

### Formatting Conventions

**Italics (represented as ...text...):**
- Internal monologue/soul commentary
- Philosophical narrator voice
- Mystical/transcendent passages

**Scene Breaks (\*\*\*):**
- Major POV shifts
- Significant time jumps
- Location changes
- Consciousness transitions

### Quotation Style
- Single quotes for dialogue: 'text'
- No nested dialogue observed in sample

### Tense Usage
- **Past tense:** Primary narrative action
- **Present tense:** Narrator commentary, internal monologue

### Capitalization
- Proper nouns: Darm, Mother, Unit, Torment
- Titles/roles: Mentalist, Specialist, Apprentice, Companion
- Locations: Hub, Boulevard, Shelter

### Implementation Rules for Generator
✅ ALWAYS: Single quotes for dialogue  
✅ ALWAYS: Capitalize proper nouns and titles  
✅ ALWAYS: Use *** for scene breaks  
✅ ALWAYS: Italicize internal monologue (format as ...text...)  
⚠️ TYPICALLY: Past tense narration  
❌ NEVER: Double quotes for dialogue  

---

## Structural Templates

### Scene Opening Templates

**Pattern 1: Action Resumption**
```
[Immediate action/reaction]. [Character] [verb] [consequence]. [Protagonist observation].
Example: "Standing next to Haji's lifeless body, Wollen turned to look at you."
```

**Pattern 2: Environmental Transition**
```
[Atmospheric description]. [Sensory detail]. [Internal state].
Example: "A chilling wind blew on your face as your consciousness sunk into an ever-darker abyss."
```

**Pattern 3: Dialogue Entry**
```
'[Direct dialogue],' [character] [verb] to [target].
Example: "'There are hardly any sentinels to be seen,' you conveyed the thought to Haji."
```

**Pattern 4: Transcendent Opening**
```
[Abstract phenomenon]. [Expansion]. [Awakening].
Example: "A single resounding boom echoed in a darkened void."
```

### Scene Closing Templates

**Pattern 1: Finality**
```
[Final action]. Then, [silence/nothingness/stillness].
Example: "He coughed once, his lungs drew one last meager breath, and his heart gave out. Then, there was nothingness."
```

**Pattern 2: Ellipsis Commentary**
```
...[philosophical/ominous statement]...
Example: "...not even after a thousand deaths would I spare you from retribution..."
```

**Pattern 3: Transition Hook**
```
[Action completed]. [Character] [departure verb]. [Scene ends].
Example: "She grabbed his left paw and pulled him away into the hall."
```

### Dialogue Exchange Templates

**Standard Exchange:**
```
'[Question/statement],' [pronoun] [tag].
[Action beat].
'[Response],' [character] [tag]. [Descriptor/action].
```

**Telepathic Exchange:**
```
'[Thought content],' you conveyed the thought to [character].
'[Response],' [character] answered back.
```

---

## Vocabulary Fingerprint

### Distinctive Word Choices
- **convey/conveyed** - telepathic communication
- **existence** - life/being (darmian concept)
- **countenance** - face/expression
- **fervor** - emotional intensity
- **recoiled** - physical reaction
- **comprised** - formal composition
- **beleaguered** - under pressure
- **unremitting** - continuous
- **gestalt** - unified whole

### Technical Vocabulary (Top 20)
1. Mother - AI overseer
2. facemask - protective gear
3. sentinels - patrol droids
4. Unit - personal tech device
5. droids - robots
6. Companion - life partner
7. Specialists - elite workers
8. Darm - city/society
9. Apprentices - young citizens
10. Field - energy barrier area
11. Hub - central location
12. Boulevard - main street
13. exoderm - outer skin layer
14. Torment - environmental hazard
15. Gathering - social event
16. Directive - rule/law
17. Shelter - safe house
18. Stalkers - hunter droids
19. pyrean - human-like species
20. Mentalist - intellectual class

### Avoided Vocabulary
- Modern Earth slang
- Contemporary technology terms
- Casual contractions in narration

---

## Example Passages

### A. Action Sequence (Combat)
**Source:** Wollen confrontation  
**Context:** Haji fighting transformed creature  
**Style Features:** Short sentences, physical detail, pacing acceleration

> "The impact was so overwhelming that it shattered Haji's left forearm and threw him backwards. Overwhelmed with sharp pain, Haji was soon struck by a vicious barrage of jabs that lit the alley in red each time Wollen's hand struck his body. Then, one hook to the face sent Haji's facemask flying to one side and his body crashing to the ground."

### B. Social/Romantic Scene
**Source:** The Gathering  
**Context:** Cathy's romantic advance  
**Style Features:** Internal conflict, physical awkwardness, emotional restraint

> "For what seemed an eternity, your eyes remained open and you remained stone cold, neither accepting nor refusing her passionate kiss, as her wet lips eagerly felt yours. To that day, Cathy had been the only girl with whom you had shared some level of intimacy, and you had imagined that kissing her would be an epiphany of joy. But now that you did, now that the kiss was happening, you felt nothing other than skin pressed against wet skin and the insipid taste of her saliva."

### C. Transformation Scene
**Source:** Alan's rage transformation  
**Context:** Protagonist's physical change under emotional stress  
**Style Features:** Building intensity, physical metamorphosis, loss of control

> "A fiery rage took complete hold of you. All the pain was suppressed by a burning sensation and your body began to grow uncontrollably, your head becoming too large for Wollen's hand to grasp. With one increasingly growing hand, you grabbed his stretched out arm and with impossible strength snapped it in two with a single crushing grip."

### D. Transcendent Epilogue
**Source:** Prelude to Ascension  
**Context:** Entity awakening  
**Style Features:** POV shift to "she," lyrical prose, metaphysical imagery

> "And where once was darkness, now there was light. It was then that the entity became aware of herself. Her senses awoke, and she felt the warm embrace of the light surrounding her and heard for the first time the distant singing that echoed in the infinite white."

### E. Internal Monologue (Italicized)
**Source:** Throughout section  
**Context:** Narrator/soul commentary  
**Style Features:** Present tense, philosophical, omniscient perspective

> "...not even after a thousand deaths would I spare you from retribution..."
> "...your future is, and will always be, a reflection of your past; and, at the same time, your past will always be a reflection of your future..."

---

## Red Flags (Style Violations)

**These patterns would break authenticity:**

❌ First-person ("I did") outside italicized commentary  
❌ Double quotes for dialogue ("text" instead of 'text')  
❌ Present tense for action narration ("you look" instead of "you looked")  
❌ Modern Earth terminology (phone, car, computer)  
❌ Excessive exclamation marks in narration  
❌ Telling emotions ("he felt angry") instead of showing  
❌ Info-dump paragraphs explaining world mechanics  
❌ All characters speaking with identical patterns  
❌ Scene breaks within continuous action  
❌ Purple prose/excessive adjective stacking  
❌ Contractions in formal narration  
❌ Third-person for protagonist outside transcendent scenes  
❌ Dialogue without action beats  
❌ Breaking from second-person in main narrative  

---

## Generator Directives

### Critical Instructions for style-transfer-generator

**ALWAYS maintain:**
1. Second-person POV ("you") for protagonist
2. Single quotes for dialogue
3. Italicized internal monologue (...text...)
4. Scene breaks (***) for major transitions
5. Past tense for action, present for commentary
6. Physical manifestation of emotion
7. Technical vocabulary integration
8. Varied sentence length based on scene type
9. Dialogue tag variety
10. Restraint in violent/emotional scenes

**ADAPT based on context:**
1. Pacing (fast for combat, slow for social)
2. Dialogue density (higher in social scenes)
3. Description detail (more for new elements)
4. Sentence length distribution
5. Internal monologue frequency

**NEVER violate:**
1. POV consistency (second-person main narrative)
2. Dialogue formatting (single quotes)
3. Scene break convention (***)
4. Worldbuilding integration (no info-dumps)
5. Emotional restraint principle

---

## Validation Checklist

**For generator to verify style transfer success:**

- [ ] POV is second-person throughout main narrative
- [ ] Dialogue uses single quotes
- [ ] Internal monologue in italicized ...text... format
- [ ] Scene breaks use *** marker
- [ ] Sentence length varies by scene type
- [ ] Average sentence length within 14-18 words
- [ ] Dialogue ratio between 40-55% for social scenes
- [ ] No forbidden vocabulary or style violations
- [ ] Tonal consistency with original
- [ ] Character voices differentiated
- [ ] Worldbuilding terms naturally integrated
- [ ] No info-dump exposition
- [ ] Physical emotion manifestation (not telling)
- [ ] Technical terms capitalized consistently
