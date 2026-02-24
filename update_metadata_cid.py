#!/usr/bin/env python3
"""
Replace YOUR_CID_HERE in all metadata files with an actual IPFS CID.

Usage:
    python update_metadata_cid.py QmYourActualCIDHere
"""

import json
import os
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python update_metadata_cid.py <IPFS_CID>")
        print("Example: python update_metadata_cid.py QmXy7z...")
        sys.exit(1)

    cid = sys.argv[1].strip()
    metadata_dir = "output/metadata"

    if not os.path.isdir(metadata_dir):
        print(f"ERROR: {metadata_dir} not found. Run generate_prompts.py first.")
        sys.exit(1)

    updated = 0
    for filename in sorted(os.listdir(metadata_dir)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(metadata_dir, filename)
        with open(path) as f:
            data = json.load(f)

        old_image = data.get("image", "")
        new_image = old_image.replace("YOUR_CID_HERE", cid)

        if new_image != old_image:
            data["image"] = new_image
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            updated += 1

    print(f"Updated {updated} metadata files with CID: {cid}")
    if updated == 0:
        print("(No files contained YOUR_CID_HERE — were they already updated?)")


if __name__ == "__main__":
    main()
