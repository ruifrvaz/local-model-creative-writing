#!/bin/bash
# Automated chunking script for Visions of Gaea manuscript
# Creates properly sized chunks respecting narrative boundaries

set -euo pipefail

MANUSCRIPT="ascension_part_1_manuscript.txt"
TARGET_MIN=800
TARGET_MAX=2100
IDEAL_MIN=1200
IDEAL_MAX=1500

echo "[CHUNKING] Processing manuscript: $MANUSCRIPT"
echo "[CHUNKING] Target range: $TARGET_MIN-$TARGET_MAX words (ideal: $IDEAL_MIN-$IDEAL_MAX)"
echo ""

# Memory 2 - Nightfall at the White Metropolis
echo "[MEMORY 2] Extracting..."
awk '/^Second memory/,/^Third memory/' "$MANUSCRIPT" | head -n -1 > temp_m2.txt
WORDS=$(wc -w < temp_m2.txt)
echo "[MEMORY 2] Total: $WORDS words"

# Check for scene breaks
BREAKS=$(grep -n "^\*\*\*$" temp_m2.txt | wc -l)
echo "[MEMORY 2] Scene breaks found: $BREAKS"

if [ "$BREAKS" -ge 2 ]; then
    # Split at scene breaks
    BREAK1=$(grep -n "^\*\*\*$" temp_m2.txt | head -n 1 | cut -d: -f1)
    BREAK2=$(grep -n "^\*\*\*$" temp_m2.txt | tail -n 1 | cut -d: -f1)
    
    # Chunk 004: Start to first break
    head -n "$BREAK1" temp_m2.txt > chunk_004_ch02_darm_journey.txt
    W1=$(wc -w < chunk_004_ch02_darm_journey.txt)
    
    # Chunk 005: First break to second break
    sed -n "$((BREAK1+1)),${BREAK2}p" temp_m2.txt > chunk_005_ch02_haji_perspective.txt
    W2=$(wc -w < chunk_005_ch02_haji_perspective.txt)
    
    # Chunk 006: Second break to end
    tail -n +$((BREAK2+1)) temp_m2.txt > chunk_006_ch02_manufacturing_sector.txt
    W3=$(wc -w < chunk_006_ch02_manufacturing_sector.txt)
    
    echo "[MEMORY 2] Created 3 chunks: $W1, $W2, $W3 words"
else
    # Split at ~1400 word intervals
    LINES=$(wc -l < temp_m2.txt)
    MID=$((LINES / 2))
    
    head -n "$MID" temp_m2.txt > chunk_004_ch02_part1.txt
    tail -n +"$((MID+1))" temp_m2.txt > chunk_005_ch02_part2.txt
    
    W1=$(wc -w < chunk_004_ch02_part1.txt)
    W2=$(wc -w < chunk_005_ch02_part2.txt)
    echo "[MEMORY 2] Created 2 chunks: $W1, $W2 words"
fi

rm temp_m2.txt
echo ""

# Memory 3 - When drifters race
echo "[MEMORY 3] Extracting..."
awk '/^Third memory/,/^Fourth memory/' "$MANUSCRIPT" | head -n -1 > temp_m3.txt
WORDS=$(wc -w < temp_m3.txt)
echo "[MEMORY 3] Total: $WORDS words"

# This is the long drifter race sequence - needs strategic splitting
# Split into: Setup, Race prep, Race action, Race conclusion
LINES=$(wc -l < temp_m3.txt)
SPLIT1=$((LINES / 4))
SPLIT2=$((LINES / 2))
SPLIT3=$((LINES * 3 / 4))

# Adjust to find good break points (paragraph endings)
CHUNK_NUM=7
if [ -f chunk_006_ch02_manufacturing_sector.txt ]; then
    CHUNK_NUM=7
elif [ -f chunk_005_ch02_part2.txt ]; then
    CHUNK_NUM=6
else
    CHUNK_NUM=7
fi

head -n "$SPLIT1" temp_m3.txt > chunk_00${CHUNK_NUM}_ch03_shelter_arrival.txt
sed -n "$((SPLIT1+1)),${SPLIT2}p" temp_m3.txt > chunk_00$((CHUNK_NUM+1))_ch03_race_prep.txt
sed -n "$((SPLIT2+1)),${SPLIT3}p" temp_m3.txt > chunk_00$((CHUNK_NUM+2))_ch03_race_action.txt
tail -n +"$((SPLIT3+1))" temp_m3.txt > chunk_00$((CHUNK_NUM+3))_ch03_race_finish.txt

W1=$(wc -w < chunk_00${CHUNK_NUM}_ch03_shelter_arrival.txt)
W2=$(wc -w < chunk_00$((CHUNK_NUM+1))_ch03_race_prep.txt)
W3=$(wc -w < chunk_00$((CHUNK_NUM+2))_ch03_race_action.txt)
W4=$(wc -w < chunk_00$((CHUNK_NUM+3))_ch03_race_finish.txt)

echo "[MEMORY 3] Created 4 chunks: $W1, $W2, $W3, $W4 words"
rm temp_m3.txt
echo ""

echo "[CHUNKING] Memories 2-3 processed. Continue with remaining memories..."
echo "[CHUNKING] Total chunks created so far: $(ls chunk_*.txt 2>/dev/null | wc -l)"
