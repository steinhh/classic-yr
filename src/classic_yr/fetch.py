"""Fetch weather forecast from Yr/MET Norway API and store as CSV."""

from __future__ import annotations

import csv
import json
import logging
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, cast

import requests  # type: ignore[import-untyped]

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Oslo, Norway
LOCATION_NAME = "oslo"
LAT = 59.9139
LON = 10.7522
ALTITUDE = 23  # metres above sea level

API_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

# Identifies this application per Yr Terms of Service: must include app name and contact info.
USER_AGENT = "classic-yr/0.1.0 https://github.com/steinhh/classic-yr"

CSV_FIELDS = [
    "time",
    "air_temperature",
    "precipitation_1h",
    "wind_speed",
    "wind_from_direction",
    "symbol_code",
]


def _data_dir() -> Path:
    """Return the data directory (relative to CWD)."""
    return Path.cwd() / "data"


def _find_cached_response(
    responses_dir: Path, location: str
) -> tuple[Path | None, dict[str, str] | None]:
    """Find the most recent cached response for a location.

    Args:
        responses_dir: Directory containing cached responses.
        location: Location name (e.g., "oslo").

    Returns:
        Tuple of (response_file, metadata) or (None, None) if no cache exists.
    """
    meta_files = sorted(responses_dir.glob(f"*_{location}.meta.json"), reverse=True)
    if not meta_files:
        return None, None

    latest_meta = meta_files[0]
    metadata: dict[str, str] = json.loads(latest_meta.read_text(encoding="utf-8"))
    response_file = latest_meta.with_name(latest_meta.name.replace(".meta.json", ".json"))

    if not response_file.exists():
        return None, None

    return response_file, metadata


def _is_cache_fresh(metadata: dict[str, str]) -> bool:
    """Check if a cached response is still fresh based on the Expires header.

    Args:
        metadata: Cache metadata containing an ``expires`` field.

    Returns:
        True if the cache has not yet expired.
    """
    expires_str = metadata.get("expires", "")
    if not expires_str:
        return False
    try:
        expires = parsedate_to_datetime(expires_str)
        return datetime.now(timezone.utc) < expires
    except Exception:
        return False


def fetch_forecast(
    location: str = LOCATION_NAME,
    lat: float = LAT,
    lon: float = LON,
    altitude: int = ALTITUDE,
) -> dict[str, Any]:
    """Fetch weather forecast from the Yr API, using cache when valid.

    Respects the Yr Terms of Service:
    - Sets a descriptive User-Agent header.
    - Checks the Expires header before making a new request.
    - Sends If-Modified-Since on stale-cache requests.
    - Handles 304 Not Modified by reusing cached data.

    Args:
        location: Location name used for response file naming.
        lat: Latitude of the location.
        lon: Longitude of the location.

    Returns:
        Parsed JSON forecast data from the API.

    Raises:
        requests.HTTPError: If the server returns an error status.
        requests.RequestException: On network or connection failure.
    """
    responses_dir = _data_dir() / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)

    cached_file, metadata = _find_cached_response(responses_dir, location)

    headers: dict[str, str] = {"User-Agent": USER_AGENT}

    if cached_file is not None and metadata is not None:
        if _is_cache_fresh(metadata):
            logger.info("Cache is fresh; using %s", cached_file.name)
            return json.loads(cached_file.read_text(encoding="utf-8"))  # type: ignore[no-any-return]

        last_modified = metadata.get("last_modified", "")
        if last_modified:
            headers["If-Modified-Since"] = last_modified

    logger.info("Fetching from %s", API_URL)
    response = requests.get(
        API_URL,
        params={"lat": lat, "lon": lon, "altitude": altitude},
        headers=headers,
        timeout=30,
    )

    if response.status_code == 304:
        logger.info("304 Not Modified; reusing cached data")
        if cached_file is None:
            raise RuntimeError("Received 304 but no cached response file found.")
        # Persist updated Expires so we respect the new freshness window.
        if metadata is not None:
            new_meta = dict(metadata)
            new_expires = response.headers.get("Expires", "")
            if new_expires:
                new_meta["expires"] = new_expires
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            (responses_dir / f"{timestamp}_{location}.meta.json").write_text(
                json.dumps(new_meta, indent=2), encoding="utf-8"
            )
        return cast("dict[str, Any]", json.loads(cached_file.read_text(encoding="utf-8")))

    response.raise_for_status()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    response_path = responses_dir / f"{timestamp}_{location}.json"
    response_path.write_text(response.text, encoding="utf-8")
    logger.info("Saved response to %s", response_path.name)

    meta: dict[str, str] = {
        "expires": response.headers.get("Expires", ""),
        "last_modified": response.headers.get("Last-Modified", ""),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    (responses_dir / f"{timestamp}_{location}.meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )

    result: dict[str, Any] = response.json()
    return result


def parse_timeseries(data: dict[str, Any]) -> list[dict[str, str]]:
    """Extract hourly rows from a forecast API response.

    Only entries that include ``next_1_hours`` data are included, which
    ensures true 1-hour resolution rows.

    Args:
        data: Parsed JSON response from the Yr compact API.

    Returns:
        List of row dicts keyed by CSV_FIELDS.
    """
    rows: list[dict[str, str]] = []
    timeseries: list[dict[str, Any]] = data.get("properties", {}).get("timeseries", [])

    for entry in timeseries:
        time: str = entry.get("time", "")
        instant: dict[str, Any] = entry.get("data", {}).get("instant", {}).get("details", {})
        next_1h: dict[str, Any] = entry.get("data", {}).get("next_1_hours", {})

        if not next_1h:
            continue

        rows.append(
            {
                "time": time,
                "air_temperature": str(instant.get("air_temperature", "")),
                "precipitation_1h": str(next_1h.get("details", {}).get("precipitation_amount", "")),
                "wind_speed": str(instant.get("wind_speed", "")),
                "wind_from_direction": str(instant.get("wind_from_direction", "")),
                "symbol_code": next_1h.get("summary", {}).get("symbol_code", ""),
            }
        )

    return rows


def update_csv(new_rows: list[dict[str, str]], csv_path: Path) -> int:
    """Append rows to the CSV file that are not already present.

    Deduplication is based on the ``time`` field.  Existing rows are never
    modified.

    Args:
        new_rows: Forecast rows to potentially add.
        csv_path: Path to the target CSV file.

    Returns:
        Number of rows actually written.
    """
    existing_times: set[str] = set()

    if csv_path.exists() and csv_path.stat().st_size > 0:
        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_times.add(row["time"])

    to_add = [r for r in new_rows if r["time"] not in existing_times]

    if not to_add:
        logger.info("No new rows to add.")
        return 0

    write_header = not csv_path.exists() or csv_path.stat().st_size == 0
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        for row in to_add:
            writer.writerow(row)

    logger.info("Added %d new row(s) to %s", len(to_add), csv_path.name)
    return len(to_add)


def main() -> None:
    """Fetch Yr weather forecast for Oslo and update data/yr.csv."""
    csv_path = _data_dir() / "yr.csv"

    try:
        data = fetch_forecast()
    except requests.HTTPError as exc:
        logger.error("HTTP error: %s", exc)
        sys.exit(1)
    except requests.RequestException as exc:
        logger.error("Request error: %s", exc)
        sys.exit(1)

    rows = parse_timeseries(data)
    added = update_csv(rows, csv_path)
    logger.info("Done. %d row(s) added.", added)


if __name__ == "__main__":
    main()
