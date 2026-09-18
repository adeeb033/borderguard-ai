import os
import cv2
import numpy as np
from PIL import Image



def analyze_localized_edges(image_path):
    findings = []

    try:
        image = cv2.imread(image_path)

        if image is None:
            return {
                "localized_edge_score": 0,
                "color_texture_score": 0,
                "edge_variation": 0,
                "findings": [
                    "Localized image analysis unavailable."
                ]
            }

        # Convert image to HSV so that
        # brightness and color can be analyzed separately.
        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2HSV
        )

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        height, width = gray.shape

        # Divide image into many small regions.
        grid_rows = 12
        grid_cols = 16

        brightness_values = []
        texture_values = []
        edge_values = []

        edges = cv2.Canny(
            gray,
            50,
            150
        )

        for row in range(grid_rows):

            for col in range(grid_cols):

                y1 = int(
                    row * height / grid_rows
                )

                y2 = int(
                    (row + 1) * height / grid_rows
                )

                x1 = int(
                    col * width / grid_cols
                )

                x2 = int(
                    (col + 1) * width / grid_cols
                )

                gray_region = gray[
                    y1:y2,
                    x1:x2
                ]

                hsv_region = hsv[
                    y1:y2,
                    x1:x2
                ]

                edge_region = edges[
                    y1:y2,
                    x1:x2
                ]

                if gray_region.size == 0:
                    continue

                brightness = float(
                    np.mean(
                        gray_region
                    )
                )

                texture = float(
                    np.std(
                        gray_region
                    )
                )

                edge_density = float(
                    np.mean(
                        edge_region > 0
                    )
                )

                brightness_values.append(
                    brightness
                )

                texture_values.append(
                    texture
                )

                edge_values.append(
                    edge_density
                )

        if not brightness_values:

            return {
                "localized_edge_score": 0,
                "color_texture_score": 0,
                "edge_variation": 0,
                "findings": [
                    "No usable image regions found."
                ]
            }

        # Calculate regional variation.
        brightness_variation = float(
            np.std(
                brightness_values
            )
        )

        texture_variation = float(
            np.std(
                texture_values
            )
        )

        edge_variation = float(
            np.std(
                edge_values
            ) * 100
        )

        color_texture_score = 0

        # Strong regional brightness variation
        if brightness_variation > 35:

            color_texture_score += 15

            findings.append(
                "Strong regional brightness variation detected."
            )

        elif brightness_variation > 25:

            color_texture_score += 10

            findings.append(
                "Moderate regional brightness variation detected."
            )

        # Strong regional texture variation
        if texture_variation > 20:

            color_texture_score += 15

            findings.append(
                "Strong regional texture variation detected."
            )

        elif texture_variation > 12:

            color_texture_score += 10

            findings.append(
                "Moderate regional texture variation detected."
            )

        # Edge variation
        if edge_variation > 15:

            color_texture_score += 10

            findings.append(
                "Strong regional edge variation detected."
            )

        elif edge_variation > 10:

            color_texture_score += 5

            findings.append(
                "Moderate regional edge variation detected."
            )

        if color_texture_score == 0:

            findings.append(
                "No strong regional color or texture "
                "inconsistency detected."
            )

        # Limit contribution from this detector.
        color_texture_score = min(
            color_texture_score,
            30
        )

        return {
            "brightness_variation": round(
                brightness_variation,
                2
            ),
            "texture_variation": round(
                texture_variation,
                2
            ),
            "edge_variation": round(
                edge_variation,
                2
            ),
            "localized_edge_score":
                color_texture_score,
            "color_texture_score":
                color_texture_score,
            "findings": findings
        }

    except Exception as e:

        return {
            "localized_edge_score": 0,
            "color_texture_score": 0,
            "edge_variation": 0,
            "findings": [
                "Localized image analysis unavailable: "
                + str(e)
            ]
        }


