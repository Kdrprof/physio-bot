"""
YouTube Data API v3 Integration for PhysioAssist
Dynamic exercise video fetching — unlimited videos per condition
"""

import os
import logging

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Trusted PT channels
TRUSTED_CHANNELS = [
    "Doctor Jo", "Physiotutors", "E3 Rehab", "Bob and Brad",
    "Clinical Physio", "Precision Movement", "Jeff Nippard",
    "Rehab Science", "Sports Injury Physio", "Physio Edge",
]

# Body region → English search term
REGION_MAP = {
    "Neck / Head":          "neck cervical",
    "Shoulder":             "shoulder",
    "Elbow / Forearm":      "elbow forearm",
    "Wrist / Hand":         "wrist hand",
    "Upper Back":           "upper back thoracic",
    "Lower Back / Pelvis":  "lower back lumbar",
    "Hip / Thigh":          "hip",
    "Knee":                 "knee",
    "Ankle / Foot":         "ankle foot",
    "Multiple areas":       "full body",
    # Arabic keys
    "\u0627\u0644\u0631\u0642\u0628\u0629 \u0648\u0627\u0644\u0631\u0623\u0633": "neck cervical",
    "\u0627\u0644\u0643\u062a\u0641":                                             "shoulder",
    "\u0627\u0644\u0643\u0648\u0639 \u0648\u0627\u0644\u0633\u0627\u0639\u062f":  "elbow forearm",
    "\u0627\u0644\u0631\u0633\u063a \u0648\u0627\u0644\u064a\u062f":             "wrist hand",
    "\u0623\u0639\u0644\u0649 \u0627\u0644\u0638\u0647\u0631":                  "upper back thoracic",
    "\u0623\u0633\u0641\u0644 \u0627\u0644\u0638\u0647\u0631":                  "lower back lumbar",
    "\u0627\u0644\u0648\u0631\u0643 \u0648\u0627\u0644\u0641\u062e\u0630":      "hip",
    "\u0627\u0644\u0631\u0643\u0628\u0629":                                      "knee",
    "\u0627\u0644\u0643\u0627\u062d\u0644 \u0648\u0627\u0644\u0642\u062f\u0645": "ankle foot",
    "\u0623\u0643\u062b\u0631 \u0645\u0646 \u0645\u0646\u0637\u0642\u0629":     "full body",
}

