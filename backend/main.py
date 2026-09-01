from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image, ImageOps, ImageFilter

import pytesseract
import io
import re
import cv2
import numpy as np
import os


# ============================================================
# FASTAPI APP
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
# TESSERACT CONFIGURATION
# ============================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ============================================================
# FACE CASCADE CONFIGURATION
# ============================================================

# Your XML file is located here:
# backend/models/haarcascade_frontalface_default.xml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FACE_CASCADE_PATH = os.path.join(
    BASE_DIR,
    "models",
    "haarcascade_frontalface_default.xml"
)


# ============================================================
# BASIC API
# ============================================================

@app.get("/")
def root():
    return {
        "message": "BorderGuard AI Backend is running!",
        "version": "2.0.0"
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
        )

        if image.mode != "RGB":
            image = image.convert("RGB")


        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        ocr_result = perform_strong_ocr(image)

        extracted_text = ocr_result["text"]

        ocr_confidence = ocr_result["confidence"]


        # ----------------------------------------------------
        # DOCUMENT TYPE
        # ----------------------------------------------------

        document_type = detect_document_type(
            extracted_text,
            image
        )


        # ----------------------------------------------------
        # MRZ
        # ----------------------------------------------------

        mrz_data = parse_mrz(
            extracted_text
        )


        # ----------------------------------------------------
        # EXTRACT INFORMATION
        # ----------------------------------------------------

        name = extract_name(
            extracted_text,
            document_type,
            mrz_data
        )

        dob = extract_dob(
            extracted_text,
            mrz_data
        )

        document_number = extract_document_number(
            extracted_text,
            document_type,
            mrz_data
        )

        nationality = extract_nationality(
            extracted_text,
            document_type,
            mrz_data
        )

        gender = extract_gender(
            extracted_text,
            mrz_data
        )

        expiry_date = extract_expiry_date(
            extracted_text,
            document_type,
            mrz_data
        )


        # ----------------------------------------------------
        # DOCUMENT VALIDATION
        # ----------------------------------------------------

        validation = validate_document(
            document_type=document_type,
            name=name,
            dob=dob,
            document_number=document_number,
            expiry_date=expiry_date,
            extracted_text=extracted_text,
            mrz_data=mrz_data
        )


        # ----------------------------------------------------
        # IMAGE ANALYSIS
        # ----------------------------------------------------

        image_analysis = analyze_image(
            contents
        )


        # ----------------------------------------------------
        # FACE DETECTION
        # ----------------------------------------------------

        face_analysis = detect_face(
            contents
        )


        # ----------------------------------------------------
        # SECURITY ASSESSMENT
        # ----------------------------------------------------

        security_assessment = create_security_assessment(
            validation,
            image_analysis,
            face_analysis,
            ocr_confidence,
            document_type
        )


        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        return {
            "success": True,

            "filename": file.filename,

            "document_type": document_type,

            "ocr_confidence": ocr_confidence,

            "extracted_data": {
                "name": name,
                "date_of_birth": dob,
                "document_number": document_number,
                "nationality": nationality,
                "gender": gender,
                "expiry_date": expiry_date
            },

            "mrz": mrz_data,

            "validation": validation,

            "image_analysis": image_analysis,

            "face_analysis": face_analysis,

            "security_assessment": security_assessment,

            "raw_text": extracted_text,

            "message": (
                "Document successfully processed using "
                "enhanced OCR, document validation, "
                "image analysis and face detection."
            )
        }


    except Exception as e:

        return {
            "success": False,
            "filename": file.filename,
            "error": str(e),
            "message": "Unable to process the document."
        }


# ============================================================
# STRONG OCR ENGINE
# ============================================================

