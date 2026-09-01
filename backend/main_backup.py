from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re
import cv2
import numpy as np


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="BorderGuard AI API",
    description="AI-powered border document screening backend",
    version="2.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# TESSERACT
# ============================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# ============================================================
# BASIC ROUTES
# ============================================================

@app.get("/")
def root():
    return {
        "message": "BorderGuard AI Backend is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "BorderGuard AI"
    }


# ============================================================
# MAIN DOCUMENT SCREENING
# ============================================================

@app.post("/screen-document")
async def screen_document(file: UploadFile = File(...)):

    contents = await file.read()

    try:

        # ----------------------------------------------------
        # OPEN IMAGE
        # ----------------------------------------------------

        image = Image.open(
            io.BytesIO(contents)
        ).convert("RGB")


        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        extracted_text = pytesseract.image_to_string(
            image
        ).strip()


        # ----------------------------------------------------
        # EXTRACT INFORMATION
        # ----------------------------------------------------

        document_type = detect_document_type(
            extracted_text
        )

        name = extract_name(
            extracted_text
        )

        dob = extract_dob(
            extracted_text
        )

        document_number = extract_document_number(
            extracted_text
        )


        # ----------------------------------------------------
        # DOCUMENT VALIDATION
        # ----------------------------------------------------

        validation = validate_document(
            document_type,
            name,
            dob,
            document_number,
            extracted_text
        )


        # ----------------------------------------------------
        # IMAGE ANALYSIS
        # ----------------------------------------------------

        image_analysis = analyze_image(
            image
        )


        # ----------------------------------------------------
        # ADVANCED RISK ENGINE
        # ----------------------------------------------------

        security_assessment = calculate_security_risk(
            validation,
            image_analysis,
            extracted_text
        )


        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        return {

            "success": True,

            "filename": file.filename,

            "document_type": document_type,

            "ocr_confidence": "Processing complete",

            "extracted_data": {

                "name": name,

                "date_of_birth": dob,

                "document_number": document_number
            },

            "validation": validation,

            "image_analysis": image_analysis,

            "security_assessment": security_assessment,

            "raw_text": extracted_text,

            "message":
                "Document successfully processed using OCR and preliminary security analysis."
        }


    except Exception as e:

        return {

            "success": False,

            "filename": file.filename,

            "error": str(e),

            "message":
                "Unable to process the document."
        }


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def detect_document_type(text):

    text_upper = text.upper()

    if (
        "AADHAAR" in text_upper
        or "UNIQUE IDENTIFICATION" in text_upper
    ):
        return "Aadhaar Card"

    if "PASSPORT" in text_upper:
        return "Passport"

    if (
        "DRIVING LICENCE" in text_upper
        or "DRIVING LICENSE" in text_upper
    ):
        return "Driving Licence"

    if "VISA" in text_upper:
        return "Visa"

    if (
        "NATIONAL ID" in text_upper
        or "IDENTITY CARD" in text_upper
    ):
        return "National ID"

    return "Unknown"


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]


    # Look for NAME label

    for i, line in enumerate(lines):

        upper_line = line.upper()

        if "NAME" in upper_line:

            parts = re.split(
                r":|-",
                line,
                maxsplit=1
            )

            if len(parts) > 1:

                possible_name = parts[1].strip()

                if possible_name:
                    return possible_name


            # Name may be on next line

            if i + 1 < len(lines):

                possible_name = lines[i + 1]

                if (
                    len(possible_name.split()) <= 5
                    and not any(
                        char.isdigit()
                        for char in possible_name
                    )
                ):
                    return possible_name


    # Aadhaar fallback

    for i, line in enumerate(lines):

        if line.lower() == "to":

            if i + 1 < len(lines):

                possible_name = lines[i + 1]

                if (
                    len(possible_name.split()) <= 5
                    and not any(
                        char.isdigit()
                        for char in possible_name
                    )
                ):
                    return possible_name


    # DOB fallback

    for i, line in enumerate(lines):

        if "DOB" in line.upper():

            if i > 0:

                possible_name = lines[i - 1]

                if (
                    len(possible_name.split()) <= 5
                    and not any(
                        char.isdigit()
                        for char in possible_name
                    )
                ):
                    return possible_name


    return "Not detected"


