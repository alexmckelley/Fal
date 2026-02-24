#!/usr/bin/env python3
"""Generate 2000 unique chibi agent NFT trait combinations."""

import json
import os
import random
from collections import Counter

random.seed(42)

# ── Trait pools ──────────────────────────────────────────────────────────────

SUIT_STYLES = [
    "black suit black tie", "black suit black turtleneck",
    "black suit open collar black shirt", "black suit white shirt loose tie",
    "black suit white shirt skinny black tie", "black double-breasted suit",
    "black three-piece suit with vest visible", "black suit mandarin collar",
    "black suit buttoned all the way up", "black suit rolled sleeves",
    "rumpled black suit no tie", "sharp black suit black shirt",
    "crisp black suit white shirt black tie", "black suit with pocket square",
]

SUNGLASSES = [
    "black aviator sunglasses", "black wayfarer sunglasses",
    "round black sunglasses", "rectangular black sunglasses",
    "wraparound black sunglasses", "black clubmaster sunglasses",
    "cat-eye black sunglasses", "oval black sunglasses",
    "angular black sunglasses", "thin rectangular black sunglasses",
]

HAIR_STYLES = [
    "short spiky hair", "long straight hair", "messy curly hair",
    "slicked back hair", "short buzzcut", "long wavy hair with bangs",
    "short textured hair with undercut", "medium tousled hair",
    "neat short hair with side part", "short choppy hair",
    "tight braids pulled back", "short flat-top military haircut",
    "messy medium hair with bangs", "long hair in a bun", "mohawk",
    "shoulder length straight hair",
]

HAIR_COLORS = [
    "black", "dark brown", "light brown", "blonde", "dark blonde",
    "platinum blonde", "red", "dark red", "auburn", "silver-white",
    "dusty blue", "pink", "gray", "jet black", "strawberry blonde",
    "purple", "green-tinted black",
]

SKIN_TONES = [
    "pale skin", "light skin", "fair pink skin", "light tan skin",
    "olive skin", "warm medium skin", "tan skin", "warm golden-brown skin",
    "brown skin", "dark brown skin", "deep dark skin", "pale porcelain skin",
]

ACCESSORIES = [
    "coiled clear earpiece", "radio earpiece with coiled cord",
    "single earpiece", "american flag lapel pin", "silver lapel pin",
    "badge lanyard tucked into jacket", "pen clipped to breast pocket",
    "classified folder peeking from jacket", "cigarette behind ear",
    "silver tie clip", "chain connecting ear cuff to collar",
    "dog tags tucked under shirt", "wristwatch peeking from sleeve",
]

TATTOOS = [
    "neck tattoo peeking above collar", "hand tattoos visible",
    "sleeve tattoo peeking from cuff", "teardrop face tattoo",
    "spider web tattoo on neck", "barcode tattoo on neck",
    "cross tattoo under eye", "snake tattoo crawling up neck",
    "rose tattoo behind ear", "skull tattoo behind ear",
    "flame tattoo on neck", "knuckle tattoos", "star tattoo behind ear",
    "dagger tattoo on hand", "forearm tattoos visible",
]

PIERCINGS = [
    "gold nose stud", "silver nose ring", "septum ring", "bull nose ring",
    "eyebrow piercing", "lip ring", "double nose ring",
    "industrial ear piercing", "double hoop earring", "ear cuff",
    "chain nose ring to ear cuff", "tongue piercing",
]

FRECKLES = [
    "freckles on nose", "scattered freckles across cheeks",
    "light freckles", "subtle freckles",
]

BACKGROUNDS = [
    "grainy surveillance footage of parking garage",
    "underground bunker with red emergency lights",
    "cork board with red string conspiracy wall",
    "foggy black helicopter tarmac",
    "empty interrogation room single lightbulb",
    "redacted documents scattered desk",
    "shadowy hallway with flickering fluorescent lights",
    "desert highway Area 51 searchlights",
    "secret underground lab with green glowing tubes",
    "rainy night embassy rooftop with satellite dishes",
    "long dark corridor with single red exit sign",
    "foggy bridge at midnight with distant headlights",
    "empty parking structure with flickering lights",
    "dark server room with rows of blinking blue lights",
    "restricted military hangar with draped tarps",
    "desert night sky with distant unmarked warehouse",
    "dimly lit war room with glowing monitors",
    "satellite dish array in desert at night",
    "blacked out SUV motorcade on rainy street",
    "abandoned warehouse with scattered classified files",
    "rooftop at night with distant radio tower blinking red",
    "deep underground tunnel with pipes and dim yellow lights",
    "static-filled TV screens in dark control room",
    "airport tarmac with unmarked black helicopter",
    "night sky with blurry UFO and searchlights",
    "Pentagon hallway with fluorescent lighting",
    "blurry redacted documents and filing cabinets",
]

