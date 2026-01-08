"""Export the sample dataset fixtures to JSON and CSV for frontend consumption."""
import json
import csv
from pathlib import Path
from tests.fixtures import sample_dataset as sd

OUT_DIR = Path(sd.__file__).parent


def _dump_json():
    payload = {
        "events": [e.model_dump() for e in sd.EVENTS],
        "people": [p.model_dump() for p in sd.PEOPLE],
        "geographies": [g.model_dump() for g in sd.GEOGRAPHIES],
        "data_sources": [s.model_dump() for s in sd.DATA_SOURCES],
        "dimensions": [d.model_dump() for d in sd.DIMENSIONS],
    }
    out = OUT_DIR / "sample_dataset.json"
    with out.open("w", encoding="utf-8") as fh:
        # Use default=str to serialize datetime and other non-JSON types
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)
    return out


def _dump_csv():
    # Events CSV (id,title,start_date,end_date,confidence,created_by)
    events_csv = OUT_DIR / "events.csv"
    with events_csv.open("w", newline='', encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "title", "start_date", "end_date", "confidence", "created_by"])
        for e in sd.EVENTS:
            sd_start = getattr(e.start_date, "start_date", "")
            sd_end = getattr(e.end_date, "start_date", "") if getattr(e, "end_date", None) else ""
            writer.writerow([e.id, e.title, sd_start, sd_end, getattr(e, "confidence", ""), e.created_by])

    people_csv = OUT_DIR / "people.csv"
    with people_csv.open("w", newline='', encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "name", "birth_date", "death_date", "occupations", "created_by"])
        for p in sd.PEOPLE:
            writer.writerow([p.id, p.name, getattr(p, "birth_date", ""), getattr(p, "death_date", ""), ";".join(p.occupations or []), p.created_by])

    geos_csv = OUT_DIR / "geographies.csv"
    with geos_csv.open("w", newline='', encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "name", "type", "latitude", "longitude", "created_by"])
        for g in sd.GEOGRAPHIES:
            lat = g.center_coordinate.latitude if getattr(g, "center_coordinate", None) else ""
            lon = g.center_coordinate.longitude if getattr(g, "center_coordinate", None) else ""
            writer.writerow([g.id, g.name, g.geography_type.value, lat, lon, g.created_by])

    return events_csv, people_csv, geos_csv


def export_all() -> dict:
    json_path = _dump_json()
    csv_paths = _dump_csv()
    return {"json": str(json_path), "csv": [str(p) for p in csv_paths]}


if __name__ == "__main__":
    print("Exporting sample dataset...")
    paths = export_all()
    print(paths)
