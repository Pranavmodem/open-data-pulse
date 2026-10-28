"""World signals: weather and air in the cities that host cloud regions, quakes, hazards and FX."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from pipeline import http
from pipeline.core import Context, Source
from pipeline.markdown import link, text

CATEGORY = "World signals"

# (region, city, latitude, longitude): Dallas plus the cities behind major AWS regions.
REGIONS = [
    ("DFW", "Dallas", 32.78, -96.80),
    ("us-east-1", "Ashburn, VA", 39.04, -77.49),
    ("us-east-2", "Columbus, OH", 39.96, -83.00),
    ("us-west-2", "Boardman, OR", 45.84, -119.70),
    ("sa-east-1", "São Paulo", -23.55, -46.63),
    ("eu-west-1", "Dublin", 53.35, -6.26),
    ("eu-central-1", "Frankfurt", 50.11, 8.68),
    ("ap-south-1", "Mumbai", 19.08, 72.88),
    ("ap-southeast-1", "Singapore", 1.35, 103.82),
    ("ap-northeast-1", "Tokyo", 35.68, 139.69),
]

# WMO weather codes, as used by Open-Meteo.
WEATHER = {0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast", 45: "fog", 48: "fog"}
WEATHER.update({c: "drizzle" for c in (51, 53, 55, 56, 57)})
WEATHER.update({c: "rain" for c in (61, 63, 65, 66, 67, 80, 81, 82)})
WEATHER.update({c: "snow" for c in (71, 73, 75, 77, 85, 86)})
WEATHER.update({c: "thunderstorms" for c in (95, 96, 99)})


def _coordinates() -> dict:
    return {"latitude": ",".join(str(r[2]) for r in REGIONS), "longitude": ",".join(str(r[3]) for r in REGIONS)}


class CloudRegionWeather(Source):
    name = "cloud_region_weather"
    title = "Weather in cloud-region cities"
    category = CATEGORY
    description = "Today's forecast for Dallas and the cities behind nine major AWS regions."
    homepage = "https://open-meteo.com/"

    def fetch(self, ctx: Context) -> list[dict]:
        forecasts = http.get_json("https://api.open-meteo.com/v1/forecast", {
            **_coordinates(),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weather_code",
            "timezone": "auto", "forecast_days": 1,
        })
        rows = []
        for (region, city, _, _), f in zip(REGIONS, forecasts):
            daily = {k: v[0] for k, v in f["daily"].items()}
            rows.append({
                "region": region,
                "city": city,
                "date": daily["time"],
                "temp_max_c": daily["temperature_2m_max"],
                "temp_min_c": daily["temperature_2m_min"],
                "precipitation_mm": daily["precipitation_sum"],
                "wind_max_kmh": daily["wind_speed_10m_max"],
                "conditions": WEATHER.get(daily["weather_code"], f"code {daily['weather_code']}"),
            })
        return rows

    def highlight(self, rows):
        home = rows[0]
        hottest = max(rows, key=lambda r: r["temp_max_c"])
        coldest = min(rows, key=lambda r: r["temp_min_c"])
        return (f"Dallas {home['temp_max_c']:.0f}°C / {home['temp_min_c']:.0f}°C, {home['conditions']}. "
                f"Hottest: {hottest['city']} ({hottest['region']}) {hottest['temp_max_c']:.0f}°C. "
                f"Coldest: {coldest['city']} ({coldest['region']}) {coldest['temp_min_c']:.0f}°C")


class AirQuality(Source):
    name = "air_quality"
    title = "Air quality in cloud-region cities"
    category = CATEGORY
    description = "Current US AQI, PM2.5, PM10 and ozone for the same cities."
    homepage = "https://open-meteo.com/en/docs/air-quality-api"

    def fetch(self, ctx: Context) -> list[dict]:
        readings = http.get_json("https://air-quality-api.open-meteo.com/v1/air-quality",
                                 {**_coordinates(), "current": "us_aqi,pm2_5,pm10,ozone"})
        return [{
            "region": region,
            "city": city,
            "us_aqi": r["current"].get("us_aqi"),
            "pm2_5": r["current"].get("pm2_5"),
            "pm10": r["current"].get("pm10"),
            "ozone": r["current"].get("ozone"),
            "measured_at": r["current"].get("time"),
        } for (region, city, _, _), r in zip(REGIONS, readings)]

    def highlight(self, rows):
        rated = [r for r in rows if r["us_aqi"] is not None]
        worst, best = max(rated, key=lambda r: r["us_aqi"]), min(rated, key=lambda r: r["us_aqi"])
        return f"Worst air: {worst['city']} (AQI {text(worst['us_aqi'], 20)}). Cleanest: {best['city']} (AQI {text(best['us_aqi'], 20)})"


class Earthquakes(Source):
    name = "earthquakes"
    title = "Earthquakes"
    category = CATEGORY
    description = "Every magnitude 2.5+ earthquake in the past 24 hours, from the USGS feed."
    homepage = "https://earthquake.usgs.gov/earthquakes/feed/"

    def fetch(self, ctx: Context) -> list[dict]:
        feed = http.get_json("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
        rows = []
        for q in feed["features"]:
            p, (lon, lat, depth) = q["properties"], q["geometry"]["coordinates"]
            rows.append({
                "quake_id": q["id"],
                "magnitude": p.get("mag"),
                "place": p.get("place"),
                "time": datetime.fromtimestamp(p["time"] / 1000, timezone.utc).isoformat(timespec="seconds"),
                "depth_km": depth,
                "latitude": lat,
                "longitude": lon,
                "tsunami": bool(p.get("tsunami")),
                "alert": p.get("alert"),
                "url": p.get("url"),
            })
        return sorted(rows, key=lambda r: r["magnitude"] or 0, reverse=True)

    def highlight(self, rows):
        top = rows[0]
        label = f"M{top['magnitude']} {top['place']}"
        return f"{len(rows)} quakes of M2.5+ in 24h. Largest: {link(label, top['url'])}"


class NaturalEvents(Source):
    name = "natural_events"
    title = "Natural hazards"
    category = CATEGORY
    description = "Open wildfires, storms, volcanoes and other events NASA EONET tracked this week."
    homepage = "https://eonet.gsfc.nasa.gov/"

    def fetch(self, ctx: Context) -> list[dict]:
        events = http.get_json("https://eonet.gsfc.nasa.gov/api/v3/events", {"status": "open", "days": 7})["events"]
        rows = []
        for e in events:
            latest = (e.get("geometry") or [{}])[-1]
            coordinates = latest.get("coordinates") if latest.get("type") == "Point" else None
            rows.append({
                "event_id": e["id"],
                "title": e["title"],
                "category": e["categories"][0]["title"] if e.get("categories") else None,
                "last_seen": latest.get("date"),
                "longitude": coordinates[0] if coordinates else None,
                "latitude": coordinates[1] if coordinates else None,
                "magnitude": latest.get("magnitudeValue"),
                "magnitude_unit": latest.get("magnitudeUnit"),
                "url": e.get("link"),
            })
        return rows

    def highlight(self, rows):
        counts = Counter(r["category"] or "Other" for r in rows).most_common()
        return f"{len(rows)} open events: " + ", ".join(f"{n} {text(c.lower(), 30)}" for c, n in counts)


class FxRates(Source):
    name = "fx_rates"
    title = "Exchange rates"
    category = CATEGORY
    description = "European Central Bank reference rates against the US dollar."
    homepage = "https://frankfurter.dev/"

    def fetch(self, ctx: Context) -> list[dict]:
        latest = http.get_json("https://api.frankfurter.app/latest", {"from": "USD"})
        return [{"base": latest["base"], "currency": currency, "rate": rate, "date": latest["date"]}
                for currency, rate in sorted(latest["rates"].items())]

    def highlight(self, rows):
        rates = {r["currency"]: r["rate"] for r in rows}
        shown = ", ".join(f"{rates[c]:.4g} {c}" for c in ("EUR", "GBP", "INR", "JPY", "MXN") if c in rates)
        return f"1 USD = {shown} (ECB, {text(rows[0]['date'], 20)})"


SOURCES = [CloudRegionWeather(), AirQuality(), Earthquakes(), NaturalEvents(), FxRates()]