def analyze_metadata(image_path):
    """
    Basic image metadata analysis.
    Metadata presence is treated only as a forensic indicator.
    """

    findings = []

    try:
        image = Image.open(image_path)

        width, height = image.size
        image_format = image.format or "UNKNOWN"

        metadata = image.getexif()

        if metadata and len(metadata) > 0:
            findings.append(
                "Image contains embedded EXIF metadata."
            )
        else:
            findings.append(
                "No EXIF metadata detected."
            )

        return {
            "format": image_format,
            "width": width,
            "height": height,
            "metadata_present": bool(metadata),
            "findings": findings
        }

    except Exception as e:
        return {
            "format": "UNKNOWN",
            "width": 0,
            "height": 0,
            "metadata_present": False,
            "findings": [
                f"Metadata analysis unavailable: {str(e)}"
            ]
        }


def calculate_ela(image_path, quality=90):
    """
    Error Level Analysis (ELA).

    ELA compares the original image with a recompressed copy.
    Areas with unusually high differences can become forensic
    indicators of inconsistent image processing.

    ELA is not proof of forgery.
    """

    try:
        original = Image.open(image_path).convert("RGB")

        temp_path = image_path + "_ela_temp.jpg"

        original.save(
            temp_path,
            "JPEG",
            quality=quality
        )

        recompressed = Image.open(temp_path).convert("RGB")

        original_array = np.array(original).astype(np.int16)
        recompressed_array = np.array(recompressed).astype(np.int16)

        difference = np.abs(
            original_array - recompressed_array
        )

        ela_score = float(np.mean(difference))

        max_difference = float(np.max(difference))

        amplified = np.clip(
            difference * 10,
            0,
            255
        ).astype(np.uint8)

        ela_gray = cv2.cvtColor(
            amplified,
            cv2.COLOR_RGB2GRAY
        )

        high_difference_pixels = np.sum(
            ela_gray > 80
        )

        total_pixels = ela_gray.size

        high_difference_ratio = (
            high_difference_pixels / total_pixels
            if total_pixels > 0
            else 0
        )

        os.remove(temp_path)

        return {
            "ela_score": round(ela_score, 2),
            "max_difference": round(max_difference, 2),
            "high_difference_ratio": round(
                high_difference_ratio * 100,
                2
            )
        }

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "ela_score": 0,
            "max_difference": 0,
            "high_difference_ratio": 0,
            "error": str(e)
        }


def analyze_noise_consistency(image_path):
    """
    Estimates local noise consistency across image regions.

    Strong variation between regions can be a suspicious indicator,
    but it is not proof of manipulation.
    """

    try:
        image = cv2.imread(
            image_path,
            cv2.IMREAD_GRAYSCALE
        )

        if image is None:
            raise ValueError(
                "Unable to read image."
            )

        blurred = cv2.GaussianBlur(
            image,
            (5, 5),
            0
        )

        noise = cv2.absdiff(
            image,
            blurred
        )

        height, width = noise.shape

        regions = []

        rows = 2
        cols = 2

        for r in range(rows):
            for c in range(cols):

                y1 = r * height // rows
                y2 = (r + 1) * height // rows

                x1 = c * width // cols
                x2 = (c + 1) * width // cols

                region = noise[
                    y1:y2,
                    x1:x2
                ]

                if region.size > 0:
                    regions.append(
                        float(np.mean(region))
                    )

        if not regions:
            return {
                "noise_mean": 0,
                "noise_variation": 0,
                "suspicious": False
            }

        noise_mean = float(
            np.mean(regions)
        )

        noise_variation = float(
            np.std(regions)
        )

        suspicious = noise_variation > 8.0

        return {
            "noise_mean": round(
                noise_mean,
                2
            ),
            "noise_variation": round(
                noise_variation,
                2
            ),
            "suspicious": suspicious
        }

    except Exception as e:
        return {
            "noise_mean": 0,
            "noise_variation": 0,
            "suspicious": False,
            "error": str(e)
        }


