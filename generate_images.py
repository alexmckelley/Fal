#!/usr/bin/env python3
"""
Generate NFT images via fal.ai queue API.

Usage:
    python generate_images.py                    # generate all 2000
    python generate_images.py --start 1 --end 20 # generate #0001-#0020
    python generate_images.py --start 50 --end 50 # generate just #0050
    python generate_images.py --redo 3,17,42      # redo specific token IDs
"""

import argparse
import json
import os
import sys
import time

import requests

# ── Config ───────────────────────────────────────────────────────────────────

FAL_KEY = os.environ.get("FAL_KEY", "")
MODEL_ID = "fal-ai/nano-banana"
QUEUE_URL = f"https://queue.fal.run/{MODEL_ID}"
COLLECTION_PATH = "output/full_collection.json"
IMAGES_DIR = "output/images"
DELAY_BETWEEN_REQUESTS = 1.0  # seconds between submitting requests
POLL_INTERVAL = 2.0           # seconds between status polls
MAX_POLL_ATTEMPTS = 150       # max polls per image (~5 min)
MAX_RETRIES = 3               # retries on failure per image

# ── Helpers ──────────────────────────────────────────────────────────────────

def headers():
    return {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json",
    }


def auth_headers():
    return {"Authorization": f"Key {FAL_KEY}"}


def submit_request(prompt: str) -> dict:
    """Submit an image generation request to the fal.ai queue."""
    payload = {
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "output_format": "png",
        "num_images": 1,
    }
    resp = requests.post(QUEUE_URL, headers=headers(), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def poll_until_done(status_url: str) -> str:
    """Poll the queue until the request completes. Returns the response URL status."""
    for attempt in range(MAX_POLL_ATTEMPTS):
        resp = requests.get(
            status_url,
            headers=auth_headers(),
            params={"logs": 1},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status", "UNKNOWN")

        if status == "COMPLETED":
            return "COMPLETED"
        elif status in ("FAILED", "CANCELLED"):
            error_msg = data.get("error", "Unknown error")
            raise RuntimeError(f"Request {status}: {error_msg}")

        time.sleep(POLL_INTERVAL)

    raise TimeoutError(f"Request did not complete after {MAX_POLL_ATTEMPTS} polls")


def fetch_result(response_url: str) -> dict:
    """Fetch the final result from the queue."""
    resp = requests.get(response_url, headers=auth_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()


def download_image(image_url: str, dest_path: str):
    """Download an image from URL to local file."""
    resp = requests.get(image_url, timeout=120)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(resp.content)


def generate_single(token_id: int, prompt: str, force: bool = False) -> bool:
    """Generate a single image. Returns True on success, False on failure."""
    filename = f"{token_id:04d}.png"
    dest_path = os.path.join(IMAGES_DIR, filename)

    # Resume capability: skip if already exists (unless force/redo)
    if not force and os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return True  # already done

    for retry in range(MAX_RETRIES):
        try:
            # Step 1: Submit to queue
            queue_resp = submit_request(prompt)
            request_id = queue_resp.get("request_id", "?")
            status_url = queue_resp.get("status_url")
            response_url = queue_resp.get("response_url")

            if not status_url or not response_url:
                raise RuntimeError(f"Missing status/response URLs in queue response: {queue_resp}")

            # Step 2: Poll until done
            poll_until_done(status_url)

            # Step 3: Fetch result
            result = fetch_result(response_url)

            # Step 4: Extract image URL and download
            images = result.get("images", [])
            if not images:
                # Some models return output.images or data.images
                output = result.get("output", result.get("data", {}))
                if isinstance(output, dict):
                    images = output.get("images", [])

            if not images:
                raise RuntimeError(f"No images in response: {json.dumps(result)[:500]}")

            image_url = images[0].get("url") if isinstance(images[0], dict) else images[0]
            if not image_url:
                raise RuntimeError(f"No URL in image data: {images[0]}")

            download_image(image_url, dest_path)
            return True

        except Exception as e:
            wait = 2 ** (retry + 1)
            print(f"    [!] Attempt {retry + 1}/{MAX_RETRIES} failed: {e}")
            if retry < MAX_RETRIES - 1:
                print(f"    [!] Retrying in {wait}s...")
                time.sleep(wait)

    return False


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    global QUEUE_URL, DELAY_BETWEEN_REQUESTS

    parser = argparse.ArgumentParser(description="Generate NFT images via fal.ai")
    parser.add_argument("--start", type=int, default=1, help="First token ID (default: 1)")
    parser.add_argument("--end", type=int, default=2000, help="Last token ID (default: 2000)")
    parser.add_argument("--redo", type=str, default="", help="Comma-separated token IDs to regenerate")
    parser.add_argument("--delay", type=float, default=DELAY_BETWEEN_REQUESTS, help="Delay between requests in seconds")
    parser.add_argument("--model", type=str, default=MODEL_ID, help=f"fal.ai model ID (default: {MODEL_ID})")
    args = parser.parse_args()

    if args.model != MODEL_ID:
        QUEUE_URL = f"https://queue.fal.run/{args.model}"
    DELAY_BETWEEN_REQUESTS = args.delay

    if not FAL_KEY:
        print("ERROR: FAL_KEY environment variable not set.")
        sys.exit(1)

    # Load collection
    with open(COLLECTION_PATH) as f:
        collection = json.load(f)

    # Build lookup by token_id
    agents_by_id = {a["token_id"]: a for a in collection}

    # Determine which IDs to process
    if args.redo:
        token_ids = [int(x.strip()) for x in args.redo.split(",") if x.strip()]
        force = True
        print(f"REDO mode: regenerating {len(token_ids)} specific images")
    else:
        token_ids = list(range(args.start, args.end + 1))
        force = False
        print(f"Generating images #{args.start:04d} to #{args.end:04d} ({len(token_ids)} total)")

    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Count already done (for resume display)
    already_done = 0
    to_generate = []
    for tid in token_ids:
        if tid not in agents_by_id:
            print(f"WARNING: Token ID {tid} not found in collection, skipping")
            continue
        dest = os.path.join(IMAGES_DIR, f"{tid:04d}.png")
        if not force and os.path.exists(dest) and os.path.getsize(dest) > 0:
            already_done += 1
        else:
            to_generate.append(tid)

    print(f"Already completed: {already_done}")
    print(f"To generate: {len(to_generate)}")
    print(f"Model: {args.model}")
    print(f"Delay between requests: {DELAY_BETWEEN_REQUESTS}s")
    print("-" * 50)

    if not to_generate:
        print("Nothing to generate — all images already exist!")
        return

    successes = 0
    failures = 0
    failed_ids = []

    for i, tid in enumerate(to_generate):
        agent = agents_by_id[tid]
        progress = f"[{i + 1}/{len(to_generate)}]"
        print(f"{progress} #{tid:04d} ({agent['rarity']})...", end=" ", flush=True)

        ok = generate_single(tid, agent["prompt"], force=force)

        if ok:
            successes += 1
            print("OK")
        else:
            failures += 1
            failed_ids.append(tid)
            print("FAILED")

        # Rate limiting delay (skip after last one)
        if i < len(to_generate) - 1:
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("=" * 50)
    print("GENERATION COMPLETE")
    print("=" * 50)
    print(f"Successful: {successes}")
    print(f"Failed:     {failures}")
    print(f"Skipped:    {already_done}")
    if failed_ids:
        ids_str = ",".join(str(x) for x in failed_ids)
        print(f"\nFailed IDs (re-run with --redo {ids_str}):")
        for tid in failed_ids:
            print(f"  #{tid:04d}")


if __name__ == "__main__":
    main()