EXPRESSIONS = [
    "tiny neutral mouth", "tiny flat mouth", "small expressionless mouth",
    "small flat mouth", "tiny straight mouth",
]

# ── Rarity-weighted optional trait selection ─────────────────────────────────
# Target distribution:
#   Common  (0 extras): ~20%  -> 400
#   Uncommon(1 extra):  ~38%  -> 760
#   Rare    (2 extras): ~30%  -> 600
#   Legendary(3-4 extras):~12% -> 240

RARITY_WEIGHTS = {
    0: 400,   # Common
    1: 760,   # Uncommon
    2: 600,   # Rare
    3: 200,   # Legendary (3 extras)
    4: 40,    # Legendary (4 extras)
}

RARITY_LABELS = {
    0: "Common",
    1: "Uncommon",
    2: "Rare",
    3: "Legendary",
    4: "Legendary",
}

OPTIONAL_CATEGORIES = [
    ("accessory", ACCESSORIES),
    ("tattoo", TATTOOS),
    ("piercing", PIERCINGS),
    ("freckles", FRECKLES),
]


def pick_extras(num_extras: int) -> dict:
    """Pick which optional categories are active and select a trait from each."""
    cats = random.sample(OPTIONAL_CATEGORIES, k=num_extras)
    result = {}
    for name, pool in OPTIONAL_CATEGORIES:
        if (name, pool) in cats:
            result[name] = random.choice(pool)
        else:
            result[name] = None
    return result


def generate_agent(token_id: int, num_extras: int) -> dict:
    """Generate a single agent's traits."""
    traits = {
        "suit_style": random.choice(SUIT_STYLES),
        "sunglasses": random.choice(SUNGLASSES),
        "hair_style": random.choice(HAIR_STYLES),
        "hair_color": random.choice(HAIR_COLORS),
        "skin_tone": random.choice(SKIN_TONES),
        "background": random.choice(BACKGROUNDS),
        "expression": random.choice(EXPRESSIONS),
    }
    extras = pick_extras(num_extras)
    traits.update(extras)

    rarity = RARITY_LABELS[num_extras]

    # Build prompt
    parts = [
        "Chibi agent, oversized head, large glossy black eyes with white highlights",
        f"{traits['hair_color']} {traits['hair_style']}",
        traits["skin_tone"],
    ]
    if traits.get("freckles"):
        parts.append(traits["freckles"])
    parts.append(traits["expression"])
    parts.append(traits["suit_style"])
    parts.append(traits["sunglasses"])
    if traits.get("accessory"):
        parts.append(traits["accessory"])
    if traits.get("tattoo"):
        parts.append(traits["tattoo"])
    if traits.get("piercing"):
        parts.append(traits["piercing"])
    parts.append("chest-up portrait")
    parts.append(f"{traits['background']} background")
    parts.append("kawaii digital art, NFT collectible card style")

    prompt = ", ".join(parts)

    return {
        "token_id": token_id,
        "traits": traits,
        "rarity": rarity,
        "num_extras": num_extras,
        "prompt": prompt,
    }


def build_opensea_metadata(agent: dict) -> dict:
    """Build OpenSea-standard metadata JSON for a single agent."""
    t = agent["traits"]
    attributes = [
        {"trait_type": "Suit Style", "value": t["suit_style"]},
        {"trait_type": "Sunglasses", "value": t["sunglasses"]},
        {"trait_type": "Hair Style", "value": t["hair_style"]},
        {"trait_type": "Hair Color", "value": t["hair_color"]},
        {"trait_type": "Skin Tone", "value": t["skin_tone"]},
        {"trait_type": "Background", "value": t["background"]},
        {"trait_type": "Expression", "value": t["expression"]},
        {"trait_type": "Rarity", "value": agent["rarity"]},
    ]
    if t.get("accessory"):
        attributes.append({"trait_type": "Accessory", "value": t["accessory"]})
    if t.get("tattoo"):
        attributes.append({"trait_type": "Tattoo", "value": t["tattoo"]})
    if t.get("piercing"):
        attributes.append({"trait_type": "Piercing", "value": t["piercing"]})
    if t.get("freckles"):
        attributes.append({"trait_type": "Freckles", "value": t["freckles"]})

    tid = agent["token_id"]
    return {
        "name": f"Chibi Agent #{tid:04d}",
        "description": "A cute chibi secret agent from the 2000-piece Chibi Agent collection.",
        "image": f"ipfs://YOUR_CID_HERE/{tid:04d}.png",
        "attributes": attributes,
    }


