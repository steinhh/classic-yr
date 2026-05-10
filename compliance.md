# Yr API Compliance

This document describes how `classic-yr` complies with the
[Yr Terms of Service](https://developer.yr.no/doc/TermsOfService/).

## User-Agent identification

Every HTTP request includes a `User-Agent` header that identifies the
application and provides a contact URL, as required:

```
User-Agent: classic-yr/0.1.0 https://github.com/steinhh/classic-yr
```

## Caching and request limits

The script is designed never to fetch data more often than the server allows:

1. **Expires header** ? The `Expires` value from each response is stored in a
   companion `.meta.json` file alongside the raw response in `data/responses/`.
2. **Cache check before request** ? On every run the script checks whether the
   cached data is still fresh (`now < Expires`).  If so, no network request is
   made.
3. **If-Modified-Since** ? When the cache has expired, the request includes the
   `If-Modified-Since` header set to the cached `Last-Modified` value.
4. **304 Not Modified** ? A 304 response causes the cached JSON to be reused
   and the new `Expires` value (if provided) is persisted so the freshness
   window is extended correctly.

## Response storage

Raw API responses are stored in `data/responses/` with filenames of the form
`YYYYMMDDTHHMMSSZ_<location>.json` (UTC timestamp), together with a
`*.meta.json` file that records `expires`, `last_modified`, and `fetched_at`.

## CSV idempotency

When `data/yr.csv` is updated, rows are deduplicated by the `time` column.
Re-running the script never duplicates data.

## Attribution

Data is provided by the
[Norwegian Meteorological Institute (MET Norway)](https://www.met.no/) via the
[Yr weather service](https://www.yr.no/).
