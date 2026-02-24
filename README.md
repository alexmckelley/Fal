# Chibi Agents NFT — Image Generation Pipeline

A pipeline for generating a 2000-piece chibi secret agent NFT collection using fal.ai.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set your fal.ai API key
export FAL_KEY="your-fal-api-key-here"
```

## Step 1: Generate Prompts & Metadata

```bash
python generate_prompts.py
```

This creates:
- `output/full_collection.json` — all 2000 agents with prompts, traits, and rarity
- `output/prompts_only.txt` — just prompts, one per line
- `output/metadata/0001.json` through `output/metadata/2000.json` — OpenSea-standard metadata

### Rarity Distribution
| Rarity    | Count | Percentage |
|-----------|-------|------------|
| Common    | 400   | 20%        |
| Uncommon  | 760   | 38%        |
| Rare      | 600   | 30%        |
| Legendary | 240   | 12%        |

## Step 2: Generate Images

```bash
# Test batch (first 20)
python generate_images.py --start 1 --end 20

# Full run (all 2000)
python generate_images.py

# Redo specific images
python generate_images.py --redo 3,17,42

# Use a different model
python generate_images.py --model fal-ai/nano-banana-pro

# Adjust delay between requests (default 1.0s)
python generate_images.py --delay 2.0
```

Features:
- **Resume capability** — re-running skips already-downloaded images
- **Batch support** — use `--start` and `--end` to generate a range
- **Redo mode** — `--redo 3,17,42` regenerates only those token IDs
- **Rate limiting** — configurable delay between requests
- **Auto-retry** — 3 retries per image with exponential backoff
- **Progress tracking** — reports success/failure counts and lists failed IDs

Images are saved to `output/images/0001.png` through `output/images/2000.png`.

## Step 3: Update Metadata with IPFS CID

After uploading images to IPFS:

```bash
python update_metadata_cid.py QmYourActualCIDHere
```

This replaces `YOUR_CID_HERE` in all 2000 metadata files with your real CID.

## Project Structure

```
chibi-agents-nft/
├── generate_prompts.py      # Phase 1: trait generation & metadata
├── generate_images.py       # Phase 2: fal.ai image generation
├── update_metadata_cid.py   # Phase 3: IPFS CID replacement
├── requirements.txt
├── README.md
└── output/                  # created by scripts
    ├── full_collection.json
    ├── prompts_only.txt
    ├── metadata/
    │   ├── 0001.json
    │   └── ...
    └── images/
        ├── 0001.png
        └── ...
```
