#!/bin/bash
# Real-world examples using the Makefile

echo "=== Example 1: Get SRT for Premiere ==="
echo "make transcribe-srt VIDEO=podcast.mp4 MODEL=medium"
echo ""

echo "=== Example 2: Full Auto Workflow ==="
echo "make full VIDEO=gaming_vod.mp4 NUM_SHORTS=10"
echo ""

echo "=== Example 3: Quick Test ==="
echo "make quick VIDEO=test.mp4"
echo ""

echo "=== Example 4: High Quality ==="
echo "make quality VIDEO=important_content.mp4"
echo ""

echo "=== Example 5: GPU Transcription + Manual Build ==="
echo "make transcribe-gpu VIDEO=stream.mp4"
echo "make build WORKDIR=\$(make latest) NUM_SHORTS=15"
echo ""

echo "=== Example 6: Batch Processing ==="
echo "for video in videos/*.mp4; do"
echo "  make full VIDEO=\"\$video\" NUM_SHORTS=5"
echo "done"

