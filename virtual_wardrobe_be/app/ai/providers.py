from abc import ABC, abstractmethod
import hashlib
import math
from app.models.entities import DIMENSIONS


class VisionProvider(ABC):
    @abstractmethod
    def analyze(self, image_url: str) -> dict:
        """Return editable clothing metadata for an image."""


class MockVisionProvider(VisionProvider):
    def analyze(self, image_url: str) -> dict:
        return {'category': 'Tops', 'subcategory': 'Shirt', 'color': 'Neutral',
                'pattern': 'Solid', 'material': 'Cotton', 'style': 'Casual',
                'season': 'All season', 'occasion': 'Everyday', 'formality': 2}


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, item: object) -> list[float]:
        """Return a fixed-size unit vector from clothing metadata."""


class MockEmbeddingProvider(EmbeddingProvider):
    def embed(self, item: object) -> list[float]:
        # Stable feature hashing keeps tests deterministic and makes mock similarity useful.
        fields = ['category', 'subcategory', 'color', 'pattern', 'material', 'style', 'season', 'occasion']
        weights = [5, 2, 4, 1, 1, 2, 1, 1]
        vector = [0.0] * DIMENSIONS
        for field, weight in zip(fields, weights):
            value = getattr(item, field, None)
            if value:
                digest = hashlib.sha256(f'{field}:{str(value).strip().lower()}'.encode()).digest()
                vector[int.from_bytes(digest[:4], 'big') % DIMENSIONS] += weight
        norm = math.sqrt(sum(v * v for v in vector)) or 1
        return [v / norm for v in vector]
