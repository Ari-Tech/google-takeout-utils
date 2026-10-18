from pathlib import Path
import zipfile

# Recognized media extensions
PHOTO_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".heic",
    ".heif",
    ".tiff",
    ".tif",
    ".dng",
    ".cr2",
    ".nef",
    ".arw",
    ".raw",
    ".svg",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".avi",
    ".wmv",
    ".flv",
    ".3gp",
    ".webm",
    ".mpg",
    ".mpeg",
    ".mts",
    ".m2ts",
    ".mod",
}


def count_takeout_media(directory_path: str):
    folder = Path(directory_path)
    zip_files = sorted(folder.glob("*.zip"))

    if not zip_files:
        print(f"No .zip files found in directory: {folder.resolve()}")
        return

    total_photos = 0
    total_videos = 0
    processed_zips = 0

    print(
        f"Found {len(zip_files)} .zip archive(s) in '{folder.resolve()}'. Processing...\n"
    )

    for zip_path in zip_files:
        photos_in_zip = 0
        videos_in_zip = 0

        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                for file_info in z.infolist():
                    # Skip folders
                    if file_info.is_dir():
                        continue

                    ext = Path(file_info.filename).suffix.lower()

                    if ext in PHOTO_EXTENSIONS:
                        photos_in_zip += 1
                    elif ext in VIDEO_EXTENSIONS:
                        videos_in_zip += 1

            total_photos += photos_in_zip
            total_videos += videos_in_zip
            processed_zips += 1

            print(
                f"{zip_path.name:<40} -> Photos: {photos_in_zip:6,} | Videos: {videos_in_zip:6,}"
            )

        except zipfile.BadZipFile:
            print(f"ERROR: '{zip_path.name}' is corrupted or incomplete.")
        except Exception as e:
            print(f"ERROR reading '{zip_path.name}': {e}")

    print("\n" + "=" * 65)
    print("SUMMARY COUNT")
    print("=" * 65)
    print(f"ZIP Archives Processed : {processed_zips}")
    print(f"Total Photos Found     : {total_photos:,}")
    print(f"Total Videos Found     : {total_videos:,}")
    print(f"Total Combined Media   : {total_photos + total_videos:,}")
    print("=" * 65)


if __name__ == "__main__":
    target_dir = input(
        "Enter path to Takeout ZIPs directory [press Enter for current folder]: "
    ).strip()
    if not target_dir:
        target_dir = "."

    count_takeout_media(target_dir)
