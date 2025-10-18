.PHONY: help transcribe transcribe-srt build shorts full clean install

# Default variables
VIDEO ?= video.mp4
MODEL ?= base
DEVICE ?= cpu
COMPUTE_TYPE ?= int8
NUM_SHORTS ?= 5
CRF ?= 17
PRESET ?= medium
OUTDIR ?= runs/$(shell date +%Y%m%d_%H%M%S)

help: ## Show this help message
	@echo "Shorts Builder - Makefile Commands"
	@echo ""
	@echo "Quick Start:"
	@echo "  make transcribe VIDEO=input.mp4          # Transcribe video (CPU)"
	@echo "  make transcribe-gpu VIDEO=input.mp4      # Transcribe video (GPU)"
	@echo "  make transcribe-srt VIDEO=input.mp4      # Get SRT only for Premiere"
	@echo "  make build WORKDIR=runs/TIMESTAMP        # Generate shorts"
	@echo "  make full VIDEO=input.mp4                # Do everything"
	@echo ""
	@echo "Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Variables (override with VAR=value):"
	@echo "  VIDEO=$(VIDEO)"
	@echo "  MODEL=$(MODEL) (tiny/base/small/medium/large-v3)"
	@echo "  DEVICE=$(DEVICE) (cpu/cuda)"
	@echo "  NUM_SHORTS=$(NUM_SHORTS)"
	@echo "  CRF=$(CRF) (quality: 17=high, 23=medium)"
	@echo "  OUTDIR=$(OUTDIR)"

install: ## Install uv and dependencies
	@echo "Installing dependencies with uv..."
	uv sync
	@echo "✓ Ready to go!"

transcribe: ## Transcribe video (CPU, creates SRT + ASS)
	@echo "Transcribing $(VIDEO) with CPU..."
	@mkdir -p $(OUTDIR)
	uv run python scripts/shorts_transcribe.py $(VIDEO) \
		--device $(DEVICE) \
		--compute-type $(COMPUTE_TYPE) \
		--model $(MODEL) \
		--vad \
		--audio-first \
		--outdir $(OUTDIR)
	@echo ""
	@echo "✓ Done! Outputs:"
	@echo "  Transcript: $(OUTDIR)/transcript.jsonl"
	@echo "  SRT:        $(OUTDIR)/captions.srt"
	@echo "  ASS:        $(OUTDIR)/captions.ass"

transcribe-gpu: ## Transcribe video with GPU
	@echo "Transcribing $(VIDEO) with GPU..."
	@mkdir -p $(OUTDIR)
	uv run python scripts/shorts_transcribe.py $(VIDEO) \
		--device cuda \
		--compute-type float16 \
		--model medium \
		--vad \
		--audio-first \
		--outdir $(OUTDIR)
	@echo ""
	@echo "✓ Done! Check $(OUTDIR)/"

transcribe-srt: ## Get SRT file only (for manual Premiere styling)
	@echo "Transcribing $(VIDEO) - SRT for Premiere..."
	@mkdir -p $(OUTDIR)
	uv run python scripts/shorts_transcribe.py $(VIDEO) \
		--device $(DEVICE) \
		--compute-type $(COMPUTE_TYPE) \
		--model $(MODEL) \
		--vad \
		--audio-first \
		--outdir $(OUTDIR)
	@echo ""
	@echo "✓ SRT file ready for Premiere!"
	@echo "  → $(OUTDIR)/captions.srt"
	@echo ""
	@echo "Import to Premiere:"
	@echo "  1. Import your video"
	@echo "  2. File > Import > $(OUTDIR)/captions.srt"
	@echo "  3. Style captions in Essential Graphics panel"

build: ## Build shorts from transcript (requires WORKDIR=runs/...)
ifndef WORKDIR
	@echo "Error: WORKDIR not set!"
	@echo "Usage: make build WORKDIR=runs/20241017_123456"
	@exit 1
endif
	@echo "Building $(NUM_SHORTS) shorts from $(WORKDIR)..."
	uv run python scripts/shorts_builder.py $(VIDEO) \
		--workdir $(WORKDIR) \
		--num-shorts $(NUM_SHORTS) \
		--crf $(CRF) \
		--preset $(PRESET)
	@echo ""
	@echo "✓ Shorts ready!"
	@echo "  → $(WORKDIR)/shorts/"
	@ls -lh $(WORKDIR)/shorts/*.mp4

shorts: build ## Alias for build

full: ## Complete workflow: transcribe + build shorts
	@echo "=== Full Workflow: $(VIDEO) ==="
	@echo ""
	@OUTDIR_FULL=$$(date +runs/%Y%m%d_%H%M%S); \
	echo "Step 1/2: Transcribing..."; \
	$(MAKE) transcribe VIDEO=$(VIDEO) MODEL=$(MODEL) DEVICE=$(DEVICE) OUTDIR=$$OUTDIR_FULL; \
	echo ""; \
	echo "Step 2/2: Building shorts..."; \
	$(MAKE) build VIDEO=$(VIDEO) WORKDIR=$$OUTDIR_FULL NUM_SHORTS=$(NUM_SHORTS) CRF=$(CRF); \
	echo ""; \
	echo "=== ✓ Complete! ==="; \
	echo "  Shorts: $$OUTDIR_FULL/shorts/*.mp4"

quick: ## Quick test: base model, 3 shorts
	@$(MAKE) full VIDEO=$(VIDEO) MODEL=base DEVICE=cpu NUM_SHORTS=3

quality: ## High quality: medium model (slow), CRF 17
	@$(MAKE) full VIDEO=$(VIDEO) MODEL=medium DEVICE=$(DEVICE) CRF=17 PRESET=slow

clean: ## Clean up old runs (keeps last 3)
	@echo "Cleaning old runs (keeping last 3)..."
	@cd runs && ls -t | tail -n +4 | xargs -r rm -rf
	@echo "✓ Cleaned!"

clean-all: ## Delete all runs
	@echo "Deleting all runs..."
	@rm -rf runs/*
	@echo "✓ All runs deleted!"

list: ## List all run directories
	@echo "Available runs:"
	@ls -lth runs/ | grep "^d" | head -10

latest: ## Show path to latest run
	@ls -dt runs/*/ 2>/dev/null | head -1 | tr -d '\n'

# Example workflows
example-basic: ## Example: Basic workflow
	make transcribe VIDEO=my_video.mp4
	make build WORKDIR=runs/20241017_123456 NUM_SHORTS=5

example-premiere: ## Example: Get SRT for Premiere
	make transcribe-srt VIDEO=my_podcast.mp4 MODEL=medium

example-gpu: ## Example: GPU transcription
	make transcribe-gpu VIDEO=my_stream.mp4
	make build WORKDIR=$$(make latest) NUM_SHORTS=10

# Advanced: Custom caption styles
test-captions: ## Test caption rendering on 10s clip
	@echo "Testing captions on first 10 seconds..."
	@LATEST=$$(make latest); \
	ffmpeg -ss 0 -t 10 -i $(VIDEO) \
		-vf "scale=-2:1920,crop=1080:1920,subtitles=$$LATEST/captions.ass" \
		-y test_captions.mp4
	@echo "✓ Preview: test_captions.mp4"