def main():
    # Build the rarity schedule: a list of num_extras values, one per agent
    schedule = []
    for num_extras, count in RARITY_WEIGHTS.items():
        schedule.extend([num_extras] * count)
    assert len(schedule) == 2000, f"Schedule has {len(schedule)} entries, expected 2000"
    random.shuffle(schedule)

    # Generate agents, ensuring uniqueness
    seen_combos = set()
    agents = []
    attempts = 0
    max_attempts = 50000

    for i, num_extras in enumerate(schedule):
        token_id = i + 1
        while attempts < max_attempts:
            attempts += 1
            agent = generate_agent(token_id, num_extras)
            # Create a hashable key from the traits
            t = agent["traits"]
            combo_key = (
                t["suit_style"], t["sunglasses"], t["hair_style"],
                t["hair_color"], t["skin_tone"], t["background"],
                t["expression"],
                t.get("accessory"), t.get("tattoo"),
                t.get("piercing"), t.get("freckles"),
            )
            if combo_key not in seen_combos:
                seen_combos.add(combo_key)
                agents.append(agent)
                break
        else:
            print(f"ERROR: Could not generate unique combo after {max_attempts} attempts")
            return

    # ── Output ───────────────────────────────────────────────────────────────

    os.makedirs("output/metadata", exist_ok=True)
    os.makedirs("output/images", exist_ok=True)

    # full_collection.json
    with open("output/full_collection.json", "w") as f:
        json.dump(agents, f, indent=2)

    # prompts_only.txt
    with open("output/prompts_only.txt", "w") as f:
        for agent in agents:
            f.write(agent["prompt"] + "\n")

    # Individual metadata files
    for agent in agents:
        meta = build_opensea_metadata(agent)
        path = f"output/metadata/{agent['token_id']:04d}.json"
        with open(path, "w") as f:
            json.dump(meta, f, indent=2)

    # ── Summary ──────────────────────────────────────────────────────────────

    rarity_counts = Counter(a["rarity"] for a in agents)
    extras_counts = Counter(a["num_extras"] for a in agents)

    print("=" * 60)
    print("CHIBI AGENT COLLECTION — GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total agents generated: {len(agents)}")
    print(f"Unique combinations verified: {len(seen_combos)}")
    print(f"Generation attempts: {attempts}")
    print()
    print("RARITY DISTRIBUTION:")
    print("-" * 40)
    for label in ["Common", "Uncommon", "Rare", "Legendary"]:
        count = rarity_counts.get(label, 0)
        pct = count / len(agents) * 100
        print(f"  {label:12s}: {count:5d}  ({pct:5.1f}%)")
    print()
    print("EXTRAS BREAKDOWN:")
    print("-" * 40)
    for n in sorted(extras_counts):
        count = extras_counts[n]
        pct = count / len(agents) * 100
        print(f"  {n} extras: {count:5d}  ({pct:5.1f}%)")
    print()

    # Print first 5 prompts
    print("FIRST 5 PROMPTS:")
    print("=" * 60)
    for agent in agents[:5]:
        tid = agent["token_id"]
        print(f"\n[#{tid:04d}] Rarity: {agent['rarity']} ({agent['num_extras']} extras)")
        print(f"  {agent['prompt']}")
    print()

    # Trait frequency stats
    print("TRAIT FREQUENCY HIGHLIGHTS:")
    print("-" * 40)
    for trait_name in ["accessory", "tattoo", "piercing", "freckles"]:
        has_it = sum(1 for a in agents if a["traits"].get(trait_name))
        pct = has_it / len(agents) * 100
        print(f"  {trait_name:12s}: {has_it:5d} agents have one ({pct:5.1f}%)")


if __name__ == "__main__":
    main()
