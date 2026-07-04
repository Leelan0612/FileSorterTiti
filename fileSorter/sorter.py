from __future__ import annotations

import logging
import shutil
import filecmp
import time
from send2trash import send2trash
from pathlib import Path


logger = logging.getLogger(__name__)


def sort_files(start_path: Path, dest_path: Path, cutoff_year: int, progress_callback=None) -> int:
    """Move year folders older than cutoff_year from source to destination.

    Structure expected:

        Source/
            Person 1/
                2021/
                2022/
                Random Folder/

        Destination/
            Person 1/
                2021/

    Logic:
    - Create matching person folder in destination if missing.
    - Move the whole year folder if destination does not already have it.
    - If the year folder already exists, move only missing contents.
    - If the same content already exists, skip it.
    - If same file name exists but contents differ, leave both alone and log conflict.
    """

    start_path = Path(start_path)
    dest_path = Path(dest_path)

    if not start_path.is_dir():
        raise ValueError(f"Source is not a valid folder: {start_path}")
    if not dest_path.is_dir():
        raise ValueError(f"Destination is not a valid folder: {dest_path}")

    total = 0

    # Count year folders for progress tracking
    for person_folder in start_path.iterdir():
        if not person_folder.is_dir():
            continue

        for year_folder in person_folder.iterdir():
            if not year_folder.is_dir():
                continue

            try:
                folder_year = int(year_folder.name)
            except ValueError:
                continue

            if folder_year < cutoff_year:
                total += 1

    moved = 0
    done = 0
    duplicates_removed = 0
    conflicts = 0

    logger.info(
        "Run started. Source=%s Destination=%s Cutoff=%s",
        start_path,
        dest_path,
        cutoff_year,
    )
    start_time = time.perf_counter()
    for person_folder in start_path.iterdir():
        if not person_folder.is_dir():
            continue

        target_person_dir = dest_path / person_folder.name
        target_person_dir.mkdir(exist_ok=True)

        for year_folder in person_folder.iterdir():
            if not year_folder.is_dir():
                continue

            try:
                folder_year = int(year_folder.name)
            except ValueError:
                logger.info("Skipped non-year folder: %s", year_folder.name)
                continue

            if folder_year >= cutoff_year:
                continue

            done += 1

            elapsed = time.perf_counter() - start_time
            avg_time = elapsed / done
            remaining = avg_time * (total - done)

            if progress_callback is not None and total > 0:
                progress_callback(done, total, remaining)

            target_year_dir = target_person_dir / year_folder.name

            # Case 1: Destination does not have this year folder yet.
            # Move the entire year folder.
            if not target_year_dir.exists():
                shutil.move(str(year_folder), str(target_person_dir))
                moved += 1
                logger.info("Moved year folder %s -> %s", year_folder, target_person_dir)
                continue

            # Case 2: Destination already has this year folder.
            # Move only missing contents.
            for content in year_folder.iterdir():
                target_content = target_year_dir / content.name

                if target_content.exists():
                    # If both are files, compare them.
                    if content.is_file() and target_content.is_file():
                        same = (
                            content.stat().st_size == target_content.stat().st_size
                            and filecmp.cmp(content, target_content, shallow=False)
                        )

                        if same:
                            try:
                                send2trash(str(content))
                                duplicates_removed += 1
                                logger.info("Duplicate removed from source: %s", content)
                            except OSError as exc:
                                logger.warning("Could not trash duplicate %s: %s", content, exc)
                        else:
                            conflicts += 1
                            logger.warning(
                                "Name conflict left in place because contents differ: %s",
                                content,
                            )

                    # If both are folders, skip to avoid overwriting or merging blindly.
                    elif content.is_dir() and target_content.is_dir():
                        duplicates_removed += 1
                        logger.info("Skipped existing folder: %s", content)

                    else:
                        conflicts += 1
                        logger.warning(
                            "Name conflict left in place because item types differ: %s",
                            content,
                        )

                    continue

                shutil.move(str(content), str(target_year_dir))
                moved += 1
                logger.info("Moved content %s -> %s", content, target_year_dir)

    logger.info(
        "Run complete. Moved %d, duplicates skipped %d, conflicts left %d.",
        moved,
        duplicates_removed,
        conflicts,
    )

    return moved