def perform_strong_ocr(image):

    try:

        # ----------------------------------------------------
        # UPSCALE
        # ----------------------------------------------------

        width, height = image.size

        scale = 2

        upscaled = image.resize(
            (
                width * scale,
                height * scale
            ),
            Image.Resampling.LANCZOS
        )


        # ----------------------------------------------------
        # GRAYSCALE
        # ----------------------------------------------------

        gray = ImageOps.grayscale(
            upscaled
        )


        # ----------------------------------------------------
        # OCR VERSIONS
        # ----------------------------------------------------

        versions = []

        versions.append(
            ("original", upscaled)
        )

        versions.append(
            ("grayscale", gray)
        )


        # ----------------------------------------------------
        # CONTRAST
        # ----------------------------------------------------

        contrast = ImageOps.autocontrast(
            gray
        )

        versions.append(
            ("contrast", contrast)
        )


        # ----------------------------------------------------
        # SHARPEN
        # ----------------------------------------------------

        sharpened = contrast.filter(
            ImageFilter.SHARPEN
        )

        versions.append(
            ("sharpened", sharpened)
        )


        # ----------------------------------------------------
        # THRESHOLD
        # ----------------------------------------------------

        gray_np = np.array(gray)

        threshold = cv2.threshold(
            gray_np,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

        threshold_image = Image.fromarray(
            threshold
        )

        versions.append(
            ("threshold", threshold_image)
        )


        # ----------------------------------------------------
        # ADAPTIVE THRESHOLD
        # ----------------------------------------------------

        adaptive = cv2.adaptiveThreshold(
            gray_np,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10
        )

        adaptive_image = Image.fromarray(
            adaptive
        )

        versions.append(
            ("adaptive", adaptive_image)
        )


        # ----------------------------------------------------
        # OCR ALL VERSIONS
        # ----------------------------------------------------

        best_text = ""

        best_confidence = 0

        best_method = "original"


        for method, version in versions:

            try:

                data = pytesseract.image_to_data(
                    version,
                    config="--oem 3 --psm 6",
                    output_type=pytesseract.Output.DICT
                )

                words = []

                confidences = []


                for i in range(
                    len(data["text"])
                ):

                    word = data["text"][i].strip()

                    conf = data["conf"][i]


                    if word:
                        words.append(word)


                    try:

                        conf_value = float(
                            conf
                        )

                        if conf_value >= 0:

                            confidences.append(
                                conf_value
                            )

                    except Exception:
                        pass


                text = " ".join(
                    words
                ).strip()


                if confidences:

                    confidence = (
                        sum(confidences)
                        /
                        len(confidences)
                    )

                else:

                    confidence = 0


                if (
                    confidence > best_confidence
                    or (
                        confidence == best_confidence
                        and len(text) > len(best_text)
                    )
                ):

                    best_confidence = confidence

                    best_text = text

                    best_method = method


            except Exception:

                continue


        # ----------------------------------------------------
        # FALLBACK OCR
        # ----------------------------------------------------

        if not best_text:

            best_text = pytesseract.image_to_string(
                upscaled,
                config="--oem 3 --psm 6"
            ).strip()

            best_confidence = 0


        # ----------------------------------------------------
        # SECOND OCR PASS
        # ----------------------------------------------------

        mrz_text = pytesseract.image_to_string(
            threshold_image,
            config="--oem 3 --psm 6"
        )


        # ----------------------------------------------------
        # COMBINE
        # ----------------------------------------------------

        combined_text = (
            best_text
            + "\n"
            + mrz_text
        )


        combined_text = clean_ocr_text(
            combined_text
        )


        return {
            "text": combined_text,
            "confidence": round(
                best_confidence,
                2
            ),
            "method": best_method
        }


    except Exception as e:

        return {
            "text": "",
            "confidence": 0,
            "method": "failed",
            "error": str(e)
        }


# ============================================================
# CLEAN OCR TEXT
# ============================================================

def clean_ocr_text(text):

    text = text.replace(
        "\x0c",
        " "
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def detect_document_type(
    text,
    image=None
):

    text_upper = text.upper()


    # --------------------------------------------------------
    # PASSPORT
    # --------------------------------------------------------

    if (
        "PASSPORT" in text_upper
        or "P<" in text_upper
        or re.search(
            r"[A-Z<]{2,3}<[A-Z<]{3,}",
            text_upper
        )
    ):

        return "Passport"


    # --------------------------------------------------------
    # AADHAAR
    # --------------------------------------------------------

    if (
        "AADHAAR" in text_upper
        or "UIDAI" in text_upper
        or "UNIQUE IDENTIFICATION" in text_upper
    ):

        return "Aadhaar Card"


    # --------------------------------------------------------
    # DRIVING LICENCE
    # --------------------------------------------------------

    if (
        "DRIVING LICENCE" in text_upper
        or "DRIVING LICENSE" in text_upper
        or "DL NO" in text_upper
    ):

        return "Driving Licence"


    # --------------------------------------------------------
    # VISA
    # --------------------------------------------------------

    if (
        "VISA" in text_upper
        or "ENTRY PERMIT" in text_upper
        or "VISA TYPE" in text_upper
    ):

        return "Visa"


    # --------------------------------------------------------
    # NATIONAL ID
    # --------------------------------------------------------

    if (
        "NATIONAL ID" in text_upper
        or "IDENTITY CARD" in text_upper
    ):

        return "National ID"


    return "Unknown"


# ============================================================
# PASSPORT MRZ PARSER
# ============================================================

def parse_mrz(text):

    result = {
        "detected": False,
        "document_code": None,
        "issuing_country": None,
        "passport_number": None,
        "nationality": None,
        "date_of_birth": None,
        "sex": None,
        "expiry_date": None,
        "surname": None,
        "given_names": None
    }


    try:

        lines = [

            re.sub(
                r"[^A-Z0-9<]",
                "",
                line.upper()
            )

            for line in text.splitlines()

        ]


        mrz_start = None


        # ----------------------------------------------------
        # Find P<
        # ----------------------------------------------------

        for i, line in enumerate(lines):

            if (
                line.startswith("P<")
                and len(line) >= 20
            ):

                mrz_start = i

                break


        # ----------------------------------------------------
        # OCR fallback
        # ----------------------------------------------------

        if mrz_start is None:

            for i, line in enumerate(lines):

                if (
                    "P<" in line
                    and len(line) >= 20
                ):

                    mrz_start = i

                    break


        if mrz_start is None:

            return result


        if mrz_start + 1 >= len(lines):

            return result


        line1 = lines[mrz_start]

        line2 = lines[mrz_start + 1]


        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        line1 = line1.replace(
            " ",
            ""
        )

        line2 = line2.replace(
            " ",
            ""
        )


        # ----------------------------------------------------
        # Document code
        # ----------------------------------------------------

        if line1.startswith("P<"):

            result["document_code"] = "P"


        # ----------------------------------------------------
        # Issuing country
        # ----------------------------------------------------

        if len(line1) >= 5:

            result["issuing_country"] = (
                line1[2:5]
                .replace("<", "")
            )


        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        if len(line1) > 5:

            name_part = line1[5:]

            name_parts = name_part.split(
                "<<"
            )


            if name_parts:

                surname = (
                    name_parts[0]
                    .replace("<", " ")
                    .strip()
                )

                result["surname"] = clean_name(
                    surname
                )


            if len(name_parts) > 1:

                given_names = (
                    name_parts[1]
                    .replace("<", " ")
                    .strip()
                )

                result["given_names"] = clean_name(
                    given_names
                )


        # ----------------------------------------------------
        # SECOND MRZ LINE
        # ----------------------------------------------------

        if len(line2) >= 44:

            result["passport_number"] = (
                line2[0:9]
                .replace("<", "")
                .strip()
            )


            result["nationality"] = (
                line2[10:13]
                .replace("<", "")
                .strip()
            )


            raw_dob = line2[13:19]

            result["date_of_birth"] = (
                convert_mrz_date(
                    raw_dob
                )
            )


            sex = line2[20:21]

            if sex in ["M", "F"]:

                result["sex"] = sex


            raw_expiry = line2[21:27]

            result["expiry_date"] = (
                convert_mrz_date(
                    raw_expiry
                )
            )


            result["detected"] = True


    except Exception:

        return result


    return result


# ============================================================
# MRZ DATE
# ============================================================

def convert_mrz_date(value):

    if not re.fullmatch(
        r"\d{6}",
        value
    ):

        return None


    year = int(
        value[0:2]
    )

    month = value[2:4]

    day = value[4:6]


    if year <= 30:

        full_year = 2000 + year

    else:

        full_year = 1900 + year


    return (
        f"{day}/{month}/{full_year}"
    )


# ============================================================
# NAME EXTRACTION
# ============================================================

# ============================================================
# IMPROVED NAME EXTRACTION
# ============================================================

def extract_name(text, document_type, mrz_data):

    candidates = []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # --------------------------------------------------------
    # 1. PASSPORT MRZ NAME
    # --------------------------------------------------------

    if document_type == "Passport":

        surname = mrz_data.get("surname")
        given_names = mrz_data.get("given_names")

        if surname and given_names:
            candidates.append(
                f"{given_names} {surname}"
            )

        elif surname:
            candidates.append(surname)

    # --------------------------------------------------------
    # 2. EXPLICIT NAME LABEL
    # --------------------------------------------------------

    for i, line in enumerate(lines):

        upper = line.upper()

        if re.search(
            r"\b(NAME|FULL NAME)\b",
            upper
        ):

            # Name on same line
            parts = re.split(
                r"[:\-]",
                line,
                maxsplit=1
            )

            if len(parts) > 1:

                possible = clean_name_candidate(
                    parts[1]
                )

                if is_possible_name(possible):
                    candidates.append(possible)

            # Name on next line
            if i + 1 < len(lines):

                possible = clean_name_candidate(
                    lines[i + 1]
                )

                if is_possible_name(possible):
                    candidates.append(possible)

    # --------------------------------------------------------
    # 3. AADHAAR "TO" SECTION
    # --------------------------------------------------------

    for i, line in enumerate(lines):

        if line.strip().upper() == "TO":

            for offset in range(1, 4):

                if i + offset >= len(lines):
                    break

                possible = clean_name_candidate(
                    lines[i + offset]
                )

                if is_possible_name(possible):
                    candidates.append(possible)

    # --------------------------------------------------------
    # 4. SEARCH FOR CLEAN PERSON-NAME PATTERNS
    # --------------------------------------------------------

    for line in lines:

        candidate = clean_name_candidate(line)

        if is_possible_name(candidate):
            candidates.append(candidate)

    # --------------------------------------------------------
    # 5. LOOK NEAR DOB
    # --------------------------------------------------------

    for i, line in enumerate(lines):

        upper = line.upper()

        if (
            "DOB" in upper
            or "DATE OF BIRTH" in upper
        ):

            for offset in [-2, -1, 1]:

                index = i + offset

                if 0 <= index < len(lines):

                    candidate = clean_name_candidate(
                        lines[index]
                    )

                    if is_possible_name(candidate):
                        candidates.append(candidate)

    # --------------------------------------------------------
    # 6. CLEAN + REMOVE DUPLICATES
    # --------------------------------------------------------

    cleaned_candidates = []

    for candidate in candidates:

        candidate = clean_name_candidate(
            candidate
        )

        if not candidate:
            continue

        candidate_upper = candidate.upper()

        if candidate_upper not in [
            item.upper()
            for item in cleaned_candidates
        ]:

            cleaned_candidates.append(candidate)

    # --------------------------------------------------------
    # 7. SCORE NAME CANDIDATES
    # --------------------------------------------------------

    scored_candidates = []

    for candidate in cleaned_candidates:

        score = 0

        words = candidate.split()

        # More realistic personal names
        if 2 <= len(words) <= 4:
            score += 30

        # Normal capitalization / alphabetic content
        if re.fullmatch(
            r"[A-Za-z]+(?:[ .'-][A-Za-z]+)*",
            candidate
        ):
            score += 20

        # Prefer names containing common name structure
        if len(candidate) >= 5:
            score += 10

        # Penalize very short candidates
        if len(candidate) < 4:
            score -= 20

        # Penalize OCR garbage
        garbage_words = [
            "OO",
            "XX",
            "TO",
            "S",
            "O",
            "ES",
            "IG",
            "BEE",
            "ARD",
            "WHS"
        ]

        for word in words:

            if word.upper() in garbage_words:
                score -= 15

        # Strong bonus for candidates found around
        # Aadhaar's "To" section
        for i, line in enumerate(lines):

            if line.strip().upper() == "TO":

                nearby = " ".join(
                    lines[
                        i + 1:min(i + 4, len(lines))
                    ]
                )

                if candidate.upper() in nearby.upper():
                    score += 40

        scored_candidates.append(
            {
                "name": candidate,
                "score": score
            }
        )

    # --------------------------------------------------------
    # 8. SELECT BEST CANDIDATE
    # --------------------------------------------------------

    if scored_candidates:

        scored_candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        best = scored_candidates[0]["name"]

        return clean_name_candidate(best)

    return "Not detected"


# ============================================================
# NAME CANDIDATE CLEANING
# ============================================================

def clean_name_candidate(value):

    if not value:
        return ""

    value = value.strip()

    # Remove common OCR symbols
    value = re.sub(
        r"[^A-Za-z .'\-]",
        " ",
        value
    )

    # Normalize whitespace
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    words = value.split()

    cleaned_words = []

    garbage_words = {
        "X",
        "XX",
        "O",
        "OO",
        "ES",
        "IG",
        "BEE",
        "ARD",
        "WHS",
        "V",
        "VV"
    }

    for word in words:

        if word.upper() in garbage_words:
            continue

        cleaned_words.append(word)

    return " ".join(cleaned_words).strip()
# ============================================================
# CLEAN NAME
# ============================================================

def clean_name(value):

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    value = value.replace(
        "<",
        " "
    )

    return value.strip()


# ============================================================
# NAME VALIDATION
# ============================================================

def is_possible_name(value):

    value = value.strip()


    if not value:
        return False


    if len(value) > 60:
        return False


    if any(
        char.isdigit()
        for char in value
    ):

        return False


    blocked_words = [

        "GOVERNMENT",
        "INDIA",
        "UNIQUE",
        "IDENTIFICATION",
        "AUTHORITY",
        "ENROLLMENT",
        "ADDRESS",
        "MALE",
        "FEMALE",
        "DATE",
        "ISSUE",
        "AADHAAR",
        "PASSPORT",
        "LICENSE",
        "LICENCE",
        "DOB",
        "YEAR",
        "BIRTH",
        "NATIONALITY",
        "VISA"

    ]


    upper_value = value.upper()


    for word in blocked_words:

        if word in upper_value:

            return False


    if not re.fullmatch(
        r"[A-Za-z][A-Za-z .'-]*",
        value
    ):

        return False


    return (
        1 <= len(value.split()) <= 6
    )


# ============================================================
# DATE OF BIRTH
# ============================================================

def extract_dob(
    text,
    mrz_data
):

    # --------------------------------------------------------
    # Passport MRZ
    # --------------------------------------------------------

    if mrz_data.get(
        "date_of_birth"
    ):

        return mrz_data[
            "date_of_birth"
        ]


    # --------------------------------------------------------
    # DOB label
    # --------------------------------------------------------

    dob_match = re.search(

        r"(DOB|DATE\s+OF\s+BIRTH|BIRTH)"
        r"[^\d]{0,30}"
        r"(\d{2}[\/\-.]\d{2}[\/\-.]\d{4})",

        text,

        re.IGNORECASE

    )


    if dob_match:

        return dob_match.group(2)


    # --------------------------------------------------------
    # General fallback
    # --------------------------------------------------------

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

def extract_document_number(
    text,
    document_type,
    mrz_data
):

    # --------------------------------------------------------
    # PASSPORT
    # --------------------------------------------------------

    if document_type == "Passport":

        if mrz_data.get(
            "passport_number"
        ):

            return mrz_data[
                "passport_number"
            ]


        passport_patterns = [

            r"\b[A-Z][0-9]{7}\b",

            r"\b[A-Z]{1,2}[0-9]{6,8}\b"

        ]


        for pattern in passport_patterns:

            match = re.search(
                pattern,
                text.upper()
            )


            if match:

                return match.group()


    # --------------------------------------------------------
    # AADHAAR
    # --------------------------------------------------------

    if document_type == "Aadhaar Card":

        patterns = [

            r"\b\d{4}\s\d{4}\s\d{4}\b",

            r"\b\d{4}-\d{4}-\d{4}\b",

            r"\b\d{12}\b"

        ]


        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )


            if match:

                number = re.sub(
                    r"[-\s]",
                    " ",
                    match.group()
                )

                return number.strip()


    # --------------------------------------------------------
    # DRIVING LICENCE
    # --------------------------------------------------------

    if document_type == "Driving Licence":

        patterns = [

            r"\b[A-Z]{2}[- ]?[0-9]{4,20}\b",

            r"\b[A-Z]{2}[0-9]{10,16}\b"

        ]


        for pattern in patterns:

            match = re.search(
                pattern,
                text.upper()
            )


            if match:

                return match.group()


    # --------------------------------------------------------
    # VISA
    # --------------------------------------------------------

    if document_type == "Visa":

        patterns = [

            r"(?:VISA\s*(?:NO|NUMBER|#)?|VISA\s*ID)"
            r"\s*[:\-]?\s*([A-Z0-9]{5,20})",

            r"(?:DOCUMENT\s*NO|REFERENCE\s*NO|APPLICATION\s*NO)"
            r"\s*[:\-]?\s*([A-Z0-9]{5,25})"

        ]


        for pattern in patterns:

            match = re.search(
                pattern,
                text.upper()
            )


            if match:

                return match.group(1)


    return "Not detected"


# ============================================================
# NATIONALITY
# ============================================================

def extract_nationality(
    text,
    document_type,
    mrz_data
):

    if mrz_data.get(
        "nationality"
    ):

        return mrz_data[
            "nationality"
        ]


    match = re.search(

        r"(?:NATIONALITY|NATION)"
        r"\s*[:\-]?\s*([A-Z]{2,30})",

        text.upper()

    )


    if match:

        return match.group(1)


    return "Not detected"


# ============================================================
# GENDER
# ============================================================

def extract_gender(
    text,
    mrz_data
):

    if mrz_data.get(
        "sex"
    ):

        return mrz_data[
            "sex"
        ]


    upper = text.upper()


    if "FEMALE" in upper:

        return "Female"


    if "MALE" in upper:

        return "Male"


    return "Not detected"


# ============================================================
# EXPIRY DATE
# ============================================================

def extract_expiry_date(
    text,
    document_type,
    mrz_data
):

    if mrz_data.get(
        "expiry_date"
    ):

        return mrz_data[
            "expiry_date"
        ]


    match = re.search(

        r"(?:EXPIRY|EXPIRATION|VALID\s*UNTIL|VALID\s*UPTO)"
        r"[^\d]{0,20}"
        r"(\d{2}[\/\-.]\d{2}[\/\-.]\d{4})",

        text,

        re.IGNORECASE

    )


    if match:

        return match.group(1)


    return "Not detected"


# ============================================================
# DOCUMENT VALIDATION
# ============================================================

# ============================================================
# IMPROVED DOCUMENT VALIDATION ENGINE
# ============================================================

def validate_document(
    document_type,
    name,
    dob,
    document_number,
    expiry_date,
    extracted_text,
    mrz_data
):

    checks = []
    score = 100

    text_upper = extracted_text.upper()

    # --------------------------------------------------------
    # HELPER
    # --------------------------------------------------------

    def add_check(check, status, message):
        checks.append({
            "check": check,
            "status": status,
            "message": message
        })

    # --------------------------------------------------------
    # 1. DOCUMENT CLASSIFICATION
    # --------------------------------------------------------

    if document_type != "Unknown":

        add_check(
            "Document Classification",
            "PASSED",
            f"{document_type} detected."
        )

    else:

        score -= 25

        add_check(
            "Document Classification",
            "FAILED",
            "Document type could not be confidently identified."
        )

    # --------------------------------------------------------
    # 2. NAME
    # --------------------------------------------------------

    if (
        name != "Not detected"
        and is_possible_name(name)
    ):

        add_check(
            "Name",
            "PASSED",
            f"Name detected: {name}."
        )

    else:

        score -= 15

        add_check(
            "Name",
            "WARNING",
            "A reliable name could not be extracted."
        )

    # --------------------------------------------------------
    # 3. DATE OF BIRTH
    # --------------------------------------------------------

    if dob != "Not detected":

        add_check(
            "Date of Birth",
            "PASSED",
            f"Date of birth detected: {dob}."
        )

    else:

        score -= 15

        add_check(
            "Date of Birth",
            "WARNING",
            "Date of birth could not be detected."
        )

    # --------------------------------------------------------
    # 4. DOCUMENT NUMBER
    # --------------------------------------------------------

    if document_number != "Not detected":

        add_check(
            "Document Number",
            "PASSED",
            "Document number detected."
        )

    else:

        score -= 20

        add_check(
            "Document Number",
            "FAILED",
            "Document number could not be detected."
        )

    # --------------------------------------------------------
    # 5. AADHAAR-SPECIFIC VALIDATION
    # --------------------------------------------------------

    if document_type == "Aadhaar Card":

        # --------------------------------------------
        # Aadhaar number format
        # --------------------------------------------

        aadhaar_digits = re.sub(
            r"\D",
            "",
            document_number
        )

        if len(aadhaar_digits) == 12:

            add_check(
                "Aadhaar Number Format",
                "PASSED",
                "A 12-digit Aadhaar-like number was detected."
            )

        else:

            score -= 15

            add_check(
                "Aadhaar Number Format",
                "WARNING",
                "Detected number does not match the basic 12-digit format."
            )

        # --------------------------------------------
        # Aadhaar text markers
        # --------------------------------------------

        aadhaar_markers = [
            "AADHAAR",
            "UNIQUE IDENTIFICATION",
            "UIDAI",
            "GOVERNMENT OF INDIA",
            "YOUR AADHAAR NO"
        ]

        marker_count = sum(
            1
            for marker in aadhaar_markers
            if marker in text_upper
        )

        if marker_count >= 2:

            add_check(
                "Aadhaar Text Markers",
                "PASSED",
                "Expected Aadhaar text markers were detected."
            )

        elif marker_count == 1:

            add_check(
                "Aadhaar Text Markers",
                "WARNING",
                "Only limited Aadhaar text markers were detected."
            )

            score -= 5

        else:

            add_check(
                "Aadhaar Text Markers",
                "WARNING",
                "Expected Aadhaar text markers were not confidently detected."
            )

            score -= 10

        # --------------------------------------------
        # DOB sanity
        # --------------------------------------------

        if dob != "Not detected":

            try:

                from datetime import datetime

                parsed_dob = None

                for fmt in (
                    "%d/%m/%Y",
                    "%d-%m-%Y",
                    "%d.%m.%Y"
                ):

                    try:

                        parsed_dob = datetime.strptime(
                            dob,
                            fmt
                        )

                        break

                    except ValueError:
                        continue

                if parsed_dob:

                    if parsed_dob <= datetime.now():

                        add_check(
                            "DOB Date Sanity",
                            "PASSED",
                            "Date of birth is a valid non-future calendar date."
                        )

                    else:

                        score -= 15

                        add_check(
                            "DOB Date Sanity",
                            "FAILED",
                            "Date of birth appears to be in the future."
                        )

                else:

                    score -= 5

                    add_check(
                        "DOB Date Sanity",
                        "WARNING",
                        "Date of birth format could not be fully validated."
                    )

            except Exception:

                add_check(
                    "DOB Date Sanity",
                    "WARNING",
                    "Date of birth sanity check could not be completed."
                )

    # --------------------------------------------------------
    # 6. PASSPORT-SPECIFIC VALIDATION
    # --------------------------------------------------------

    if document_type == "Passport":

        # --------------------------------------------
        # MRZ detection
        # --------------------------------------------

        if mrz_data.get("detected", False):

            add_check(
                "Passport MRZ",
                "PASSED",
                "Passport machine-readable zone detected."
            )

        else:

            score -= 15

            add_check(
                "Passport MRZ",
                "WARNING",
                "Passport MRZ could not be confidently detected."
            )

        # --------------------------------------------
        # Passport nationality
        # --------------------------------------------

        if mrz_data.get("nationality"):

            add_check(
                "Nationality",
                "PASSED",
                f"Nationality code detected: {mrz_data['nationality']}."
            )

        else:

            add_check(
                "Nationality",
                "WARNING",
                "Passport nationality could not be detected."
            )

        # --------------------------------------------
        # Passport expiry
        # --------------------------------------------

        if expiry_date != "Not detected":

            add_check(
                "Expiry Date",
                "PASSED",
                f"Expiry date detected: {expiry_date}."
            )

        else:

            score -= 10

            add_check(
                "Expiry Date",
                "WARNING",
                "Passport expiry date could not be detected."
            )

    # --------------------------------------------------------
    # 7. VISA VALIDATION
    # --------------------------------------------------------

    if document_type == "Visa":

        if expiry_date != "Not detected":

            add_check(
                "Expiry Date",
                "PASSED",
                f"Visa expiry date detected: {expiry_date}."
            )

        else:

            score -= 15

            add_check(
                "Expiry Date",
                "WARNING",
                "Visa expiry date could not be detected."
            )

    # --------------------------------------------------------
    # 8. DRIVING LICENCE VALIDATION
    # --------------------------------------------------------

    if document_type == "Driving Licence":

        if expiry_date != "Not detected":

            add_check(
                "Expiry Date",
                "PASSED",
                f"Licence expiry date detected: {expiry_date}."
            )

        else:

            score -= 15

            add_check(
                "Expiry Date",
                "WARNING",
                "Driving licence expiry date could not be detected."
            )

    # --------------------------------------------------------
    # 9. NATIONAL ID
    # --------------------------------------------------------

    if document_type == "National ID":

        if (
            "IDENTITY CARD" in text_upper
            or "NATIONAL ID" in text_upper
        ):

            add_check(
                "Identity Card Markers",
                "PASSED",
                "Identity-card markers detected."
            )

        else:

            score -= 5

            add_check(
                "Identity Card Markers",
                "WARNING",
                "Identity-card markers could not be confidently detected."
            )

    # --------------------------------------------------------
    # FINAL SCORE LIMIT
    # --------------------------------------------------------

    score = max(
        0,
        min(
            score,
            100
        )
    )

    risk_score = 100 - score

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if risk_score <= 20:

        risk_level = "LOW"
        status = "VALID"

        recommendation = (
            "Document passed preliminary automated "
            "document-structure screening."
        )

    elif risk_score <= 50:

        risk_level = "MEDIUM"
        status = "REVIEW"

        recommendation = (
            "Document requires additional manual "
            "verification by an authorized officer."
        )

    else:

        risk_level = "HIGH"
        status = "SUSPICIOUS"

        recommendation = (
            "Document contains indicators requiring "
            "further manual investigation."
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

def analyze_image(contents):

    try:

        # ----------------------------------------------------
        # Decode
        # ----------------------------------------------------

        image_array = np.frombuffer(
            contents,
            np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )


        if image is None:

            return {

                "status":
                    "UNABLE TO ANALYZE",

                "risk_level":
                    "MEDIUM",

                "tampering_score":
                    50,

                "image_quality":
                    "UNKNOWN",

                "checks": []

            }


        height, width = image.shape[:2]


        # ----------------------------------------------------
        # Resolution
        # ----------------------------------------------------

        if (
            width >= 500
            and height >= 500
        ):

            quality = "GOOD"

            quality_status = "PASSED"

            quality_message = (
                "Image resolution is suitable for analysis."
            )

        else:

            quality = "LOW"

            quality_status = "WARNING"

            quality_message = (
                "Image resolution may be too low "
                "for reliable analysis."
            )


        # ----------------------------------------------------
        # Sharpness
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


        sharpness = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()


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


        # ----------------------------------------------------
        # Structural Analysis
        # ----------------------------------------------------

        edges = cv2.Canny(
            gray,
            100,
            200
        )


        edge_density = np.mean(
            edges > 0
        )


        if edge_density < 0.35:

            structure_status = "PASSED"

            structure_message = (
                "No abnormal edge density detected."
            )

        else:

            structure_status = "WARNING"

            structure_message = (
                "Unusual edge density detected; "
                "manual review recommended."
            )


        # ----------------------------------------------------
        # Color Consistency
        # ----------------------------------------------------

        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2HSV
        )


        saturation_mean = np.mean(
            hsv[:, :, 1]
        )


        if (
            20 <= saturation_mean <= 230
        ):

            color_status = "PASSED"

            color_message = (
                "Color distribution appears consistent."
            )

        else:

            color_status = "WARNING"

            color_message = (
                "Unusual color distribution detected."
            )


        # ----------------------------------------------------
        # Tampering Score
        # ----------------------------------------------------

        warnings = 0


        if quality_status != "PASSED":
            warnings += 1


        if sharpness_status != "PASSED":
            warnings += 1


        if structure_status != "PASSED":
            warnings += 1


        if color_status != "PASSED":
            warnings += 1


        tampering_score = min(
            warnings * 20,
            100
        )


        # ----------------------------------------------------
        # Tampering Status
        # ----------------------------------------------------

        if tampering_score <= 20:

            tampering_status = (
                "NO OBVIOUS TAMPERING"
            )

            risk_level = "LOW"


        elif tampering_score <= 50:

            tampering_status = (
                "POSSIBLE TAMPERING"
            )

            risk_level = "MEDIUM"


        else:

            tampering_status = (
                "HIGH TAMPERING INDICATORS"
            )

            risk_level = "HIGH"


        return {

            "status":
                tampering_status,

            "risk_level":
                risk_level,

            "tampering_score":
                tampering_score,

            "image_quality":
                quality,

            "resolution": {

                "width":
                    width,

                "height":
                    height

            },

            "checks": [

                {

                    "check":
                        "Image Quality",

                    "status":
                        quality_status,

                    "message":
                        quality_message

                },

                {

                    "check":
                        "Image Sharpness",

                    "status":
                        sharpness_status,

                    "message":
                        sharpness_message

                },

                {

                    "check":
                        "Structural Analysis",

                    "status":
                        structure_status,

                    "message":
                        structure_message

                },

                {

                    "check":
                        "Color Consistency",

                    "status":
                        color_status,

                    "message":
                        color_message

                }

            ]

        }


    except Exception as e:

        return {

            "status":
                "ANALYSIS ERROR",

            "risk_level":
                "MEDIUM",

            "tampering_score":
                50,

            "error":
                str(e),

            "checks": []

        }


# ============================================================
# FACE DETECTION
# ============================================================

def detect_face(contents):

    try:

        # ----------------------------------------------------
        # Decode image
        # ----------------------------------------------------

        image_array = np.frombuffer(
            contents,
            np.uint8
        )


        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )


        if image is None:

            return {

                "status":
                    "UNABLE TO ANALYZE",

                "face_detected":
                    False,

                "face_count":
                    0,

                "face_quality":
                    "UNKNOWN",

                "risk_level":
                    "MEDIUM",

                "message":
                    "Unable to decode image."

            }


        # ----------------------------------------------------
        # Grayscale
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


        # Improve contrast
        gray = cv2.equalizeHist(
            gray
        )


        # ----------------------------------------------------
        # CHECK OUR LOCAL CASCADE FILE
        # ----------------------------------------------------

        if not os.path.exists(
            FACE_CASCADE_PATH
        ):

            return {

                "status":
                    "FACE DETECTOR FILE NOT FOUND",

                "face_detected":
                    False,

                "face_count":
                    0,

                "face_quality":
                    "UNKNOWN",

                "risk_level":
                    "MEDIUM",

                "message":
                    (
                        "Haar Cascade XML file was not found at: "
                        + FACE_CASCADE_PATH
                    )

            }


        # ----------------------------------------------------
        # LOAD CASCADE
        # ----------------------------------------------------

        face_cascade = cv2.CascadeClassifier(
            FACE_CASCADE_PATH
        )


        if face_cascade.empty():

            return {

                "status":
                    "FACE DETECTOR FAILED",

                "face_detected":
                    False,

                "face_count":
                    0,

                "face_quality":
                    "UNKNOWN",

                "risk_level":
                    "MEDIUM",

                "message":
                    "Unable to load Haar Cascade face detector."

            }


        # ----------------------------------------------------
        # DETECT FACES
        # ----------------------------------------------------

        faces = face_cascade.detectMultiScale(

            gray,

            scaleFactor=1.05,

            minNeighbors=5,

            minSize=(40, 40)

        )


        face_count = len(faces)


        # ----------------------------------------------------
        # NO FACE
        # ----------------------------------------------------

        if face_count == 0:

            return {

                "status":
                    "FACE NOT DETECTED",

                "face_detected":
                    False,

                "face_count":
                    0,

                "face_quality":
                    "NOT AVAILABLE",

                "risk_level":
                    "MEDIUM",

                "message":
                    "No clear face detected in the document image."

            }


        # ----------------------------------------------------
        # LARGEST FACE
        # ----------------------------------------------------

        largest_face = max(

            faces,

            key=lambda rect:
                rect[2] * rect[3]

        )


        x, y, w, h = largest_face


        # ----------------------------------------------------
        # FACE REGION
        # ----------------------------------------------------

        face_region = gray[
            y:y + h,
            x:x + w
        ]


        if face_region.size > 0:

            face_sharpness = cv2.Laplacian(
                face_region,
                cv2.CV_64F
            ).var()

        else:

            face_sharpness = 0


        # ----------------------------------------------------
        # FACE QUALITY
        # ----------------------------------------------------

        if face_sharpness >= 50:

            face_quality = "GOOD"

        else:

            face_quality = "LOW"


        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {

            "status":
                "FACE DETECTED",

            "face_detected":
                True,

            "face_count":
                face_count,

            "face_quality":
                face_quality,

            "risk_level":
                "LOW",

            "message":
                "Face successfully detected in document image.",

            "face_location": {

                "x":
                    int(x),

                "y":
                    int(y),

                "width":
                    int(w),

                "height":
                    int(h)

            }

        }


    except Exception as e:

        return {

            "status":
                "FACE ANALYSIS ERROR",

            "face_detected":
                False,

            "face_count":
                0,

            "face_quality":
                "UNKNOWN",

            "risk_level":
                "MEDIUM",

            "message":
                str(e)

        }