# ============================================================
# DATE OF BIRTH
# ============================================================

def extract_dob(text):

    patterns = [

        r"\b\d{2}/\d{2}/\d{4}\b",

        r"\b\d{2}-\d{2}-\d{4}\b",

        r"\b\d{2}\.\d{2}\.\d{4}\b"

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return match.group()


    return "Not detected"


# ============================================================
# DOCUMENT NUMBER
# ============================================================

def extract_document_number(text):

    # Aadhaar

    aadhaar = re.search(
        r"\b\d{4}\s\d{4}\s\d{4}\b",
        text
    )

    if aadhaar:
        return aadhaar.group()


    # Passport-style number

    passport = re.search(
        r"\b[A-Z][0-9]{7}\b",
        text.upper()
    )

    if passport:
        return passport.group()


    return "Not detected"


# ============================================================
# DOCUMENT VALIDATION
# ============================================================

def validate_document(
    document_type,
    name,
    dob,
    document_number,
    text
):

    checks = []

    score = 0


    # --------------------------------------------------------
    # DOCUMENT TYPE
    # --------------------------------------------------------

    if document_type != "Unknown":

        score += 25

        checks.append({

            "check": "Document Type",

            "status": "PASSED",

            "message":
                f"{document_type} detected."
        })

    else:

        checks.append({

            "check": "Document Type",

            "status": "FAILED",

            "message":
                "Document type could not be identified."
        })


    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if name != "Not detected":

        score += 25

        checks.append({

            "check": "Name",

            "status": "PASSED",

            "message":
                "Name detected."
        })

    else:

        checks.append({

            "check": "Name",

            "status": "FAILED",

            "message":
                "Name could not be detected."
        })


    # --------------------------------------------------------
    # DOB
    # --------------------------------------------------------

    if dob != "Not detected":

        score += 25

        checks.append({

            "check": "Date of Birth",

            "status": "PASSED",

            "message":
                "Date of birth detected."
        })

    else:

        checks.append({

            "check": "Date of Birth",

            "status": "FAILED",

            "message":
                "Date of birth could not be detected."
        })


    # --------------------------------------------------------
    # DOCUMENT NUMBER
    # --------------------------------------------------------

    if document_number != "Not detected":

        score += 25

        checks.append({

            "check": "Document Number",

            "status": "PASSED",

            "message":
                "Document number detected."
        })

    else:

        checks.append({

            "check": "Document Number",

            "status": "FAILED",

            "message":
                "Document number could not be detected."
        })


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if score >= 75:

        status = "VALID"

    elif score >= 50:

        status = "REVIEW"

    else:

        status = "INVALID"


    risk_score = 100 - score


    if risk_score <= 20:

        risk_level = "LOW"

    elif risk_score <= 50:

        risk_level = "MEDIUM"

    else:

        risk_level = "HIGH"


    if status == "VALID":

        recommendation = (
            "Document passed preliminary automated screening."
        )

    elif status == "REVIEW":

        recommendation = (
            "Document requires additional verification."
        )

    else:

        recommendation = (
            "Document failed preliminary validation and requires manual review."
        )


    return {

        "status": status,

        "risk_level": risk_level,

        "validation_score": score,

        "risk_score": risk_score,

        "recommendation": recommendation,

        "checks": checks
    }


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_image(image):

    # Convert PIL → OpenCV

    image_array = np.array(image)

    cv_image = cv2.cvtColor(
        image_array,
        cv2.COLOR_RGB2BGR
    )


    height, width = cv_image.shape[:2]


    # --------------------------------------------------------
    # IMAGE SHARPNESS
    # --------------------------------------------------------

    gray = cv2.cvtColor(
        cv_image,
        cv2.COLOR_BGR2GRAY
    )

    laplacian = cv2.Laplacian(
        gray,
        cv2.CV_64F
    )

    sharpness = laplacian.var()


    if sharpness >= 100:

        sharpness_status = "PASSED"

        sharpness_message = (
            "Image is sufficiently sharp."
        )

    else:

        sharpness_status = "WARNING"

        sharpness_message = (
            "Image may be blurry."
        )


    # --------------------------------------------------------
    # IMAGE QUALITY
    # --------------------------------------------------------

    if width >= 500 and height >= 500:

        image_quality = "GOOD"

        quality_status = "PASSED"

        quality_message = (
            "Image resolution is suitable for analysis."
        )

    else:

        image_quality = "LOW"

        quality_status = "WARNING"

        quality_message = (
            "Image resolution may be insufficient."
        )


    # --------------------------------------------------------
    # EDGE ANALYSIS
    # --------------------------------------------------------

    edges = cv2.Canny(
        gray,
        100,
        200
    )

    edge_density = (
        np.count_nonzero(edges)
        / edges.size
    )


    if edge_density < 0.30:

        structural_status = "PASSED"

        structural_message = (
            "No abnormal edge density detected."
        )

    else:

        structural_status = "WARNING"

        structural_message = (
            "High edge density detected; manual review recommended."
        )


    # --------------------------------------------------------
    # COLOR ANALYSIS
    # --------------------------------------------------------

    hsv = cv2.cvtColor(
        cv_image,
        cv2.COLOR_BGR2HSV
    )

    saturation_mean = np.mean(
        hsv[:, :, 1]
    )


    if 20 <= saturation_mean <= 220:

        color_status = "PASSED"

        color_message = (
            "Color distribution appears consistent."
        )

    else:

        color_status = "WARNING"

        color_message = (
            "Unusual color distribution detected."
        )


    # --------------------------------------------------------
    # TAMPERING SCORE
    # --------------------------------------------------------

    tampering_score = 0


    if sharpness_status == "WARNING":
        tampering_score += 15

    if quality_status == "WARNING":
        tampering_score += 15

    if structural_status == "WARNING":
        tampering_score += 35

    if color_status == "WARNING":
        tampering_score += 35


    if tampering_score <= 20:

        tampering_status = (
            "NO OBVIOUS TAMPERING"
        )

        risk_level = "LOW"

    elif tampering_score <= 50:

        tampering_status = (
            "POSSIBLE ANOMALY"
        )

        risk_level = "MEDIUM"

    else:

        tampering_status = (
            "HIGH RISK IMAGE"
        )

        risk_level = "HIGH"


    return {

        "status": tampering_status,

        "risk_level": risk_level,

        "tampering_score": tampering_score,

        "image_quality": image_quality,

        "resolution": {

            "width": width,

            "height": height
        },

        "checks": [

            {

                "check": "Image Quality",

                "status": quality_status,

                "message": quality_message
            },

            {

                "check": "Image Sharpness",

                "status": sharpness_status,

                "message": sharpness_message
            },

            {

                "check": "Structural Analysis",

                "status": structural_status,

                "message": structural_message
            },

            {

                "check": "Color Consistency",

                "status": color_status,

                "message": color_message
            }
        ]
    }


# ============================================================
# ADVANCED SECURITY RISK ENGINE
# ============================================================

def calculate_security_risk(
    validation,
    image_analysis,
    extracted_text
):

    # Start with validation risk

    validation_risk = validation["risk_score"]

    # Image tampering risk

    tampering_risk = image_analysis[
        "tampering_score"
    ]


    # OCR text quality

    if len(extracted_text) >= 100:

        ocr_risk = 0

    elif len(extracted_text) >= 50:

        ocr_risk = 10

    else:

        ocr_risk = 25


    # --------------------------------------------------------
    # COMBINED RISK
    # --------------------------------------------------------

    combined_risk = round(

        (
            validation_risk * 0.50
            +
            tampering_risk * 0.40
            +
            ocr_risk * 0.10
        )

    )


    # Keep score between 0 and 100

    combined_risk = max(
        0,
        min(100, combined_risk)
    )


    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if combined_risk <= 20:

        risk_level = "LOW"

        status = "VERIFIED"

        recommendation = (
            "Document passed preliminary automated screening. "
            "No obvious tampering indicators detected."
        )

    elif combined_risk <= 50:

        risk_level = "MEDIUM"

        status = "REVIEW"

        recommendation = (
            "Document contains potential anomalies. "
            "Manual verification is recommended."
        )

    else:

        risk_level = "HIGH"

        status = "HIGH RISK"

        recommendation = (
            "Document shows significant risk indicators. "
            "Immediate manual verification is recommended."
        )


    return {

        "status": status,

        "risk_level": risk_level,

        "risk_score": combined_risk,

        "recommendation": recommendation
    }