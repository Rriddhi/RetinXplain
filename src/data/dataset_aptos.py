#Adapted from https://docs.pytorch.org/tutorials/beginner/data_loading_tutorial.html
import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset

from .transforms import get_aptos_transforms

class AptosDataset(Dataset):
    """Diabetic Retinopathy Fundus Image Dataset (for classification)."""
    def __init__(self, csv_file, root_dir, transform=None):
        """
        Args:
            csv_file (string): Path to the CSV file with labels.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to apply on an image.
        """
        self.labels_frame = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.labels_frame)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        # Get the image ID and label
        img_id = str(self.labels_frame.iloc[idx, 0])  
        label = int(self.labels_frame.iloc[idx, 1])

        img_path = os.path.join(self.root_dir, f"{img_id}.png")

        if not os.path.exists(img_path):
            img_path = os.path.join(self.root_dir, f"{img_id}.jpg")

        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)
            
        return image, label
