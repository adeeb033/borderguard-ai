from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from verification_api import (
    router as verification_router,
    compare_document_data
)
from face_verification import router as face_verification_router
from forensic_analysis import perform_forensic_analysis

from PIL import Image, ImageOps, ImageFilter

import pytesseract
import io
import re
import cv2
import numpy as np
import os
import httpx
import uuid

from psycopg2.extras import Json

try:
    from backend.database import get_db_connection
except ImportError:
    from database import get_db_connection



def get_history_db_connection():
    return get_db_connection()


def save_screening_history(
    screening_id,
    filename,
    applicant_name,
    document_type,
    risk_score,
    risk_level,
    status,
    ocr_confidence,
    validation_score,
    tampering_score,
    face_detected,
    risk_reasons
):
    conn = get_history_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO public.screening_history (
            screening_id,
            filename,
            applicant_name,
            document_type,
            risk_score,
            risk_level,
            status,
            review_status,
            officer_notes,
            reviewed_at,
            ocr_confidence,
            validation_score,
            tampering_score,
            face_detected,
            risk_reasons
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            'PENDING',
            NULL,
            NULL,
            %s, %s, %s, %s, %s
        )
        """,
        (
            screening_id,
            filename,
            applicant_name,
            document_type,
            risk_score,
            risk_level,
            status,
            ocr_confidence,
            validation_score,
            tampering_score,
            face_detected,
            Json(risk_reasons)
        )
    )

    conn.commit()

    cursor.close()
    conn.close()    
    
    
def save_security_alert(
    screening_id,
    filename,
    applicant_name,
    document_type,
    risk_score,
    risk_level,
    alert_type,
    description
):
    conn = get_history_db_connection()
    cursor = conn.cursor()

    alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"

    cursor.execute(
        """
        INSERT INTO public.security_alerts (
            alert_id,
            screening_id,
            filename,
            applicant_name,
            document_type,
            risk_score,
            risk_level,
            alert_type,
            description,
            status
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, 'OPEN'
        )
        """,
        (
            alert_id,
            screening_id,
            filename,
            applicant_name,
            document_type,
            risk_score,
            risk_level,
            alert_type,
            description
        )
    )

    conn.commit()

    cursor.close()
    conn.close()   


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="BorderGuard AI API",
    description="AI-powered border document screening backend",
    version="2.0.0"
)
app.include_router(verification_router)
app.include_router(face_verification_router)


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

    temp_image_path = os.path.join(
        os.path.dirname(__file__),
        "temp_forensic_image.jpg"
    )

    with open(temp_image_path, "wb") as temp_file:
        temp_file.write(contents)

    try:
        # ----------------------------------------------------
        # OPEN IMAGE
        # ----------------------------------------------------

        image = Image.open(
            io.BytesIO(contents)
        )
        print("\n========== FILE DEBUG ==========")
        print("Filename:", file.filename)
        print("Image size:", image.size)
        print("========== END FILE DEBUG ==========\n")

        if image.mode != "RGB":
            image = image.convert("RGB")

        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        ocr_result = perform_strong_ocr(image)

        extracted_text = ocr_result["text"]

        raw_ocr_text = ocr_result.get(
            "raw_text",
            extracted_text
        )

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

        visa_type = extract_visa_type(
            extracted_text,
            document_type
        )

        entry_validation = validate_visa_entry(
            extracted_text,
            document_type
        )

        stay_duration = extract_stay_duration(
            extracted_text,
            document_type
        )

        expiry_date = extract_expiry_date(
            extracted_text,
            document_type,
            mrz_data,
            image
        )

        # ----------------------------------------------------
        # VERIFICATION DATA
        # ----------------------------------------------------

        verification_data = {
            "document_number": document_number,
            "full_name": name,
            "date_of_birth": dob,
            "nationality": nationality,
            "expiry_date": expiry_date
        }

        # ----------------------------------------------------
        # REFERENCE VERIFICATION
        # ----------------------------------------------------

        verification_result = {
            "status": "NOT CHECKED"
        }

        if document_number:
            async with httpx.AsyncClient() as client:
                verification_response = await client.get(
                    f"http://127.0.0.1:8000/verification/check/{document_number}",
                    timeout=5
                )

            if verification_response.status_code == 200:
                verification_result = verification_response.json()

                # ------------------------------------------------
                # FIELD-BY-FIELD COMPARISON
                # ------------------------------------------------

                if verification_result.get("found"):
                    reference_data = verification_result.get(
                        "reference_data",
                        {}
                    )

                    comparison = compare_document_data(
                        verification_data,
                        reference_data
                    )

                    verification_result["comparison"] = comparison

            else:
                verification_result = {
                    "status": "VERIFICATION API ERROR",
                    "message": (
                        f"Verification API returned "
                        f"status {verification_response.status_code}"
                    )
                }

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
        
        print("========== VALIDATION DEBUG ==========")
        print(validation)
        print("========== END VALIDATION DEBUG ==========")

        # ----------------------------------------------------
        # IMAGE ANALYSIS
        # ----------------------------------------------------

        image_analysis = analyze_image(
            contents
        )

        # ----------------------------------------------------
        # ADVANCED FORENSIC ANALYSIS
        # ----------------------------------------------------

        forensic_analysis = perform_forensic_analysis(
            temp_image_path
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
            document_type,
            verification_result,
            forensic_analysis
        )
        
                # SAVE SCREENING HISTORY
        screening_id = f"SCR-{uuid.uuid4().hex[:8].upper()}"

        save_screening_history(
            screening_id=screening_id,
            filename=file.filename,
            applicant_name=name,
            document_type=document_type,
            risk_score=security_assessment.get("risk_score", 0),
            risk_level=security_assessment.get("risk_level", ""),
            status=security_assessment.get("status", ""),
            ocr_confidence=ocr_confidence,
            validation_score=validation.get("validation_score", 0),
            tampering_score=image_analysis.get("tampering_score", 0),
            face_detected=face_analysis.get("face_detected", False),
            risk_reasons=security_assessment.get("risk_reasons", [])
        )
        
        
                # ----------------------------------------------------
        # SAVE SECURITY ALERT
        # ----------------------------------------------------

        if (
            security_assessment.get("risk_level") in ["MEDIUM", "HIGH"]
            or security_assessment.get("status") in ["REVIEW", "HIGH RISK"]
        ):
            save_security_alert(
                screening_id=screening_id,
                filename=file.filename,
                applicant_name=name,
                document_type=document_type,
                risk_score=security_assessment.get("risk_score", 0),
                risk_level=security_assessment.get("risk_level", ""),
                alert_type="SCREENING RISK",
                description=(
                    "Security review required based on "
                    "the screening risk assessment."
                )
            )
        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        return {
            "success": True,
            "screening_id": screening_id,
            "filename": file.filename,
            "document_type": document_type,
            "ocr_confidence": ocr_confidence,
            "extracted_data": {
                "name": name,
                "date_of_birth": dob,
                "document_number": document_number,
                "nationality": nationality,
                "gender": gender,
                "expiry_date": expiry_date,
                "visa_type": visa_type,
                "entry_validation": entry_validation,
                "stay_duration": stay_duration
            },
            "mrz": mrz_data,
            "validation": validation,
            "image_analysis": image_analysis,
            "forensic_analysis": forensic_analysis,
            "face_analysis": face_analysis,
            "security_assessment": security_assessment,
            "verification": verification_result,
            "raw_text": raw_ocr_text,
            "message": (
                "Document successfully processed using "
                "enhanced OCR, forensic analysis, "
                "reference verification and face verification."
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
        # NORMALIZE IMAGE
        # ----------------------------------------------------

        image = ImageOps.exif_transpose(image)

        if image.mode != "RGB":
            image = image.convert("RGB")

        width, height = image.size

        # ----------------------------------------------------
        # GENERAL OCR
        # ----------------------------------------------------

        scale = 2

        upscaled = image.resize(
            (
                width * scale,
                height * scale
            ),
            Image.Resampling.LANCZOS
        )

        gray = ImageOps.grayscale(upscaled)
        gray = ImageOps.autocontrast(gray)

        sharp = gray.filter(
            ImageFilter.SHARPEN
        )

        general_text = pytesseract.image_to_string(
            sharp,
            config="--oem 3 --psm 6"
        )

        # ----------------------------------------------------
        # DEDICATED PASSPORT MRZ OCR
        # ----------------------------------------------------

        # Passport MRZ is located at the bottom of the page.
        mrz_top = int(height * 0.72)

        mrz = image.crop(
            (
                0,
                mrz_top,
                width,
                height
            )
        )

        # Make MRZ much larger
        mrz = mrz.resize(
            (
                mrz.width * 4,
                mrz.height * 4
            ),
            Image.Resampling.LANCZOS
        )

        mrz_gray = ImageOps.grayscale(mrz)
        mrz_gray = ImageOps.autocontrast(mrz_gray)

        mrz_sharp = mrz_gray.filter(
            ImageFilter.SHARPEN
        )

        mrz_np = np.array(mrz_sharp)

        # Threshold MRZ image
        _, mrz_binary = cv2.threshold(
            mrz_np,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        mrz_binary_image = Image.fromarray(
            mrz_binary
        )

        # MRZ contains only these characters
        mrz_config_6 = (
            "--oem 3 --psm 6 "
            "-c tessedit_char_whitelist="
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
        )

        mrz_config_7 = (
            "--oem 3 --psm 7 "
            "-c tessedit_char_whitelist="
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
        )

        mrz_text_1 = pytesseract.image_to_string(
            mrz_sharp,
            config=mrz_config_6
        )

        mrz_text_2 = pytesseract.image_to_string(
            mrz_binary_image,
            config=mrz_config_6
        )

        mrz_text_3 = pytesseract.image_to_string(
            mrz_binary_image,
            config=mrz_config_7
        )

        # ----------------------------------------------------
        # CLEAN MRZ
        # ----------------------------------------------------

        mrz_combined = (
            mrz_text_1
            + "\n"
            + mrz_text_2
            + "\n"
            + mrz_text_3
        )

        mrz_combined = mrz_combined.upper()

        mrz_lines = []

        for line in mrz_combined.splitlines():

            line = re.sub(
                r"[^A-Z0-9<]",
                "",
                line.upper()
            )

            if len(line) >= 15:
                mrz_lines.append(line)

        # ----------------------------------------------------
        # COMBINE OCR
        # ----------------------------------------------------

        combined_text = (
            general_text
            + "\n"
            + "\n".join(mrz_lines)
        )

        # Keep the original OCR text for display/debugging.
        raw_ocr_text = combined_text

        combined_text = clean_ocr_text(
            combined_text
        )

        # ----------------------------------------------------
        # DEBUG
        # ----------------------------------------------------

        print("\n========== OCR DEBUG ==========")
        print(combined_text)
        print("========== END OCR DEBUG ==========\n")

        # ----------------------------------------------------
        # CONFIDENCE
        # ----------------------------------------------------

        confidence = 0

        try:

            data = pytesseract.image_to_data(
                sharp,
                config="--oem 3 --psm 6",
                output_type=pytesseract.Output.DICT
            )

            values = []

            for conf in data["conf"]:

                try:

                    value = float(conf)

                    if value >= 0:
                        values.append(value)

                except Exception:
                    pass

            if values:
                confidence = sum(values) / len(values)

        except Exception:
            confidence = 0

        return {
            "text": combined_text,
            "raw_text": raw_ocr_text,
            "confidence": round(
                confidence,
                2
            ),
            "method": "general_plus_passport_mrz"
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
    print("\n🔥 DOCUMENT CLASSIFICATION TEXT:")
    print(text_upper)
    print("🔥 DRIVING LICENCE FOUND:", "DRIVING LICENCE" in text_upper)

    # --------------------------------------------------------
    # VISA
    # --------------------------------------------------------

    if (
        "VISA TYPE" in text_upper
        or "VISA TYPE / CLASS" in text_upper
        or "ISSUING POST NAME" in text_upper
        or "CONTROL NUMBER" in text_upper
        or "ENTRY PERMIT" in text_upper
    ):
        return "Visa"

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
        or re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text_upper)
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

        # Clean OCR lines
        lines = []

        for line in text.splitlines():
            cleaned = re.sub(
                r"[^A-Z0-9<]",
                "",
                line.upper()
            )

            if len(cleaned) >= 15:
                lines.append(cleaned)

        # ----------------------------------------------------
        # VISA MRZ DETECTION
        # ----------------------------------------------------

        visa_mrz_match = re.search(
            r"V[0-9]{7,8}<",
            text.upper()
        )

        if visa_mrz_match:

            visa_text = re.sub(
                r"[^A-Z0-9<]",
                "",
                text.upper()
            )

            visa_number_match = re.search(
                r"V[0-9]{7,8}<",
                visa_text
            )

            if visa_number_match:
                result["passport_number"] = (
                    visa_number_match.group(0)[:-1]
                )

            visa_data_match = re.search(
                r"V[0-9]{7,8}<"
                r"[0-9]{1,3}"
                r"([A-Z]{3})"
                r"(?:0O|O0|0)?"
                r"([0-9O]{6})"
                r"[0-9]"
                r"([MF])"
                r"([0-9O]{6})",
                visa_text
            )

            if visa_data_match:
                result["nationality"] = visa_data_match.group(1)

                raw_dob = (
                    visa_data_match.group(2)
                    .replace("O", "0")
                )

                result["date_of_birth"] = convert_mrz_date(raw_dob)
                result["sex"] = visa_data_match.group(3)

                raw_expiry = (
                    visa_data_match.group(4)
                    .replace("O", "0")
                )

                result["expiry_date"] = convert_mrz_date(raw_expiry)
                result["detected"] = True

            if result["passport_number"]:
                result["detected"] = True

            return result

        mrz_start = None

        for index, line in enumerate(lines):
            if (
                line.startswith("P<")
                and len(line) >= 20
            ):
                mrz_start = index
                break

        if mrz_start is None:
            for index, line in enumerate(lines):
                if len(line) >= 30 and "<<" in line:
                    mrz_start = index
                    break

        if mrz_start is None or mrz_start + 1 >= len(lines):

            # ----------------------------------------------------
            # VISA MRZ FALLBACK
            # ----------------------------------------------------
            # Some visa documents contain passport-style
            # information in a shorter / OCR-distorted MRZ.
            #
            # Example OCR:
            # V12345678<5INDO706032M2703108...
            # ----------------------------------------------------

            visa_text = text.upper()
            visa_text = re.sub(r"[^A-Z0-9<]", "", visa_text)

            print("DEBUG CLEAN VISA MRZ TEXT:", repr(visa_text))

            visa_number_match = re.search(
                r"\b(V[0-9]{7,8})<",
                visa_text
            )

            if visa_number_match:
                result["passport_number"] = visa_number_match.group(1)

            visa_data_match = re.search(
                r"V[0-9]{7,8}<"
                r"[0-9]{1,3}"
                r"([A-Z]{3})"
                r"(?:0O|O0|0)?"
                r"([0-9O]{6})"
                r"[0-9]"
                r"([MF])"
                r"([0-9O]{6})",
                visa_text
            )

            if visa_data_match:
                nationality = visa_data_match.group(1)

                raw_dob = (
                    visa_data_match.group(2)
                    .replace("O", "0")
                )

                sex = visa_data_match.group(3)

                raw_expiry = (
                    visa_data_match.group(4)
                    .replace("O", "0")
                )

                result["nationality"] = nationality
                result["date_of_birth"] = convert_mrz_date(raw_dob)
                result["sex"] = sex
                result["expiry_date"] = convert_mrz_date(raw_expiry)

            if (
                result["passport_number"]
                or result["nationality"]
                or result["date_of_birth"]
                or result["expiry_date"]
            ):
                result["detected"] = True
                return result

            return result

        line1 = lines[mrz_start].replace(" ", "")
        line2 = lines[mrz_start + 1].replace(" ", "")

        if line1.startswith("P<"):
            result["document_code"] = "P"

        if len(line1) >= 5:
            result["issuing_country"] = line1[2:5].replace("<", "")

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        if len(line1) > 5:
            name_part = line1[5:]
            name_parts = name_part.split("<<")

            if len(name_parts) >= 1:
                surname = (
                    name_parts[0]
                    .replace("<", " ")
                    .strip()
                )

                if surname:
                    result["surname"] = clean_name(surname)

            if len(name_parts) >= 2:
                given_names = (
                    name_parts[1]
                    .replace("<", " ")
                    .strip()
                )

                if given_names:
                    result["given_names"] = clean_name(given_names)

        # ----------------------------------------------------
        # SECOND MRZ LINE
        # ----------------------------------------------------

        # Passport MRZ normally has 44 characters.
        # Allow slightly shorter OCR output.
        if len(line2) >= 30:

            # Passport number
            passport_number = line2[0:9]
            passport_number = (
                passport_number
                .replace("<", "")
                .strip()
            )

            if passport_number:
                # OCR commonly confuses Z with 7
                # in passport numbers.
                if re.fullmatch(
                    r"7[A-Z0-9]{7}",
                    passport_number
                ):
                    passport_number = (
                        "Z" + passport_number[1:]
                    )

                result["passport_number"] = passport_number

            # Nationality
            if len(line2) >= 13:
                nationality = line2[10:13]
                nationality = (
                    nationality
                    .replace("<", "")
                    .strip()
                )

                if nationality:
                    nationality = nationality.upper().strip()

                    if nationality in ["1ND", "91N", "91ND"]:
                        nationality = "IND"

                    result["nationality"] = nationality

            # Date of birth
            if len(line2) >= 19:
                raw_dob = line2[13:19]
                result["date_of_birth"] = convert_mrz_date(raw_dob)

            # Sex
            if len(line2) >= 21:
                sex = line2[20:21]

                if sex in ["M", "F"]:
                    result["sex"] = sex

            # Expiry date
            if len(line2) >= 27:
                raw_expiry = line2[21:27]
                result["expiry_date"] = convert_mrz_date(raw_expiry)

            # We have successfully found
            # passport-style MRZ data
            if (
                result["passport_number"]
                or result["nationality"]
                or result["date_of_birth"]
            ):
                result["detected"] = True

    except Exception as e:
        print(
            "MRZ parsing error:",
            str(e)
        )
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

    # MRZ uses two-digit years.
    # For this prototype, treat 00-30 as 2000-2030
    # and 31-99 as 2031-2099.
    full_year = 2000 + year

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

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # ---------------------------------------------------------
    # 1. PASSPORT NAME
    # ---------------------------------------------------------
    if document_type == "Passport":

        surname = mrz_data.get("surname")
        given_names = mrz_data.get("given_names")

        if surname and given_names:
            return clean_name_candidate(
                f"{given_names} {surname}"
            )

        if surname:
            return clean_name_candidate(surname)

    # ---------------------------------------------------------
    # 2. VISA NAME
    # ---------------------------------------------------------
    if document_type == "Visa":

        # ---------------------------------------------------------
        # VISA NAME EXTRACTION
        # Priority:
        # 1. MRZ
        # 2. Surname + Given Name fields
        # 3. Normal name labels
        # 4. Existing contextual fallback
        # ---------------------------------------------------------

        # 1. Try extracting the name from the MRZ first.
        # Example:
        # VISAUSADUSSA<<SAI<SUJEETH<<<<<<<<<<<<<<<<<<<<<
        #
        # Expected result:
        # SAI SUJEETH DUSSA

        for line in lines:
            upper_line = line.upper().strip()

            if "<<" in upper_line and upper_line.startswith("VISA"):
                mrz_line = upper_line

                try:
                    # Everything before << contains:
                    # VISA + country code + surname
                    name_parts = mrz_line.split("<<", 1)

                    if len(name_parts) == 2:
                        first_part = name_parts[0]
                        second_part = name_parts[1]

                        # Remove the VISA prefix.
                        # Example:
                        # VISAUSADUSSA
                        #      USA = issuing country
                        #          DUSSA = surname
                        if first_part.startswith("VISA"):
                            first_part = first_part[4:]

                        # Remove the 3-letter issuing country code.
                        if len(first_part) > 3:
                            surname_section = first_part[3:]
                        else:
                            surname_section = ""

                        # Convert MRZ < separators into spaces.
                        given_section = second_part.replace("<", " ")

                        surname = clean_name_candidate(
                            surname_section
                        )

                        given_name = clean_name_candidate(
                            given_section
                        )

                        # Remove anything after filler spaces.
                        given_name = " ".join(
                            given_name.split()
                        )

                        if (
                            is_possible_name(surname)
                            and is_possible_name(given_name)
                        ):
                            return f"{given_name} {surname}".strip()

                except Exception:
                    pass

        # 2. Look specifically for Surname and Given Name fields.
        surname = ""
        given_name = ""

        for i, line in enumerate(lines):
            upper_line = line.upper().strip()

            # Surname
            if "SURNAME" in upper_line:
                parts = re.split(
                    r"[:\-]",
                    line,
                    maxsplit=1
                )

                if len(parts) > 1:
                    candidate = clean_name_candidate(parts[1])

                    if is_possible_name(candidate):
                        surname = candidate

                elif i + 1 < len(lines):
                    candidate = clean_name_candidate(
                        lines[i + 1]
                    )

                    if is_possible_name(candidate):
                        surname = candidate

            # Given Name / Given Names
            if (
                "GIVEN NAME" in upper_line
                or "GIVEN NAMES" in upper_line
                or "GIVENNAME" in upper_line
            ):
                parts = re.split(
                    r"[:\-]",
                    line,
                    maxsplit=1
                )

                if len(parts) > 1:
                    candidate = clean_name_candidate(parts[1])

                    # Reject lines containing visa metadata
                    metadata_words = [
                        "B1",
                        "B2",
                        "VISA",
                        "TYPE",
                        "CLASS",
                        "ENTRY",
                        "PASSPORT",
                        "SEX",
                        "NATIONALITY"
                    ]

                    if (
                        is_possible_name(candidate)
                        and not any(
                            word in candidate.upper()
                            for word in metadata_words
                        )
                    ):
                        given_name = candidate

                elif i + 1 < len(lines):
                    candidate = clean_name_candidate(
                        lines[i + 1]
                    )

                    metadata_words = [
                        "B1",
                        "B2",
                        "VISA",
                        "TYPE",
                        "CLASS",
                        "ENTRY",
                        "PASSPORT",
                        "SEX",
                        "NATIONALITY"
                    ]

                    if (
                        is_possible_name(candidate)
                        and not any(
                            word in candidate.upper()
                            for word in metadata_words
                        )
                    ):
                        given_name = candidate

        if given_name and surname:
            return f"{given_name} {surname}".strip()

        if given_name:
            return given_name

        if surname:
            return surname

        # 3. Normal Visa name labels
        visa_name_labels = [
            "APPLICANT NAME",
            "NAME OF APPLICANT",
            "FULL NAME",
            "NAME"
        ]

        for i, line in enumerate(lines):
            upper_line = line.upper().strip()

            for label in visa_name_labels:
                if upper_line.startswith(label):
                    parts = re.split(
                        r"[:\-]",
                        line,
                        maxsplit=1
                    )

                    if len(parts) > 1:
                        candidate = clean_name_candidate(
                            parts[1]
                        )

                        if is_possible_name(candidate):
                            return candidate

                    if i + 1 < len(lines):
                        candidate = clean_name_candidate(
                            lines[i + 1]
                        )

                        if is_possible_name(candidate):
                            return candidate

        # 4. Secondary Visa fallback
        visa_context_words = [
            "VISA",
            "APPLICANT",
            "ENTRY",
            "PERMIT"
        ]

        for i, line in enumerate(lines):
            upper_line = line.upper()

            if any(
                word in upper_line
                for word in visa_context_words
            ):
                for offset in range(1, 4):
                    index = i + offset

                    if index >= len(lines):
                        break

                    candidate = clean_name_candidate(
                        lines[index]
                    )

                    if is_possible_name(candidate):
                        return candidate

    # ---------------------------------------------------------
    # 3. AADHAAR NAME
    # ---------------------------------------------------------
    if document_type == "Aadhaar Card":

        aadhaar_candidates = []

        # Aadhaar OCR commonly contains the person's name
        # after the "To" section.
        for i, line in enumerate(lines):

            if line.strip().upper() == "TO":

                # Look at the next few OCR lines.
                for offset in range(1, 5):

                    index = i + offset

                    if index >= len(lines):
                        break

                    candidate = clean_name_candidate(
                        lines[index]
                    )

                    if not candidate:
                        continue

                    upper_candidate = candidate.upper()

                    # Ignore obvious address/relationship lines.
                    ignored_words = [
                        "S/O",
                        "D/O",
                        "W/O",
                        "C/O",
                        "DOB",
                        "DATE OF BIRTH",
                        "GOVERNMENT",
                        "INDIA",
                        "UNIQUE",
                        "IDENTIFICATION",
                        "AUTHORITY",
                        "ENROLLMENT",
                        "AADHAAR",
                        "MOBILE",
                        "PIN",
                        "CODE",
                        "DISTRICT",
                        "STATE",
                        "VTC",
                        "SUB DISTRICT"
                    ]

                    if any(
                        word in upper_candidate
                        for word in ignored_words
                    ):
                        continue

                    if is_possible_name(candidate):

                        score = 0

                        # Prefer names containing at least
                        # two normal alphabetic words.
                        words = candidate.split()

                        if 2 <= len(words) <= 4:
                            score += 30

                        if all(
                            re.fullmatch(
                                r"[A-Za-z]+",
                                word
                            )
                            for word in words
                        ):
                            score += 30

                        if len(candidate) >= 8:
                            score += 10

                        # Strong preference for common
                        # Aadhaar name structure.
                        if any(
                            word.upper() in [
                                "MOHD",
                                "MOHAMMED",
                                "MUHAMMAD"
                            ]
                            for word in words
                        ):
                            score += 20

                        aadhaar_candidates.append(
                            {
                                "name": candidate,
                                "score": score
                            }
                        )

        # -----------------------------------------------------
        # 3. Prefer names found near "Faye" / OCR variations
        # -----------------------------------------------------
        for line in lines:

            candidate = clean_name_candidate(line)

            if not candidate:
                continue

            upper_candidate = candidate.upper()

            # OCR may produce "Faye Mohd Adeeb".
            # Remove common OCR prefix if present.
            if upper_candidate.startswith("FAYE "):

                possible = candidate[5:].strip()

                if is_possible_name(possible):

                    aadhaar_candidates.append(
                        {
                            "name": possible,
                            "score": 100
                        }
                    )

        # -----------------------------------------------------
        # 4. Look near DOB as a secondary method
        # -----------------------------------------------------
        for i, line in enumerate(lines):

            upper = line.upper()

            if (
                "DOB" in upper
                or "DATE OF BIRTH" in upper
            ):

                for offset in [-2, -1]:

                    index = i + offset

                    if index < 0:
                        continue

                    candidate = clean_name_candidate(
                        lines[index]
                    )

                    if is_possible_name(candidate):

                        aadhaar_candidates.append(
                            {
                                "name": candidate,
                                "score": 40
                            }
                        )

        # -----------------------------------------------------
        # 5. Remove duplicates
        # -----------------------------------------------------
        unique_candidates = {}

        for item in aadhaar_candidates:

            name = clean_name_candidate(
                item["name"]
            )

            if not name:
                continue

            key = name.upper()

            if (
                key not in unique_candidates
                or item["score"]
                > unique_candidates[key]["score"]
            ):
                unique_candidates[key] = {
                    "name": name,
                    "score": item["score"]
                }

        # -----------------------------------------------------
        # 6. Select highest-confidence Aadhaar name
        # -----------------------------------------------------
        if unique_candidates:

            best = max(
                unique_candidates.values(),
                key=lambda item: item["score"]
            )

            return clean_name_candidate(
                best["name"]
            )

    # ---------------------------------------------------------
    # 7. GENERIC NAME LABEL
    # ---------------------------------------------------------
    for i, line in enumerate(lines):

        upper = line.upper()

        if re.search(
            r"\b(NAME|FULL NAME)\b",
            upper
        ):

            parts = re.split(
                r"[:\-]",
                line,
                maxsplit=1
            )

            if len(parts) > 1:

                candidate = parts[1].strip()

                # Remove common text that appears after the person's name
                # on Driving Licence OCR.
                candidate = re.split(
                    r"\bHOLDER'?S\s+SIGNATURE\b",
                    candidate,
                    maxsplit=1,
                    flags=re.IGNORECASE
                )[0].strip()

                candidate = clean_name_candidate(candidate)

                if is_possible_name(candidate):
                    return candidate

            if i + 1 < len(lines):

                candidate = clean_name_candidate(
                    lines[i + 1]
                )

                if is_possible_name(candidate):
                    return candidate

    # ---------------------------------------------------------
    # 8. FINAL FALLBACK
    # ---------------------------------------------------------
    for line in lines:

        candidate = clean_name_candidate(line)

        if is_possible_name(candidate):

            return candidate

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
    # Passport / existing MRZ data
    # --------------------------------------------------------

    if mrz_data.get(
        "date_of_birth"
    ):
        return mrz_data[
            "date_of_birth"
        ]

    # --------------------------------------------------------
    # Visa MRZ fallback
    #
    # Example:
    # V12345678<5INDO706032M2703108...
    #
    # 070603 = YYMMDD = 2007-06-03
    # --------------------------------------------------------

    visa_mrz_match = re.search(
        r"[A-Z][0-9]{7,8}<\d[A-Z]{3}(\d{6})[MF]",
        text.upper()
    )

    if visa_mrz_match:

        raw_dob = visa_mrz_match.group(1)

        yy = raw_dob[0:2]
        mm = raw_dob[2:4]
        dd = raw_dob[4:6]

        year = int(yy)

        if year <= 30:
            year += 2000
        else:
            year += 1900

        return f"{dd}/{mm}/{year}"

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

        passport_number = mrz_data.get(
            "passport_number"
        )

        if passport_number:
            passport_number = passport_number.upper().strip()

            # OCR commonly confuses Z with 7 in passport numbers
            # when the MRZ starts with Z followed by digits.
            if re.fullmatch(
                r"7[A-Z0-9]{7}",
                passport_number
            ):
                passport_number = "Z" + passport_number[1:]

            return passport_number

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

        text_upper = text.upper()

        patterns = [
            r"\b[A-Z]{2}[- ]?[0-9]{4,20}\b",
            r"\b[A-Z]{2}[0-9]{10,16}\b"
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                text_upper
            )

            if match:
                return match.group()

        # OCR may confuse the first letter T with the digit 1
        match = re.search(
            r"\b1G[0-9]{12,16}\b",
            text_upper
        )

        if match:
            return "T" + match.group()[1:]

    # --------------------------------------------------------
    # VISA
    # --------------------------------------------------------

    if document_type == "Visa":

        # ---------------------------------------------------------
        # VISA MRZ DOCUMENT / PASSPORT NUMBER
        # Example:
        # V12345678<5INDO706032M2703108...
        # ---------------------------------------------------------

        mrz_match = re.search(
            r"\b([A-Z][0-9]{7,8})<[0-9]",
            text.upper()
        )

        if mrz_match:
            return mrz_match.group(1)

        # ---------------------------------------------------------
        # VISA NORMAL OCR FALLBACK
        # ---------------------------------------------------------

        patterns = [
            r"(?:PASSPORT\s*(?:NO|NUMBER|#)?|"
            r"PASSPORT\s*NO)"
            r"\s*[:\-]?\s*([A-Z0-9]{5,20})",

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

        nationality = mrz_data[
            "nationality"
        ].upper().strip()

        # OCR commonly confuses I with 1
        # in MRZ nationality codes.
        if nationality == "1ND":
            nationality = "IND"

        return nationality

    match = re.search(
        r"(?:NATIONALITY|NATION)"
        r"\s*[:\-]?\s*([A-Z]{2,30})",
        text.upper()
    )

    if match:
        nationality = match.group(1)

        if nationality == "1ND":
            nationality = "IND"

        return nationality

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
    mrz_data,
    image=None
):
    # ----------------------------------------------------
    # PASSPORT MRZ EXPIRY
    # ----------------------------------------------------

    if document_type == "Passport":

        # First use the MRZ data if it contains
        # a valid expiry date.
        mrz_expiry = mrz_data.get("expiry_date")

        if mrz_expiry:
            return mrz_expiry

        # ------------------------------------------------
        # FALLBACK: READ PASSPORT MRZ DIRECTLY
        # ------------------------------------------------

        passport_text = re.sub(
            r"\s+",
            "",
            text.upper()
        )

        passport_mrz_match = re.search(
            r"P[0-9A-Z]{8}<"
            r"\d?[A-Z0-9]{3}"
            r"\d{6}"
            r"\d"
            r"[MF]"
            r"(\d{6})",
            passport_text
        )

        if passport_mrz_match:

            raw_expiry = passport_mrz_match.group(1)

            converted_expiry = convert_mrz_date(
                raw_expiry
            )

            if converted_expiry:
                return converted_expiry

    # ----------------------------------------------------
    # DRIVING LICENCE EXPIRY
    # ----------------------------------------------------

    if document_type == "Driving Licence" and image is not None:

        image_array = (
            np.array(image.convert("RGB"))
            if hasattr(image, "convert")
            else image
        )

        if len(image_array.shape) == 3:

            height, width = image_array.shape[:2]

            roi = image_array[
                int(height * 0.30):int(height * 0.45),
                int(width * 0.43):int(width * 0.62)
            ]

            gray = cv2.cvtColor(
                roi,
                cv2.COLOR_RGB2GRAY
            )

            gray = cv2.resize(
                gray,
                None,
                fx=2,
                fy=2,
                interpolation=cv2.INTER_CUBIC
            )

            expiry_ocr = pytesseract.image_to_string(
                gray,
                config="--psm 6"
            )

            print(
                "\n========== DL EXPIRY OCR =========="
            )

            print(expiry_ocr)

            print(
                "========== END DL EXPIRY OCR ==========\n"
            )

            date_matches = re.findall(
                r"\d{2}[-/.]\d{2}[-/.]\d{4}",
                expiry_ocr
            )

            if date_matches:

                print(
                    "DL DATE CANDIDATES:",
                    date_matches
                )

                return date_matches[-1]

    # ----------------------------------------------------
    # GENERIC EXPIRY DATE
    # ----------------------------------------------------

    expiry_match = re.search(
        r"(?:EXPIRY|EXPIRATION|VALID\s*UNTIL|VALID\s*UPTO)"
        r"[^\d]{0,20}"
        r"(\d{2}[/\-.]\d{2}[/\-.]\d{4})",
        text,
        re.IGNORECASE
    )

    if expiry_match:
        return expiry_match.group(1)

    return "Not detected"

def validate_visa_entry(text, document_type):
    if document_type != "Visa":
        return "Not applicable"

    text_upper = text.upper()

    if "SINGLE ENTRY" in text_upper:
        return "SINGLE ENTRY"

    if "DOUBLE ENTRY" in text_upper:
        return "DOUBLE ENTRY"

    if "MULTIPLE ENTRY" in text_upper:
        return "MULTIPLE ENTRY"

    if "MULTIPLE ENTRIES" in text_upper:
        return "MULTIPLE ENTRY"

    return "Not detected"
def extract_visa_type(text, document_type):
    if document_type != "Visa":
        return "Not applicable"

    text_upper = text.upper()

    # Common Visa Type values
    if "TOURIST" in text_upper:
        return "TOURIST"
    
    if "B1/B2" in text_upper or "B1B2" in text_upper:
        return "TOURIST"

    if "BUSINESS" in text_upper:
        return "BUSINESS"

    if "STUDENT" in text_upper:
        return "STUDENT"

    if "WORK" in text_upper:
        return "WORK"

    match = re.search(
        r"(?:VISA\s*TYPE|TYPE\s*OF\s*VISA|VISA\s*CLASS)"
        r"\s*(?:/\s*CLASS)?\s*[:\-]?\s*([A-Z][A-Z ]{1,30})",
        text_upper
    )

    if match:
        return match.group(1).strip()

    return "Not detected"
def extract_stay_duration(text, document_type):
    if document_type != "Visa":
        return "Not applicable"

    text_upper = text.upper()

    # Direct duration detection
    match = re.search(
        r"([0-9]{1,3})\s*(DAYS?|MONTHS?|YEARS?)",
        text_upper
    )

    if match:
        return f"{match.group(1)} {match.group(2)}"

    # Common Visa duration labels
    match = re.search(
        r"(?:STAY\s*DURATION|DURATION\s*OF\s*STAY|"
        r"PERMITTED\s*STAY|LENGTH\s*OF\s*STAY)"
        r"\s*[:\-]?\s*([0-9]{1,3}\s*(?:DAYS?|MONTHS?|YEARS?))",
        text_upper
    )

    if match:
        return match.group(1).strip()

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
        # Passport expiry validation
        # --------------------------------------------

        if expiry_date != "Not detected":

            try:

                from datetime import datetime

                parsed_expiry = None

                for fmt in (
                    "%d/%m/%Y",
                    "%d-%m-%Y",
                    "%d.%m.%Y"
                ):

                    try:

                        parsed_expiry = datetime.strptime(
                            expiry_date,
                            fmt
                        )

                        break

                    except ValueError:

                        continue

                if parsed_expiry:

                    today = datetime.now()

                    if parsed_expiry.date() >= today.date():

                        add_check(
                            "Expiry Date",
                            "PASSED",
                            f"Passport expiry date is valid: {expiry_date}."
                        )

                    else:

                        score -= 25

                        add_check(
                            "Expiry Date",
                            "FAILED",
                            f"Passport appears to be expired: {expiry_date}."
                        )

                else:

                    score -= 5

                    add_check(
                        "Expiry Date",
                        "WARNING",
                        "Passport expiry date format could not be validated."
                    )

            except Exception:

                score -= 5

                add_check(
                    "Expiry Date",
                    "WARNING",
                    "Passport expiry date validation could not be completed."
                )

        else:

            score -= 10

            add_check(
                "Expiry Date",
                "WARNING",
                "Passport expiry date could not be detected."
            )
                    # --------------------------------------------
        # Passport MRZ cross-check
        # --------------------------------------------

        if mrz_data.get("detected", False):

            # ----------------------------------------
            # Passport number cross-check
            # ----------------------------------------

            mrz_passport_number = mrz_data.get(
                "passport_number"
            )

            if (
                mrz_passport_number
                and document_number != "Not detected"
            ):

                if (
                    document_number.upper().replace(" ", "")
                    ==
                    mrz_passport_number.upper().replace(" ", "")
                ):

                    add_check(
                        "Passport Number",
                        "PASSED",
                        "Passport number matches the MRZ."
                    )

                else:

                    score -= 20

                    add_check(
                        "Passport Number",
                        "FAILED",
                        "Passport number does not match the MRZ."
                    )

            # ----------------------------------------
            # DOB cross-check
            # ----------------------------------------

            mrz_dob = mrz_data.get(
                "date_of_birth"
            )

            if (
                mrz_dob
                and dob != "Not detected"
            ):

                if dob == mrz_dob:

                    add_check(
                        "Date of Birth",
                        "PASSED",
                        "Date of birth matches the passport MRZ."
                    )

                else:

                    score -= 20

                    add_check(
                        "Date of Birth",
                        "FAILED",
                        "Date of birth does not match the passport MRZ."
                    )

            # ----------------------------------------
            # Name cross-check
            # ----------------------------------------

            mrz_surname = mrz_data.get(
                "surname"
            )

            mrz_given_names = mrz_data.get(
                "given_names"
            )

            if (
                mrz_surname
                or mrz_given_names
            ):

                mrz_name_parts = []

                if mrz_given_names:
                    mrz_name_parts.append(
                        mrz_given_names
                    )

                if mrz_surname:
                    mrz_name_parts.append(
                        mrz_surname
                    )

                mrz_full_name = " ".join(
                    mrz_name_parts
                )

                normalized_name = re.sub(
                    r"[^A-Z]",
                    "",
                    name.upper()
                )

                normalized_mrz_name = re.sub(
                    r"[^A-Z]",
                    "",
                    mrz_full_name.upper()
                )

                if (
                    normalized_name
                    and normalized_mrz_name
                    and (
                        normalized_name
                        == normalized_mrz_name
                    )
                ):

                    add_check(
                        "Name",
                        "PASSED",
                        "Name matches the passport MRZ."
                    )

                else:

                    score -= 20

                    add_check(
                        "Name",
                        "FAILED",
                        "Name does not match the passport MRZ."
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
                "status": "UNABLE TO ANALYZE",
                "risk_level": "MEDIUM",
                "tampering_score": 50,
                "image_quality": "UNKNOWN",
                "checks": []
            }

        height, width = image.shape[:2]

        # ----------------------------------------------------
        # Resolution
        # ----------------------------------------------------

        if width >= 500 and height >= 500:

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

        if 20 <= saturation_mean <= 230:

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
        # Noise / Texture Consistency
        # ----------------------------------------------------

        blurred = cv2.GaussianBlur(
            gray,
            (5, 5),
            0
        )

        noise = cv2.absdiff(
            gray,
            blurred
        )

        noise_mean = np.mean(
            noise
        )

        if noise_mean <= 25:

            noise_status = "PASSED"

            noise_message = (
                "Image texture and noise appear consistent."
            )

        else:

            noise_status = "WARNING"

            noise_message = (
                "Unusual image texture or noise detected; "
                "manual review recommended."
            )

        # ----------------------------------------------------
        # Tampering Score
        # ----------------------------------------------------

        tampering_score = 0

        # Resolution
        if quality_status != "PASSED":

            tampering_score += 15

        # Sharpness is image quality,
        # not direct evidence of tampering.

        # Structure
        if structure_status != "PASSED":

            tampering_score += 25

        # Color
        if color_status != "PASSED":

            tampering_score += 20

        # Noise / texture
        if noise_status != "PASSED":

            tampering_score += 30

        # ----------------------------------------------------
        # Local Image Consistency
        # ----------------------------------------------------

        gray_float = gray.astype(
            np.float32
        )

        h, w = gray_float.shape

        top_left = gray_float[
            0:h // 2,
            0:w // 2
        ]

        top_right = gray_float[
            0:h // 2,
            w // 2:w
        ]

        bottom_left = gray_float[
            h // 2:h,
            0:w // 2
        ]

        bottom_right = gray_float[
            h // 2:h,
            w // 2:w
        ]
        print("🔥 LOCAL CONSISTENCY CODE REACHED 🔥")
        region_means = [

            np.mean(top_left),

            np.mean(top_right),

            np.mean(bottom_left),

            np.mean(bottom_right)

        ]

        local_difference = (
            max(region_means)
            - min(region_means)
        )

        print(
            "\n========== LOCAL CONSISTENCY DEBUG =========="
        )
        print(
            "Region means:",
            region_means
        )
        print(
            "Local difference:",
            local_difference
        )
        print(
            "=============================================\n"
        )

        if local_difference > 60:

            tampering_score += 20

            local_consistency_status = (
                "WARNING"
            )

            local_consistency_message = (
                "Unusual brightness variation detected "
                "between image regions; manual review recommended."
            )

        else:

            local_consistency_status = (
                "PASSED"
            )

            local_consistency_message = (
                "No significant regional brightness "
                "inconsistency detected."
            )

        # ----------------------------------------------------
        # Local Modification Detection
        # ----------------------------------------------------

        # Detect small areas whose color characteristics
        # differ strongly from their immediate surroundings.
        #
        # This is useful for detecting localized edits such
        # as a small colored mark added to an image.
        #
        # It is only a preliminary tampering indicator and
        # does not prove document forgery.

        saturation = hsv[:, :, 1].astype(
            np.float32
        )

        saturation_blur = cv2.GaussianBlur(
            saturation,
            (21, 21),
            0
        )

        saturation_difference = cv2.absdiff(
            saturation,
            saturation_blur
        )

        local_color_mask = (
            saturation_difference > 55
        ).astype(
            np.uint8
        ) * 255

        # Remove tiny isolated noise.
        kernel = np.ones(
            (5, 5),
            np.uint8
        )

        local_color_mask = cv2.morphologyEx(
            local_color_mask,
            cv2.MORPH_OPEN,
            kernel
        )

        local_color_mask = cv2.morphologyEx(
            local_color_mask,
            cv2.MORPH_CLOSE,
            kernel
        )

        anomalous_pixels = np.sum(
            local_color_mask > 0
        )

        total_pixels = (
            local_color_mask.shape[0]
            * local_color_mask.shape[1]
        )

        anomaly_ratio = (
            anomalous_pixels
            / max(total_pixels, 1)
        )

        if anomaly_ratio > 0.002:

            local_modification_status = (
                "WARNING"
            )

            local_modification_message = (
                "Localized color inconsistency detected; "
                "manual review recommended."
            )

            tampering_score += 20

        else:

            local_modification_status = (
                "PASSED"
            )

            local_modification_message = (
                "No significant localized color inconsistency detected."
            )

        # ----------------------------------------------------
        # Localized Color Edit Detection
        # ----------------------------------------------------

        # Detect unusually strong warm/orange color regions.
        # This can identify localized edits such as an artificial
        # colored mark added to the document image.
        #
        # This is only a preliminary tampering indicator.
        # It does NOT prove that a document is forged.

        hsv_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2HSV
        )

        # OpenCV HSV:
        # Hue 5-25 approximately covers orange/yellow-orange tones.
        # High saturation helps separate artificial colored marks
        # from the normal low-saturation passport background.

        orange_mask = cv2.inRange(
            hsv_image,
            np.array([5, 120, 100]),
            np.array([25, 255, 255])
        )

        # Remove very small isolated pixels.

        orange_kernel = np.ones(
            (5, 5),
            np.uint8
        )

        orange_mask = cv2.morphologyEx(
            orange_mask,
            cv2.MORPH_OPEN,
            orange_kernel
        )

        # Find connected colored regions.

        contours, _ = cv2.findContours(
            orange_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        large_orange_region = False
        largest_orange_area = 0

        for contour in contours:

            area = cv2.contourArea(
                contour
            )

            if area > largest_orange_area:

                largest_orange_area = area

            if area >= 500:

                large_orange_region = True

        # ----------------------------------------------------
        # Evaluate localized color region
        # ----------------------------------------------------

        image_area = image.shape[0] * image.shape[1]

        orange_ratio = (
            largest_orange_area /
            max(image_area, 1)
        )

        print(
            "\n========== ORANGE DETECTION DEBUG =========="
        )
        print(
            "Largest orange area:",
            largest_orange_area
        )
        print(
            "Image area:",
            image_area
        )
        print(
            "Orange ratio:",
            orange_ratio
        )
        print(
            "Large orange region:",
            large_orange_region
        )
        print(
            "============================================\n"
        )

        # Require a substantially large and localized orange region
        # before treating it as a possible artificial edit.
        if (
            large_orange_region
            and largest_orange_area >= 20000
            and orange_ratio >= 0.03
        ):
            localized_color_status = "WARNING"
            localized_color_message = (
                "Localized artificial color region detected; "
                "manual review recommended."
            )
            tampering_score += 25
        else:
            localized_color_status = "PASSED"
            localized_color_message = (
                "No significant localized artificial color region detected."
            )

        # ----------------------------------------------------
        # Limit Score
        # ----------------------------------------------------

        tampering_score = min(
            tampering_score,
            100
        )

        # ----------------------------------------------------
        # Tampering Status
        # ----------------------------------------------------

        if tampering_score <= 10:

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

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

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
                },

                {
                    "check":
                        "Noise / Texture Analysis",

                    "status":
                        noise_status,

                    "message":
                        noise_message
                },

                {
                    "check":
                        "Local Image Consistency",

                    "status":
                        local_consistency_status,

                    "message":
                        local_consistency_message
                },

                {
                    "check":
                        "Localized Modification Detection",

                    "status":
                        local_modification_status,

                    "message":
                        local_modification_message
                },
                {
                    "check":
                        "Localized Color Edit Detection",

                    "status":
                        localized_color_status,

                    "message":
                        localized_color_message
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

            scaleFactor=1.08,

            minNeighbors=6,

            minSize=(60, 60)

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
    document_type,
    verification_result,
    forensic_analysis
):

    validation_risk = validation.get(
        "risk_score",
        50
    )

    tampering_risk = image_analysis.get(
        "tampering_score",
        50
    )
    
    
    forensic_risk = forensic_analysis.get(
        "forensic_risk_score",
        0
    )

    # OCR risk
    if ocr_confidence >= 80:
        ocr_risk = 0
    elif ocr_confidence >= 60:
        ocr_risk = 10
    elif ocr_confidence >= 40:
        ocr_risk = 20
    else:
        ocr_risk = 30

    # Face detection is only an assistance signal.
    # It is NOT identity verification.
    if face_analysis.get(
        "face_detected",
        False
    ):
        face_risk = 0
    else:
        face_risk = 10

   

    # ---------------------------------------------------------
    # Reference verification risk
    # ---------------------------------------------------------

    reference_risk = 0

    if verification_result.get("found"):

        comparison = verification_result.get(
            "comparison",
            {}
        )

        mismatch_count = 0

        for field_name, field_data in comparison.items():

            if field_name == "document_status":
                continue

            if field_data.get("status") == "MISMATCH":
                mismatch_count += 1

        if mismatch_count == 1:
            reference_risk = 20

        elif mismatch_count >= 2:
            reference_risk = 50

    elif verification_result.get("status") != "NOT CHECKED":

        # Reference not found/unavailable should not prove forgery.
        # It only increases the need for manual review.
        reference_risk = 10

    # ---------------------------------------------------------
    # Discrepancy analysis
    # ---------------------------------------------------------

    discrepancies = []
    discrepancy_count = 0

    if verification_result.get("found"):

        comparison = verification_result.get(
            "comparison",
            {}
        )

        for field_name, field_data in comparison.items():

            if field_name == "document_status":
                continue

            if field_data.get("status") == "MISMATCH":

                discrepancy_count += 1

                discrepancies.append({
                    "field": field_data.get(
                        "label",
                        field_name
                    ),
                    "ocr_value": field_data.get(
                        "ocr_value"
                    ),
                    "reference_value": field_data.get(
                        "reference_value"
                    ),
                    "status": "MISMATCH"
                })

    # Determine discrepancy severity
    if discrepancy_count == 0:

        discrepancy_severity = "NONE"

        discrepancy_summary = (
            "No discrepancies found between "
            "the extracted document data and "
            "the reference record."
        )

    elif discrepancy_count == 1:

        discrepancy_severity = "MEDIUM"

        discrepancy_summary = (
            "One discrepancy was detected between "
            "the document data and the reference record. "
            "Manual verification is recommended."
        )

    else:

        discrepancy_severity = "HIGH"

        discrepancy_summary = (
            f"{discrepancy_count} discrepancies were detected "
            "between the document data and the reference record. "
            "Additional manual verification is required."
        )

    # ---------------------------------------------------------
    # Weighted risk calculation
    # ---------------------------------------------------------

    final_risk = int(
        (
            validation_risk * 0.30
            + tampering_risk * 0.30
            + forensic_risk * 0.20
            + ocr_risk * 0.05
            + face_risk * 0.05
            + reference_risk * 0.10
        )
    )

    final_risk = max(
        0,
        min(
            final_risk,
            100
        )
    )

    # ---------------------------------------------------------
    # Explainable risk reasons
    # ---------------------------------------------------------

    risk_reasons = []

    # Reference verification explanation
    if verification_result.get("found"):

        risk_reasons.append(
            "Reference record found in the database."
        )

        comparison = verification_result.get(
            "comparison",
            {}
        )

        for field_name, field_data in comparison.items():

            if field_name == "document_status":
                continue

            if field_data.get("status") == "MATCH":

                risk_reasons.append(
                    f"{field_data.get('label')} "
                    "matches the reference record."
                )

            elif field_data.get("status") == "MISMATCH":

                risk_reasons.append(
                    f"{field_data.get('label')} "
                    "does not match the reference record."
                )

    elif verification_result.get("status") == "NOT CHECKED":

        risk_reasons.append(
            "Reference verification was not performed."
        )

    else:

        risk_reasons.append(
            "No matching reference record was found."
        )

    # Validation explanation
    if validation_risk <= 20:

        risk_reasons.append(
            "Document structure checks passed."
        )

    elif validation_risk <= 50:

        risk_reasons.append(
            "Some document validation checks require review."
        )

    else:

        risk_reasons.append(
            "Document validation indicates significant concerns."
        )

    # Tampering explanation
    if tampering_risk <= 10:

        risk_reasons.append(
            "No obvious image tampering indicators detected."
        )

    elif tampering_risk <= 50:

        risk_reasons.append(
            "Some image characteristics require manual review."
        )

    else:

        risk_reasons.append(
            "Strong image tampering indicators detected."
        )
        
        
    # Forensic explanation
    if forensic_risk <= 20:

        risk_reasons.append(
            "Forensic analysis found no strong image-level suspicious indicators."
        )

    elif forensic_risk <= 50:

        risk_reasons.append(
            "Forensic analysis detected some image-level indicators that require manual review."
        )

    else:

        risk_reasons.append(
            "Forensic analysis detected strong image-level suspicious indicators."
        )

    # OCR explanation
    if ocr_confidence >= 80:

        risk_reasons.append(
            "OCR confidence is high."
        )

    elif ocr_confidence >= 60:

        risk_reasons.append(
            "OCR confidence is acceptable."
        )

    elif ocr_confidence >= 40:

        risk_reasons.append(
            "OCR confidence is moderate."
        )

    else:

        risk_reasons.append(
            "OCR confidence is low."
        )

    # Face explanation
    if face_analysis.get(
        "face_detected",
        False
    ):

        risk_reasons.append(
            "Face region detected in the document image."
        )

    else:

        risk_reasons.append(
            "No face region detected; manual review may be required."
        )

    # ---------------------------------------------------------
    # Final status
    # ---------------------------------------------------------

    reference_mismatch = discrepancy_count > 0

    # Reference mismatch requires manual review
    if reference_mismatch:

        status = "REVIEW"
        risk_level = "MEDIUM"

        recommendation = (
            "Reference data mismatch detected. "
            "Additional manual verification by an authorized "
            "officer is required."
        )

    # Possible tampering should also trigger manual review
    elif tampering_risk > 10 and final_risk <= 20:

        status = "REVIEW"
        risk_level = "MEDIUM"

        recommendation = (
            "Document shows possible image tampering indicators. "
            "Additional manual verification by an authorized "
            "officer is recommended."
        )

    elif final_risk <= 20:

        status = "VERIFIED"
        risk_level = "LOW"

        recommendation = (
            "Document passed preliminary screening checks. "
            "No significant risk indicators were detected."
        )

    elif final_risk <= 50:

        status = "REVIEW"
        risk_level = "MEDIUM"

        recommendation = (
            "Document requires additional manual "
            "verification by an authorized officer."
        )

    else:

        status = "HIGH RISK"
        risk_level = "HIGH"

        recommendation = (
            "Document contains indicators requiring "
            "further manual investigation."
        )

    # ---------------------------------------------------------
    # Final assessment result
    # ---------------------------------------------------------

    return {
        "status": status,
        "risk_level": risk_level,
        "risk_score": final_risk,
        "recommendation": recommendation,
        "risk_reasons": risk_reasons,

        "discrepancy_analysis": {
            "count": discrepancy_count,
            "severity": discrepancy_severity,
            "summary": discrepancy_summary,
            "items": discrepancies
        },

        "components": {
            "validation_risk": validation_risk,
            "tampering_risk": tampering_risk,
            "forensic_risk": forensic_risk,
            "ocr_risk": ocr_risk,
            "face_risk": face_risk,
            "reference_risk": reference_risk
        }
    }