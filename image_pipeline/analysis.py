import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def save_histogram(values, title, filename, output_dir, bins=50):
    """
    Save histogram of index values (ExG / GLI).
    """
    values = values[~np.isnan(values)]

    plt.figure(figsize=(4, 3))
    plt.hist(values, bins=bins, color="#4CAF50", edgecolor="black")
    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Pixel Count")
    plt.tight_layout()

    # out = Path(output_dir)
    # out.mkdir(parents=True, exist_ok=True)

    path = output_dir / filename
    plt.savefig(path, dpi=150)
    plt.close()

    return path.name