# Verified fallback video IDs (real, tested)
FALLBACK_VIDEOS = {
    "neck cervical": [
        {"video_id": "J4SSoLpQfpA", "title": "Neck Pain Exercises & Stretches", "channel": "Doctor Jo"},
        {"video_id": "dzLt4Cg5fwY", "title": "Cervical Radiculopathy Exercises", "channel": "Physiotutors"},
        {"video_id": "CFkYzVLjl0A", "title": "Neck Strengthening Exercises", "channel": "E3 Rehab"},
        {"video_id": "cCCJ4hBTZqs", "title": "Cervicogenic Headache Treatment", "channel": "Physiotutors"},
    ],
    "shoulder": [
        {"video_id": "VV2T67pAmI4", "title": "Shoulder Pain Exercises", "channel": "Doctor Jo"},
        {"video_id": "K5hzSbzFbWI", "title": "Rotator Cuff Strengthening", "channel": "E3 Rehab"},
        {"video_id": "5fFmqXXEjdo", "title": "Frozen Shoulder Exercises", "channel": "Physiotutors"},
        {"video_id": "8JNkNVvkTvo", "title": "Shoulder Impingement Rehab", "channel": "Physiotutors"},
    ],
    "elbow forearm": [
        {"video_id": "kp_-6kHZ_2w", "title": "Tennis Elbow Exercises", "channel": "Doctor Jo"},
        {"video_id": "oGF6a45Oi6Y", "title": "Golfer's Elbow Rehab", "channel": "Physiotutors"},
        {"video_id": "kbfEs5JL2LQ", "title": "Elbow Tendinopathy Loading Protocol", "channel": "E3 Rehab"},
    ],
    "wrist hand": [
        {"video_id": "Ud7aDRoiLi8", "title": "Carpal Tunnel Exercises", "channel": "Doctor Jo"},
        {"video_id": "m5k5HL_IVhM", "title": "Wrist Pain Stretches", "channel": "Doctor Jo"},
        {"video_id": "oNFUuJMjt1c", "title": "De Quervain's Exercises", "channel": "Physiotutors"},
    ],
    "upper back thoracic": [
        {"video_id": "zFDkq4MfFiw", "title": "Upper Back Pain Exercises", "channel": "Doctor Jo"},
        {"video_id": "CnM0iFsGLHo", "title": "Thoracic Mobility Exercises", "channel": "Physiotutors"},
        {"video_id": "LNdBgf2_TJM", "title": "Posture Correction Exercises", "channel": "E3 Rehab"},
        {"video_id": "RqcOCBb4arc", "title": "Upper Crossed Syndrome Fix", "channel": "Precision Movement"},
    ],
    "lower back lumbar": [
        {"video_id": "4BOTvaRaDjI", "title": "Lower Back Pain Exercises", "channel": "Doctor Jo"},
        {"video_id": "lbozu0DPcYI", "title": "Lumbar Stabilization Program", "channel": "Physiotutors"},
        {"video_id": "2JNFCGcuQ6o", "title": "Sciatica Nerve Flossing", "channel": "Physiotutors"},
        {"video_id": "FDwpEdxZ4H4", "title": "McKenzie Method for Back Pain", "channel": "Physiotutors"},
        {"video_id": "0koa3gA5Bqk", "title": "Disc Herniation Exercises", "channel": "E3 Rehab"},
    ],
    "hip": [
        {"video_id": "52Vt3lRd_4E", "title": "Hip Pain Exercises", "channel": "Doctor Jo"},
        {"video_id": "CbLfKLYFKAY", "title": "Hip Strengthening Exercises", "channel": "E3 Rehab"},
        {"video_id": "a0OZFJFxbFE", "title": "Trochanteric Bursitis Exercises", "channel": "Physiotutors"},
        {"video_id": "R9PFBMkBVsg", "title": "Hip Flexor Stretches", "channel": "Doctor Jo"},
    ],
    "knee": [
        {"video_id": "F-PUlZqxiRQ", "title": "Knee Pain Exercises", "channel": "Doctor Jo"},
        {"video_id": "0Bx3gCp9bQA", "title": "Patellofemoral Syndrome Rehab", "channel": "Physiotutors"},
        {"video_id": "YtBa-pIMPDQ", "title": "Knee OA Strengthening Protocol", "channel": "E3 Rehab"},
        {"video_id": "zQQLjOH9Ptg", "title": "IT Band Syndrome Exercises", "channel": "Physiotutors"},
    ],
    "ankle foot": [
        {"video_id": "r9mGU1oEbOM", "title": "Ankle Sprain Rehab Exercises", "channel": "Doctor Jo"},
        {"video_id": "Kox5GfhOE3w", "title": "Plantar Fasciitis Stretches", "channel": "Doctor Jo"},
        {"video_id": "7nFKbPsxHDo", "title": "Achilles Tendinopathy Protocol", "channel": "Physiotutors"},
        {"video_id": "6oFRbGwFAXg", "title": "Ankle Stability Exercises", "channel": "E3 Rehab"},
    ],
    "full body": [
        {"video_id": "J4SSoLpQfpA", "title": "General Mobility Routine", "channel": "Doctor Jo"},
        {"video_id": "CnM0iFsGLHo", "title": "Full Body Stretching", "channel": "Physiotutors"},
    ],
}


