import os
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset
from torchvision import transforms

def load_canonical_classes(landmark_classes_csv=None):
    """
    Loads canonical 24 landmark classes registry from landmark_classes.csv
    Returns:
      - df_classes: DataFrame
      - num_classes: int (24)
      - class_to_id: dict
      - id_to_class: dict
    """
    if landmark_classes_csv is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        landmark_classes_csv = os.path.join(root_dir, "data", "processed", "landmark_classes.csv")

    df_classes = pd.read_csv(landmark_classes_csv)
    num_classes = len(df_classes)
    class_to_id = dict(zip(df_classes['class_name'], df_classes['class_id']))
    id_to_class = dict(zip(df_classes['class_id'], df_classes['class_name']))
    
    return df_classes, num_classes, class_to_id, id_to_class

class MonumentDataset(Dataset):
    """
    PyTorch Dataset for Monument Landmark Classification (24 Canonical Classes)
    Loads images from processed CSV manifest (train_v2.csv, val_v2.csv, test_v2.csv)
    with runtime transforms.
    """
    def __init__(self, csv_file, root_dir=None, transform=None):
        if root_dir is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        if isinstance(csv_file, str):
            if not os.path.isabs(csv_file):
                csv_file = os.path.join(root_dir, csv_file)
            self.df = pd.read_csv(csv_file)
        else:
            self.df = csv_file
            
        self.root_dir = root_dir
        self.transform = transform
        
        # Load canonical classes
        self.landmark_df, self.num_classes, self.class_to_id, self.id_to_class = load_canonical_classes()

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_rel_path = self.df.iloc[idx]['image_path']
        img_full_path = os.path.join(self.root_dir, img_rel_path)

        image = Image.open(img_full_path).convert('RGB')
        label = int(self.df.iloc[idx]['class_id'])

        if self.transform:
            image = self.transform(image)

        return image, label

def get_transforms(stage='train'):
    """
    Returns standard ImageNet runtime transforms for PyTorch models.
    Target resolution: 224 x 224 RGB
    """
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]

    if stage == 'train':
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=imagenet_mean, std=imagenet_std)
        ])
    else:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=imagenet_mean, std=imagenet_std)
        ])
