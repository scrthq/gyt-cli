import importlib.metadata

_DISTRIBUTION_METADATA = importlib.metadata.metadata("gyt-cli")

__version__ = _DISTRIBUTION_METADATA["Version"]
