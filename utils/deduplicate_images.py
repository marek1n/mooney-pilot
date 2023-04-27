from pathlib import Path
from PIL import Image, ImageOps
import imagehash
import numpy as np



def compute_phash(image_path: str | Path) -> tuple[imagehash.ImageHash, ...]:
    """Computes pHash for base image + vertically & horizontally flipped"""
    # load greyscale image
    image = Image.open(image_path)
    
    # mirror (vertical ax) + flip (horizontal ax)
    mirror = ImageOps.mirror(image)
    flip = ImageOps.flip(image)

    phash, mphash, fphash = imagehash.phash(image), \
                            imagehash.phash(mirror), \
                            imagehash.phash(flip)
    
    return phash, mphash, fphash


if __name__ == "__main__":

    FOLDER = '/Users/mn/Desktop/g_images/stim_set_final_by_cat/tree'
    files = [f for f in Path(FOLDER).glob("dis_*.jpg")]
    filenames = list(map(lambda x: str(x).split('/')[-1], files))

    phashz = [compute_phash(img) for img in files]
    
    # compute Hamming distance between all pairs of tuples
    for i, x in enumerate(phashz):
        for j, y in enumerate(phashz):
            if i < j:
                hamming_ds = [(x[k] - y[l]) for k in range(3) for l in range(3)]
                if any(d < 20 for d in hamming_ds):
                    print(f"Hamming distance between {filenames[i]} and {filenames[j]}: {hamming_ds}")
