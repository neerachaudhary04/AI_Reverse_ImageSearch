# pathUpdateModelNPY.py

#It's a one-time setup script:

# Model weights were trained on Google Colab, so the stored gallery paths used Colab-style locations.
# This script rewrites gallery_paths.npy to point at the new path and is only needed for that migration step.
# It isn’t required for the web app or for generating new model weights—only for the initial data move.


import os, numpy as np

BUNDLE = "bundle"
IDX = os.path.join(BUNDLE, "index", "gallery_paths.npy")

# Prefix that appears in .npy (from Colab):
IN_PREFIX = "/content/drive/MyDrive/Capstone_Project/In-Shop Clothes Retrieval/Anno/densepose/"

# output location (relative to bundle/):
OUT_PREFIX = "gallery/"

def main():
    paths = np.load(IDX, allow_pickle=True).tolist()
    new = []
    for p in paths:
        p = str(p)
        if p.startswith(IN_PREFIX):
            rel = OUT_PREFIX + p[len(IN_PREFIX):]
        elif p.startswith("gallery/"):
            rel = p
        else:
            rel = "gallery/" + os.path.basename(p)
        new.append(rel.replace("\\", "/"))

    np.save(IDX, np.array(new, dtype=object))
    print("Rewrote", IDX)

    missing = [q for q in new if not os.path.exists(os.path.join(BUNDLE, q))]
    print("Missing locally:", len(missing))
    print("First few missing:", missing[:5])

if __name__ == "__main__":
    main()
