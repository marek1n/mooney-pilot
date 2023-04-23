from PIL import Image
from pathlib import Path
from tqdm import tqdm

from Katna.image import Image
from Katna.writer import ImageCropDiskWriter



def crop_images(term: str, dls_path: Path):

    cat_path = dls_path / term
    imgs_cat = [imgpath for imgpath in cat_path.glob('**/*') 
                            if ".DS_Store" not in str(imgpath)]

    img_module = Image()

    output_path = cat_path / "cropped"
    output_path.mkdir(parents=True, exist_ok=True)

    diskwriter = ImageCropDiskWriter(location=output_path)

    print(f"Cropping {len(imgs_cat)} images ...\n")

    for img in tqdm(imgs_cat):
        try:
            crop_list = img_module.crop_image_with_aspect(
                file_path=str(img),
                crop_aspect_ratio="1:1",
                num_of_crops=1,
                writer=diskwriter
            )
        except Exception as e:
            print(e)

    print(f"Cropping finished.\nImages saved in {output_path}")


def resize_images(term: str, dls_path: Path):

    cat_path = dls_path / term
    
    img_module = Image()

    cropped = cat_path / "cropped"
    resized = cat_path / "resized"
    resized.mkdir(parents=True, exist_ok=True)

    resized_images = img_module.resize_image_from_dir(
        dir_path=cropped,
        target_width=500,
        target_height=500,
        down_sample_factor=8,
    )
    print("Resizing images ...\n")

    for i, (filepath, resized_image) in enumerate(resized_images.items()):
        img_module.save_image_to_disk(
            resized_image, str(resized), f"{term}_{i}", ".jpeg"
        )
    print(f"Resizing finished.\nImages saved in {resized}")


if __name__ == "__main__":
    # example use
    term = 'cat'
    downloads = Path.cwd()
    crop_images(term, downloads)
    resize_images(term, downloads)
