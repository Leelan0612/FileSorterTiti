from __future__ import annotations

import logging
import shutil
import filecmp
from send2trash import send2trash
from pathlib import Path


logger = logging.getLogger(__name__)


def sort_files(start_path: Path, dest_path: Path, cutoff_year: int, progress_callback=None) -> int:
    """Move year-named files older than ``cutoff_year`` from source to destination.

    For every sub-folder of ``start_path``, a matching folder is created under
    ``dest_path``. Any file whose stem parses as an integer year less than
    ``cutoff_year`` is moved into that mirrored folder.

    Duplicate handling: if a file with the same name already exists at the
    destination and is byte-for-byte identical, the source copy is sent to the
    recycle bin (removed from the source, not duplicated). If the names match
    but the contents differ, both files are left untouched and the conflict is
    logged, so nothing is ever lost silently.

    Args:
        start_path: Source directory containing sub-folders of files.
        dest_path: Destination directory; mirrored sub-folders are created here.
        cutoff_year: Files with a year strictly less than this are moved.
        progress_callback: Optional callable(done, total) for progress updates.

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
    duplicates_removed = 0
    conflicts = 0

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

                target_path = target_dir / file.name
                if target_path.exists():
                    same = (
                        file.stat().st_size == target_path.stat().st_size
                        and filecmp.cmp(file, target_path, shallow=False)
                    )
                    if same:
                        
                        try:
                            send2trash(str(file))
                            duplicates_removed += 1
                            logger.info("Duplicate removed from source: %s", file.name)
                        except OSError as exc:
                            logger.warning("Could not trash duplicate %s: %s", file.name, exc)
                    else:
                        
                        conflicts += 1
                        logger.warning("Name conflict left in place (different content): %s", file.name)
                    continue

                shutil.move(str(file), str(target_dir))
                logger.info("Moved %s -> %s", file.name, target_dir)
                moved += 1

    logger.info(
        "Run complete. Moved %d, duplicates removed %d, conflicts left %d.",
        moved, duplicates_removed, conflicts,
    )
    return moved
