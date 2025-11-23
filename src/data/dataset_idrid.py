import os
from PIL import Image
from torch.utils.data import Dataset

from .transforms import get_idrid_transforms

class IdridSegmentationDataset(Dataset):
    """
    IDRiD segmentation dataset.
    Expects:
    - images_dir: folder with retinal images
    - masks_dirs: dict with lesion_type -> folder containing corresponding masks
    """

    def __init__(self, images_dir: str, masks_dirs: dict, image_ids: list, phase: str = "train"):
        self.images_dir = images_dir
        self.masks_dirs = masks_dirs  # e.g. {"ma": path_to_ma_masks, "he": path_to_he_masks, ...}
        self.image_ids = image_ids
        self.phase = phase

        self.transforms = get_idrid_transforms(phase)

    def __len__(self):
        return len(self.image_ids)

    def __getitem__(self, idx):
        image_id = self.image_ids[idx]

        img_path = os.path.join(self.images_dir, f"{image_id}.jpg")  # adapt extension
        image = Image.open(img_path).convert("RGB")

        # Build a multi-channel mask (C x H x W)
        masks = []
        for lesion_type, lesion_dir in self.masks_dirs.items():
            mask_path = os.path.join(lesion_dir, f"{image_id}.tif")  # adapt extension
            mask = Image.open(mask_path).convert("L")
            masks.append(mask)

        if self.transforms is not None:
            image, masks = self.transforms(image, masks)

        return image, masks
