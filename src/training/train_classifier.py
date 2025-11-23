import torch
from torch.utils.data import DataLoader
from torch import nn, optim
from tqdm import tqdm

from src.data.dataset_aptos import AptosDataset
from src.models.classification.resnet_classifier import ResNetDRClassifier
from src.utils.paths import get_path

def train_classifier(
    train_csv: str,
    val_csv: str,
    images_dir: str,
    num_classes: int = 5,
    epochs: int = 10,
    batch_size: int = 16,
    lr: float = 1e-4,
    device: str = "cuda"
):
    train_dataset = AptosDataset(train_csv, images_dir, phase="train")
    val_dataset = AptosDataset(val_csv, images_dir, phase="val")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    model = ResNetDRClassifier(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_val_loss = float("inf")
    save_path = get_path("models", "aptos", "best_resnet50.pt")

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [train]"):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * images.size(0)

        train_loss /= len(train_loader.dataset)

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [val]"):
                images, labels = images.to(device), labels.to(device)
                logits = model(images)
                loss = criterion(logits, labels)
                val_loss += loss.item() * images.size(0)

        val_loss /= len(val_loader.dataset)
        print(f"Epoch {epoch+1}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), save_path)
            print(f"✅ Saved new best model to {save_path}")

    return model