def analyze_image_quality(image_path):
    """
    Basic forensic image quality measurements.
    """

    try:
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(
                "Unable to read image."
            )

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        height, width = gray.shape

        sharpness = float(
            cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()
        )

        brightness = float(
            np.mean(gray)
        )

        contrast = float(
            np.std(gray)
        )

        return {
            "width": width,
            "height": height,
            "sharpness": round(
                sharpness,
                2
            ),
            "brightness": round(
                brightness,
                2
            ),
            "contrast": round(
                contrast,
                2
            )
        }

    except Exception as e:
        return {
            "width": 0,
            "height": 0,
            "sharpness": 0,
            "brightness": 0,
            "contrast": 0,
            "error": str(e)
        }


def perform_forensic_analysis(image_path):
    """
    Main Advanced Forensic Analysis function.

    Combines multiple image-level indicators into an
    explainable forensic assessment.
    """

    metadata = analyze_metadata(
        image_path
    )

    ela = calculate_ela(
        image_path
    )

    noise = analyze_noise_consistency(
        image_path
    )

    quality = analyze_image_quality(
        image_path
    )
    
    localized_edge = analyze_localized_edges(
        image_path
    )

    risk_score = 0

    findings = []

    # -------------------------------------------------
    # ELA INDICATOR
    # -------------------------------------------------

    if ela.get("high_difference_ratio", 0) > 15:

        risk_score += 30

        findings.append(
            "High ELA difference detected in a significant "
            "portion of the image."
        )

    elif ela.get("high_difference_ratio", 0) > 8:

        risk_score += 15

        findings.append(
            "Moderate ELA differences detected."
        )

    else:

        findings.append(
            "ELA differences are within the expected range."
        )

    # -------------------------------------------------
    # NOISE INDICATOR
    # -------------------------------------------------

    if noise.get("suspicious", False):

        risk_score += 25

        findings.append(
            "Noise consistency varies significantly "
            "between image regions."
        )

    else:

        findings.append(
            "No strong regional noise inconsistency detected."
        )

    # -------------------------------------------------
    # LOCALIZED EDGE INDICATOR
    # -------------------------------------------------

    localized_edge_score = localized_edge.get(
        "localized_edge_score",
        0
    )

    if localized_edge_score > 0:

        risk_score += localized_edge_score

        for finding in localized_edge.get(
            "findings",
            []
        ):

            findings.append(
                finding
            )

    else:

        findings.append(
            "No strong localized edge variation detected."
        )

    # -------------------------------------------------
    # IMAGE QUALITY
    # -------------------------------------------------

    if quality.get("sharpness", 0) < 50:

        risk_score += 10

        findings.append(
            "Image sharpness is low and may affect forensic analysis."
        )

    if quality.get("brightness", 0) < 40:

        risk_score += 5

        findings.append(
            "Image brightness is relatively low."
        )

    elif quality.get("brightness", 0) > 220:

        risk_score += 5

        findings.append(
            "Image brightness is relatively high."
        )

    # -------------------------------------------------
    # METADATA
    # -------------------------------------------------

    if metadata.get("metadata_present", False):

        findings.append(
            "Embedded metadata is present and should be "
            "considered during forensic review."
        )

    else:

        findings.append(
            "No embedded EXIF metadata was detected."
        )

    # -------------------------------------------------
    # LIMIT SCORE
    # -------------------------------------------------

    risk_score = min(
        risk_score,
        100
    )

    if risk_score >= 60:

        status = "SUSPICIOUS"
        risk_level = "HIGH"

    elif risk_score >= 30:

        status = "REVIEW"
        risk_level = "MEDIUM"

    else:

        status = "NO STRONG INDICATORS"
        risk_level = "LOW"

    return {
        "status": status,
        "risk_level": risk_level,
        "forensic_risk_score": risk_score,
        "metadata": metadata,
        "ela": ela,
        "noise_analysis": noise,
        "image_quality": quality,
        "localized_edge_analysis": localized_edge,
        "findings": findings,
        "message": (
            "Forensic analysis identifies image-level "
            "suspicious indicators for officer review. "
            "It does not by itself prove document forgery."
        )
    }