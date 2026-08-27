# OpenStreetMap matching

## Candidate discovery

Prefer the least expensive method:

1. Fetch a known OSM object directly when an object type and ID are available.
2. For a location search, use a tightly bounded Overpass query around the OBDB coordinates or locality and relevant tags such as `craft=brewery`, `industrial=brewery`, `amenity=bar`, `microbrewery=yes`, `name`, or `website`.
3. Use the public Nominatim service only for occasional, user-triggered geocoding/search. It is not a bulk discovery API.

For public Nominatim, follow its current usage policy, including a valid identifying `User-Agent` or `Referer`, caching, attribution, and an absolute maximum of one request per second. Do not send systematic queries, autocomplete requests, or parallel traffic.

For public Overpass instances, make bounded, modest queries with explicit timeouts; avoid world/large-area scans and repeated identical requests. Check endpoint status, serialize requests, cache results, and back off on overload or throttling. Do not endpoint-hop to evade limits. Use a self-hosted or appropriately provisioned service for bulk analysis.

## Match the place, not just the name

Compare:

- `name`, `alt_name`, `short_name`, and `old_name`
- `addr:*` components, locality, postcode, and country
- `website`/`contact:website` host
- Geometry or representative coordinates
- Brewery-related tags and operational status

OSM commonly has separate objects for a brewery campus, building, taproom, shop, and entrance. A node inside a matching polygon may be a distinct feature, not a duplicate. Report stable references as `<node|way|relation>/<id>` and include the canonical `openstreetmap.org` URL. Do not record a bare numeric ID.

When coordinates differ, account for point-versus-polygon centroids and entrances, but flag different premises or branches as a conflict. Distinguish duplicate OSM objects from legitimate related features; do not recommend deletion or merging without OSM community review.

## Attribution and license

Reports using OSM data must include `© OpenStreetMap contributors` and link to `https://www.openstreetmap.org/copyright`. OSM data is available under ODbL; preserve source links and retrieval dates. Nominatim and Overpass may impose additional operational policies. This workflow reads OSM only and never edits objects or tags.