# ============================================================
# FINAL SECURITY ASSESSMENT
# ============================================================

def create_security_assessment(
    validation,
    image_analysis,
    face_analysis,
    ocr_confidence,
    document_type
):

    validation_risk = validation.get(
        "risk_score",
        50
    )


    tampering_risk = image_analysis.get(
        "tampering_score",
        50
    )


    # --------------------------------------------------------
    # OCR RISK
    # --------------------------------------------------------

    if ocr_confidence >= 80:

        ocr_risk = 0

    elif ocr_confidence >= 60:

        ocr_risk = 10

    elif ocr_confidence >= 40:

        ocr_risk = 20

    else:

        ocr_risk = 30


    # --------------------------------------------------------
    # FACE RISK
    # --------------------------------------------------------

    if face_analysis.get(
        "face_detected",
        False
    ):

        face_risk = 0

    else:

        face_risk = 25


    # --------------------------------------------------------
    # FINAL RISK
    # --------------------------------------------------------

    final_risk = int(

        (
            validation_risk
            + tampering_risk
            + ocr_risk
            + face_risk
        )
        /
        4

    )


    final_risk = max(
        0,
        min(
            final_risk,
            100
        )
    )


    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    if final_risk <= 20:

        status = "VERIFIED"

        risk_level = "LOW"

        recommendation = (
            "Document passed preliminary automated "
            "screening. No obvious tampering indicators "
            "were detected."
        )


    elif final_risk <= 50:

        status = "REVIEW"

        risk_level = "MEDIUM"

        recommendation = (
            "Document requires additional manual "
            "verification by an officer."
        )


    else:

        status = "HIGH RISK"

        risk_level = "HIGH"

        recommendation = (
            "Document contains indicators requiring "
            "immediate manual investigation."
        )


    return {

        "status":
            status,

        "risk_level":
            risk_level,

        "risk_score":
            final_risk,

        "recommendation":
            recommendation,

        "components": {

            "validation_risk":
                validation_risk,

            "tampering_risk":
                tampering_risk,

            "ocr_risk":
                ocr_risk,

            "face_risk":
                face_risk

        }

    }