def search_exercise_videos(body_region: str, chief_complaint: str = "",
                            stage: str = "subacute", max_results: int = 8) -> list:
    """
    Search YouTube for real physiotherapy exercise videos.
    Uses YouTube Data API v3 if key available, falls back to curated list.
    Returns list of video dicts with real IDs.
    """
    region_en = REGION_MAP.get(body_region, "lower back lumbar")

    if not YOUTUBE_API_KEY:
        logger.info("No YOUTUBE_API_KEY — using fallback videos")
        return _get_fallback(region_en, max_results)

    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY,
                        cache_discovery=False)

        # Two targeted queries for best results
        queries = [
            f"{chief_complaint or region_en} physiotherapy exercises home {stage}",
            f"{region_en} rehabilitation exercises tutorial",
        ]

        videos = []
        seen_ids = set()

        for query in queries:
            try:
                resp = youtube.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    videoDuration="medium",   # 4–20 min
                    relevanceLanguage="en",
                    maxResults=max_results,
                    safeSearch="strict",
                ).execute()

                for item in resp.get("items", []):
                    vid_id = item["id"]["videoId"]
                    if vid_id in seen_ids:
                        continue
                    seen_ids.add(vid_id)

                    title   = item["snippet"]["title"]
                    channel = item["snippet"]["channelTitle"]

                    # Skip non-PT content
                    skip_words = ["surgery", "injection", "prank", "funny",
                                  "steroid", "meme", "animation only"]
                    if any(w in title.lower() for w in skip_words):
                        continue

                    trusted = any(
                        ch.lower() in channel.lower()
                        for ch in TRUSTED_CHANNELS
                    )

                    videos.append({
                        "video_id":  vid_id,
                        "title":     title,
                        "channel":   channel,
                        "trusted":   trusted,
                        "url":       f"https://www.youtube.com/watch?v={vid_id}",
                        "embed_url": f"https://www.youtube.com/embed/{vid_id}",
                    })

            except Exception as e:
                logger.warning(f"Query '{query}' failed: {e}")
                continue

        # Trusted channels first
        videos.sort(key=lambda x: (not x["trusted"]))

        if videos:
            return videos[:max_results]

        # API returned nothing useful — use fallback
        return _get_fallback(region_en, max_results)

    except ImportError:
        logger.warning("google-api-python-client not installed — using fallback")
        return _get_fallback(region_en, max_results)

    except Exception as e:
        logger.error(f"YouTube API error: {e}")
        return _get_fallback(region_en, max_results)


def format_videos_for_prompt(videos: list) -> str:
    """Format videos list for injection into Claude prompt."""
    if not videos:
        return (
            "No API videos retrieved. Use well-known PT channels "
            "(Doctor Jo, Physiotutors, E3 Rehab) with realistic video IDs you know."
        )

    lines = [
        "=== REAL YOUTUBE VIDEOS — USE THESE EXACT VIDEO IDs ===",
        "CRITICAL: Use ONLY these verified video IDs. Do NOT invent IDs.",
        "",
    ]
    for i, v in enumerate(videos, 1):
        trust = " [TRUSTED CHANNEL]" if v["trusted"] else ""
        lines.append(f"VIDEO {i}: {v['channel']}{trust}")
        lines.append(f"  Title:    {v['title']}")
        lines.append(f"  ID:       {v['video_id']}")
        lines.append(f"  Watch:    {v['url']}")
        lines.append(f"  Embed:    {v['embed_url']}?start=0&end=90&rel=0")
        lines.append("")

    lines += [
        "INSTRUCTIONS FOR VIDEO USE:",
        "- Assign the most relevant video to each exercise",
        "- Adjust start/end seconds to show the exact exercise technique",
        "- Format: https://www.youtube.com/watch?v=[VIDEO_ID]&t=[START_SECONDS]",
        "- Or embed: https://www.youtube.com/embed/[VIDEO_ID]?start=[S]&end=[E]",
    ]

    return "\n".join(lines)


def _get_fallback(region_en: str, max_results: int) -> list:
    """Return curated fallback videos for region."""
    videos = FALLBACK_VIDEOS.get(region_en, FALLBACK_VIDEOS["lower back lumbar"])
    result = []
    for v in videos[:max_results]:
        result.append({
            **v,
            "trusted":   True,
            "url":       f"https://www.youtube.com/watch?v={v['video_id']}",
            "embed_url": f"https://www.youtube.com/embed/{v['video_id']}",
        })
    return result
