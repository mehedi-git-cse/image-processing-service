import cv2
import numpy as np
from io import BytesIO
from PIL import Image

# ---------------------------------------------------------------------------
# Optional pretrained AI-image classifier (HuggingFace transformers).
# Loaded lazily so the service still runs if transformers is unavailable
# or the model cannot be downloaded.
# ---------------------------------------------------------------------------
_HF_PIPELINE = None
_HF_LOAD_FAILED = False
_HF_MODEL_ID = "Organika/sdxl-detector"


def _get_hf_pipeline():
    global _HF_PIPELINE, _HF_LOAD_FAILED
    if _HF_PIPELINE is not None or _HF_LOAD_FAILED:
        return _HF_PIPELINE
    try:
        from transformers import pipeline
        _HF_PIPELINE = pipeline(
            "image-classification",
            model=_HF_MODEL_ID,
            device=-1,  # CPU
        )
    except Exception as e:
        print(f"[ai_image_detector] HF model unavailable, falling back to heuristic: {e}")
        _HF_LOAD_FAILED = True
        _HF_PIPELINE = None
    return _HF_PIPELINE


def _classify_with_hf(image_bytes):
    """Run the pretrained classifier. Returns dict or None on failure."""
    pipe = _get_hf_pipeline()
    if pipe is None:
        return None
    try:
        pil_img = Image.open(BytesIO(image_bytes)).convert("RGB")
        preds = pipe(pil_img)
        # Normalise to {label: score}
        scores = {p["label"].lower(): float(p["score"]) for p in preds}

        # Common labels across AI-detector models:
        # "ai", "artificial", "fake", "generated", "sdxl" -> AI-generated
        # "human", "real", "natural" -> real
        ai_keys = ("ai", "artificial", "fake", "generated", "sdxl")
        real_keys = ("human", "real", "natural")

        ai_prob = max(
            (v for k, v in scores.items() if any(t in k for t in ai_keys)),
            default=0.0,
        )
        real_prob = max(
            (v for k, v in scores.items() if any(t in k for t in real_keys)),
            default=0.0,
        )

        if ai_prob == 0.0 and real_prob == 0.0:
            # Unknown label schema - treat highest score as decisive
            top = max(scores.items(), key=lambda kv: kv[1])
            return {
                "source": "huggingface",
                "model": _HF_MODEL_ID,
                "label": top[0],
                "score": round(top[1], 4),
                "raw": {k: round(v, 4) for k, v in scores.items()},
            }

        return {
            "source": "huggingface",
            "model": _HF_MODEL_ID,
            "ai_prob": round(ai_prob, 4),
            "real_prob": round(real_prob, 4),
            "raw": {k: round(v, 4) for k, v in scores.items()},
        }
    except Exception as e:
        print(f"[ai_image_detector] HF inference failed: {e}")
        return None


def _ela_score(img_bgr):
    """Error Level Analysis: re-compress and measure residual.
    AI / heavily edited images tend to have very uniform residuals,
    real camera JPEGs have higher variance in textured regions.
    Returns mean residual (lower = more suspicious)."""
    try:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        _, enc = cv2.imencode(".jpg", img_bgr, encode_param)
        recompressed = cv2.imdecode(enc, cv2.IMREAD_COLOR)
        diff = cv2.absdiff(img_bgr, recompressed)
        return float(np.mean(diff))
    except Exception:
        return 0.0


def _heuristic_score(image_bytes):
    """Combined heuristic signals. Returns (ai_score, metrics_dict) or (None, {})."""
    try:
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return None, {}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        residual = cv2.absdiff(gray, blur)
        noise_level = float(np.mean(residual))

        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude = np.log(np.abs(fshift) + 1)
        cy, cx = h // 2, w // 2
        r = min(h, w) // 6
        high_freq_mask = np.ones_like(magnitude)
        high_freq_mask[cy - r:cy + r, cx - r:cx + r] = 0
        high_freq_energy = float(np.mean(magnitude * high_freq_mask))

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        saturation = float(np.mean(hsv[:, :, 1]))
        brightness_std = float(np.std(hsv[:, :, 2]))

        ela_residual = _ela_score(img)

        noise_susp = max(0.0, min(1.0, (2.5 - noise_level) / 2.0))
        freq_susp = max(0.0, min(1.0, (8.0 - high_freq_energy) / 3.0))
        sat_susp = max(0.0, min(1.0, (saturation - 85) / 70))
        smooth_susp = max(0.0, min(1.0, (80 - brightness_std) / 60))
        ela_susp = max(0.0, min(1.0, (4.0 - ela_residual) / 4.0))

        ai_score = round(
            0.30 * noise_susp
            + 0.20 * freq_susp
            + 0.10 * sat_susp
            + 0.15 * smooth_susp
            + 0.25 * ela_susp,
            3,
        )

        return ai_score, {
            "noise_level": round(noise_level, 3),
            "high_freq_energy": round(high_freq_energy, 3),
            "saturation": round(saturation, 2),
            "brightness_std": round(brightness_std, 2),
            "ela_residual": round(ela_residual, 3),
        }
    except Exception:
        return None, {}


def check_ai_generated(image_bytes):
    """
    Detect AI-generated images using a pretrained HuggingFace classifier
    (Organika/sdxl-detector) when available, with a heuristic fallback.

    Returns:
        {
            "is_ai_generated": bool,
            "ai_score": float,   # 0.0 - 1.0 suspicion
            "source": "huggingface" | "heuristic",
            "reason": str,
            ...debug metrics
        }
    """
    try:
        hf_result = _classify_with_hf(image_bytes)

        # Also compute heuristic for debug/fallback
        heuristic_ai_score, heuristic_metrics = _heuristic_score(image_bytes)

        if hf_result is not None and "ai_prob" in hf_result:
            ai_score = hf_result["ai_prob"]
            is_ai = ai_score >= 0.55
            return {
                "is_ai_generated": is_ai,
                "ai_score": round(ai_score, 4),
                "source": "huggingface",
                "model": hf_result["model"],
                "raw": hf_result["raw"],
                "heuristic_score": heuristic_ai_score,
                "heuristic_metrics": heuristic_metrics,
                "reason": (
                    "Image classified as AI-generated by pretrained model"
                    if is_ai
                    else "Image classified as real by pretrained model"
                ),
            }

        # Fallback: heuristic only.
        # Heuristic is noisy, especially on clean studio portraits (white
        # background, soft lighting). Use a conservative threshold and
        # require ELA + noise to BOTH be suspicious before flagging.
        if heuristic_ai_score is None:
            return _fail("Image decode failed")

        ela_susp_metric = heuristic_metrics.get("ela_residual", 99)
        noise_metric = heuristic_metrics.get("noise_level", 99)

        strong_signal = (ela_susp_metric < 1.5) and (noise_metric < 1.2)
        is_ai = heuristic_ai_score >= 0.65 and strong_signal

        return {
            "is_ai_generated": is_ai,
            "ai_score": heuristic_ai_score,
            "source": "heuristic",
            **heuristic_metrics,
            "reason": (
                "Image looks synthetic/AI-generated (heuristic fallback: very low sensor noise and uniform compression)"
                if is_ai
                else "Image appears to be a real photo (heuristic fallback)"
            ),
        }

    except Exception as e:
        return _fail(str(e))


def _fail(msg):
    return {
        "is_ai_generated": False,
        "ai_score": 0.0,
        "source": "error",
        "reason": f"AI detection failed: {msg}",
    }
