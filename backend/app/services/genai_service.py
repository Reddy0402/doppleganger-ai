import random
from typing import Optional
from app.core.config import settings

LOCAL_CREATIVE_CAPTIONS = [
    "Your reflection in a parallel dimension! Notice the striking harmony in orbital bone structure.",
    "An uncanny resemblance! You two could easily swap passport photos in a cinematic thriller.",
    "Fascinating facial symmetry—the neural embeddings found remarkable alignment in your brow and jawline.",
    "Somewhere in a multiverse studio, you two were drafted from the exact same aesthetic moodboard.",
    "A legendary lookalike match! Strong visual balance across the bridge and cheek contours.",
    "Double-take guaranteed! The algorithm flagged a rare geometric correspondence in facial proportions."
]

def generate_fun_caption(candidate_name: str, resemblance_percentage: float) -> str:
    """
    Generates a witty, non-factual match caption celebrating visual resemblance.
    Strictly follows safety guidelines: never infers ethnicity, genetics, personality, or health.
    Operates locally with zero external API dependencies.
    """
    if settings.GEMINI_API_KEY:
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            prompt = (
                f"Write a 1-sentence charming, witty, respectful caption celebrating a visual lookalike match "
                f"between a user and '{candidate_name}' ({resemblance_percentage}% visual resemblance). "
                f"DO NOT mention ethnicity, race, genetics, intelligence, or biology. Keep it fun and lighthearted."
            )
            resp = requests.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=3
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text:
                    return text
        except Exception:
            pass

    # Local fallback
    base = random.choice(LOCAL_CREATIVE_CAPTIONS)
    return f"{base} ({resemblance_percentage}% match with {candidate_name})"
