import os
import zipfile
import json

OUTPUT_METADATA = "global_metadata.json"

def build_global_metadata(zip_files):
    metadata_map = {}

    for zip_path in zip_files:
        print(f"📦 Reading JSON from: {zip_path}")
        with zipfile.ZipFile(zip_path, "r") as z:
            for name in z.namelist():
                if not name.lower().endswith(".json"):
                    continue

                try:
                    raw = z.read(name).decode("utf-8")
                    j = json.loads(raw)
                except Exception:
                    continue

                # Prefer 'title' field
                title = j.get("title")
                if title:
                    key = os.path.basename(title)
                else:
                    base = os.path.basename(name)
                    if base.endswith(".supplemental-metadata.json"):
                        key = base.replace(".supplemental-metadata.json", "")
                    else:
                        key = base.replace(".json", "")

                metadata_map[key] = j

    print(f"Total metadata entries: {len(metadata_map)}")

    with open(OUTPUT_METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata_map, f, indent=2)

    print(f"🎉 Saved metadata to {OUTPUT_METADATA}")


def main():
    zip_files = [f for f in os.listdir(".") if f.lower().endswith(".zip")]
    zip_files.sort()

    if not zip_files:
        print("No ZIP files found.")
        return

    build_global_metadata(zip_files)


if __name__ == "__main__":
    main()

