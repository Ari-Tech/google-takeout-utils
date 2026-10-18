from pathlib import Path
import zipfile


def validate_takeout_zips(directory_path: str):
    folder = Path(directory_path)
    zip_files = sorted(folder.glob("*.zip"))

    if not zip_files:
        print(f"No .zip files found in directory: {folder.resolve()}")
        return

    print(
        f"Scanning and verifying {len(zip_files)} .zip archive(s) in '{folder.resolve()}'...\n"
    )

    valid_zips = []
    corrupted_zips = []

    for zip_path in zip_files:
        file_size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(
            f"Testing: {zip_path.name:<40} ({file_size_mb:.1f} MB)... ",
            end="",
            flush=True,
        )

        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                # testzip() reads CRC checksums for every item in the archive.
                # Returns the name of the first corrupted file, or None if completely valid.
                bad_file = z.testzip()

                if bad_file is None:
                    print(" OK")
                    valid_zips.append(zip_path.name)
                else:
                    print(f"FAILED (Corrupted inner file: '{bad_file}')")
                    corrupted_zips.append((zip_path.name, f"Bad CRC/data in '{bad_file}'"))

        except zipfile.BadZipFile:
            print("FAILED (Invalid ZIP header / corrupt archive)")
            corrupted_zips.append(
                (zip_path.name, "Invalid header - file is truncated or not a ZIP")
            )
        except Exception as e:
            print(f"FAILED ({e})")
            corrupted_zips.append((zip_path.name, str(e)))

    print("\n" + "=" * 65)
    print("VALIDATION SUMMARY")
    print("=" * 65)
    print(f"Total Archives Checked : {len(zip_files)}")
    print(f"Valid Archives        : {len(valid_zips)}")
    print(f"Corrupted Archives    : {len(corrupted_zips)}")

    if corrupted_zips:
        print("\n" + "!" * 65)
        print("THE FOLLOWING ZIP FILES ARE INVALID / CORRUPT:")
        print("!" * 65)
        for name, reason in corrupted_zips:
            print(f" - {name}\n   Reason: {reason}")
        print(
            "\nTip: Re-download the corrupted zip files from Google Takeout before running immich-go."
        )
    else:
        print("\nAll ZIP archives are healthy and valid!")


if __name__ == "__main__":
    target_dir = input(
        "Enter path to Takeout ZIPs directory [press Enter for current folder]: "
    ).strip()
    if not target_dir:
        target_dir = "."

    validate_takeout_zips(target_dir)
