import os
import sys
import zipfile
import json
import subprocess
from datetime import datetime

EXIFTOOL = r"/usr/bin/exiftool"

OUTPUT_WITH_DATE = "exportedwithDate"
OUTPUT_MISSING = "missingDates"

SUPPORTED_MEDIA = (".jpg", ".jpeg", ".png", ".heic", ".mp4", ".mov")


# --- TIMESTAMP HELPERS ---
def get_timestamp_from_json(j):
    ts = None

    try:
        ts_str = j.get("photoTakenTime", {}).get("timestamp")
        if ts_str:
            ts = int(ts_str)
    except Exception:
        pass

    if ts is None:
        try:
            ts_str = j.get("creationTime", {}).get("timestamp")
            if ts_str:
                ts = int(ts_str)
        except Exception:
            pass

    if ts is None or ts <= 0:
        return None, None

    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%Y:%m:%d %H:%M:%S"), dt.strftime("%Y")


def get_gps_from_json(j):
    lat = None
    lon = None

    for key in ("geoData", "geoDataExif"):
        try:
            g = j.get(key, {})
            if "latitude" in g and "longitude" in g:
                lat = g["latitude"]
                lon = g["longitude"]
                break
        except Exception:
            continue

    return lat, lon


def write_metadata(file_path, exif_timestamp, lat, lon):
    cmd = [
        EXIFTOOL,
        f"-DateTimeOriginal={exif_timestamp}",
        f"-CreateDate={exif_timestamp}",
        f"-ModifyDate={exif_timestamp}",
        "-overwrite_original"
    ]

    if lat is not None and lon is not None:
        cmd.append(f"-GPSLatitude={lat}")
        cmd.append(f"-GPSLongitude={lon}")
        cmd.append("-GPSLatitudeRef=N" if lat >= 0 else "-GPSLatitudeRef=S")
        cmd.append("-GPSLongitudeRef=E" if lon >= 0 else "-GPSLongitudeRef=W")

    cmd.append(file_path)
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# --- PROCESS ONE ZIP ---
def process_zip(zip_path, metadata_map):
    print(f"\n📦 Processing ZIP: {zip_path}")

    os.makedirs(OUTPUT_WITH_DATE, exist_ok=True)
    os.makedirs(OUTPUT_MISSING, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        media_files = [f for f in z.namelist() if f.lower().endswith(SUPPORTED_MEDIA)]
        print(f"Found {len(media_files)} media files")

        for f in media_files:
            filename = os.path.basename(f)

            j = metadata_map.get(filename)
            exif_ts = None
            year = None
            lat = None
            lon = None

            if j:
                exif_ts, year = get_timestamp_from_json(j)
                lat, lon = get_gps_from_json(j)

            if exif_ts and year:
                out_dir = os.path.join(OUTPUT_WITH_DATE, year)
            else:
                out_dir = OUTPUT_MISSING

            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, filename)

            # --- SKIP IF FILE EXISTS ---
            if os.path.exists(out_path):
                print(f"⏭ SKIPPED (already exists): {filename}")
                continue

            # Write media file
            with open(out_path, "wb") as out:
                out.write(z.read(f))

            if exif_ts:
                print(f"✔ {filename} → {exif_ts}")
                write_metadata(out_path, exif_ts, lat, lon)
            else:
                print(f"✖ {filename} → No timestamp")


def main():
    if len(sys.argv) < 2:
        print("Usage: python process_single_zip.py <zipfile>")
        return

    zip_path = sys.argv[1]

    if not os.path.exists(zip_path):
        print(f"ZIP not found: {zip_path}")
        return

    # Load global metadata
    with open("global_metadata.json", "r", encoding="utf-8") as f:
        metadata_map = json.load(f)

    process_zip(zip_path, metadata_map)


if __name__ == "__main__":
    main()

