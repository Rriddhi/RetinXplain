from torchvision import transforms

def get_aptos_transforms(phase: str):
    if phase == "train":
        return transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
        ])

def get_idrid_transforms(phase: str):
    """
    TODO: Replace with Albumentations pipeline that jointly augments image + masks.
    For now, just resize.
    """
    def _simple_transform(image, masks):
        image = image.resize((512, 512))
        masks = [m.resize((512, 512)) for m in masks]
        return image, masks

    return _simple_transform
