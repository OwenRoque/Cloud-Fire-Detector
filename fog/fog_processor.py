#!/usr/bin/env python3

from utils.logger import setup_logger
from core.processor import FogProcessor

if __name__ == "__main__":
    logger = setup_logger()

    print("=" * 70)
    print("  FOG PROCESSOR - Fire Detection System")
    print("=" * 70)

    processor = FogProcessor(logger)
    processor.start()
