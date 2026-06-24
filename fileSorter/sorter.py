


from __future__ import annotations

import logging
import shutil
from pathlib import Path


logger = logging.getLogger(__name__)


def sort_files(start_path: Path, dest_path: Path, cutoff_year: int, progress_callback=None) -> int:
    """Move year-named files older than ``cutoff_year`` from source to destination.

    For every sub-folder of ``start_path``, a matching folder is created under
    ``dest_path``. Any file whose stem parses as an integer year less than
    ``cutoff_year`` is moved into that mirrored folder.

    Args:
        start_path: Source directory containing sub-folders of files.
        dest_path: Destination directory; mirrored sub-folders are created here.
        cutoff_year: Files with a year strictly less than this are moved.

    Returns:
        The number of files moved.

    Raises:
        ValueError: If either path is missing or not a directory.
    """
    start_path = Path(start_path)
    dest_path = Path(dest_path)

    if not start_path.is_dir():
        raise ValueError(f"Source is not a valid folder: {start_path}")
    if not dest_path.is_dir():
        raise ValueError(f"Destination is not a valid folder: {dest_path}")

    total = 0

    for item in start_path.iterdir():
        if not item.is_dir():
            continue
        for file in item.iterdir():
            if file.is_file():
                total += 1

    moved = 0
    done = 0

    logger.info("Run started. Source=%s Destination=%s Cutoff=%s",
                start_path, dest_path, cutoff_year)

    for item in start_path.iterdir():
        if not item.is_dir():
            continue

        target_dir = dest_path / item.name
        target_dir.mkdir(exist_ok=True)

        for file in item.iterdir():
            if not file.is_file():
                continue
            done += 1
            if progress_callback is not None:
                progress_callback(done, total or 1)   
            
            try:
                file_year = int(file.stem)
            except ValueError:
                logger.info("Skipped non-year file: %s", file.name)
                continue
                
            if file_year < cutoff_year:
                shutil.move(str(file), str(target_dir))
                logger.info("Moved %s -> %s", file.name, target_dir)
                moved += 1
                

    logger.info("Run complete. Moved %d files.", moved)
    return moved
