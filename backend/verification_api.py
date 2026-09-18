from fastapi import APIRouter
import os
import json

try:
    from backend.database import get_db_connection
except ImportError:
    from database import get_db_connection


# ----------------------------------------------------
# VERIFICATION ROUTER
# ----------------------------------------------------

router = APIRouter(
    prefix="/verification",
    tags=["Verification"]
)


# ----------------------------------------------------
# VERIFICATION API STATUS
# ----------------------------------------------------

@router.get("/status")
def verification_status():
    return {
        "status": "Verification API is working"
    }


# ----------------------------------------------------
# DATABASE STATUS
# ----------------------------------------------------

@router.get("/db-status")
def database_status():
    try:
        conn = get_db_connection()
        conn.close()

        return {
            "status": "PostgreSQL connection successful"
        }

    except Exception as e:
        return {
            "status": "PostgreSQL connection failed",
            "error": str(e)
        }


# ----------------------------------------------------
# CHECK DOCUMENT IN REFERENCE DATABASE
# ----------------------------------------------------

@router.get("/check/{document_number}")
def check_document(document_number: str):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                document_type,
                document_number,
                full_name,
                date_of_birth,
                nationality,
                expiry_date,
                gender,
                status
            FROM public.reference_documents
            WHERE document_number = %s
            """,
            (document_number,)
        )

        record = cursor.fetchone()

        cursor.close()
        conn.close()

        # ---------------------------------------------
        # REFERENCE NOT FOUND
        # ---------------------------------------------

        if record is None:
            return {
                "document_number": document_number,
                "found": False,
                "message": "Reference document not found."
            }

        # ---------------------------------------------
        # REFERENCE FOUND
        # ---------------------------------------------

        return {
    "document_number": record[1],
    "found": True,
    "reference_data": {
        "document_type": record[0],
        "document_number": record[1],
        "full_name": record[2],
        "date_of_birth": record[3],
        "nationality": record[4],
        "expiry_date": record[5],
        "gender": record[6],
        "status": record[7]
    }
}

    except Exception as e:

        return {
            "document_number": document_number,
            "found": False,
            "message": "Database verification failed.",
            "error": str(e)
        }


# ----------------------------------------------------
# FIELD-BY-FIELD DOCUMENT COMPARISON
# ----------------------------------------------------

def compare_document_data(ocr_data, reference_data):

    comparison = {}

    fields = {
        "document_number": "Document Number",
        "full_name": "Name",
        "date_of_birth": "Date of Birth",
        "nationality": "Nationality",
        "expiry_date": "Expiry Date"
    }

    for field, display_name in fields.items():

        ocr_value = str(
            ocr_data.get(field, "")
        ).strip().upper()

        reference_value = str(
            reference_data.get(field, "")
        ).strip().upper()

        # ---------------------------------------------
        # OCR VALUE NOT DETECTED
        # ---------------------------------------------

        if not ocr_value:

            comparison[field] = {
                "label": display_name,
                "ocr_value": ocr_data.get(field),
                "reference_value": reference_data.get(field),
                "status": "NOT DETECTED"
            }

        # ---------------------------------------------
        # VALUES MATCH
        # ---------------------------------------------

        elif ocr_value == reference_value:

            comparison[field] = {
                "label": display_name,
                "ocr_value": ocr_data.get(field),
                "reference_value": reference_data.get(field),
                "status": "MATCH"
            }

        # ---------------------------------------------
        # VALUES DO NOT MATCH
        # ---------------------------------------------

        else:

            comparison[field] = {
                "label": display_name,
                "ocr_value": ocr_data.get(field),
                "reference_value": reference_data.get(field),
                "status": "MISMATCH"
            }

    # ---------------------------------------------
    # DOCUMENT STATUS
    # ---------------------------------------------

    comparison["document_status"] = {
        "label": "Document Status",
        "ocr_value": None,
        "reference_value": reference_data.get("status"),
        "status": "REFERENCE STATUS"
    }

    return comparison


# ----------------------------------------------------
# COMPARISON TEST
# ----------------------------------------------------

@router.get("/compare-test")
def compare_test():

    ocr_data = {
        "document_number": "P12345678",
        "full_name": "ARJUN KUMAR",
        "date_of_birth": "15/08/2005",
        "nationality": "IND",
        "expiry_date": "15/08/2035"
    }

    reference_data = {
        "document_type": "Passport",
        "document_number": "P12345678",
        "full_name": "ARJUN KUMAR",
        "date_of_birth": "15/08/2005",
        "nationality": "IND",
        "expiry_date": "15/08/2035",
        "gender": "M",
        "status": "ACTIVE"
    }

    comparison = compare_document_data(
        ocr_data,
        reference_data
    )

    return {
        "comparison": comparison
    }
    
@router.get("/reference-face/{document_number}")
def get_reference_face(document_number: str):

    reference_face_folder = os.path.join(
        os.path.dirname(__file__),
        "reference_faces"
    )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT document_number, full_name
            FROM public.reference_documents
            WHERE document_number = %s
            """,
            (document_number,)
        )

        record = cursor.fetchone()

        cursor.close()
        conn.close()

        if record is None:
            return {
                "found": False,
                "message": "Reference document not found."
            }

        document_number = record[0]
        full_name = record[1]

        reference_face_path = os.path.join(
            reference_face_folder,
            f"{document_number}.jpg"
        )

        if not os.path.exists(reference_face_path):
            return {
                "found": True,
                "face_found": False,
                "document_number": document_number,
                "full_name": full_name,
                "message": "Reference face image not found."
            }

        return {
            "found": True,
            "face_found": True,
            "document_number": document_number,
            "full_name": full_name,
            "reference_face": reference_face_path
        }

    except Exception as e:
        return {
            "found": False,
            "face_found": False,
            "message": "Reference face lookup failed.",
            "error": str(e)
        }
        
        
        
        # ----------------------------------------------------
# CHECKPOINT GATE STATUS
# ----------------------------------------------------

@router.get("/gates")
def get_checkpoint_gates():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                gate_code,
                status,
                created_at
            FROM public.checkpoint_gates
            ORDER BY id
            """
        )

        records = cursor.fetchall()

        cursor.close()
        conn.close()

        gates = []

        for record in records:
            gates.append({
                "id": record[0],
                "gate_code": record[1],
                "status": record[2],
                "created_at": record[3]
            })

        return {
            "total_gates": len(gates),
            "active_gates": sum(
                1 for gate in gates
                if gate["status"] == "ACTIVE"
            ),
            "inactive_gates": sum(
                1 for gate in gates
                if gate["status"] == "INACTIVE"
            ),
            "gates": gates
        }

    except Exception as e:

        return {
            "total_gates": 0,
            "active_gates": 0,
            "inactive_gates": 0,
            "gates": [],
            "error": str(e)
        }
        
        
        # ----------------------------------------------------
# SCREENING HISTORY
# ----------------------------------------------------

@router.get("/history")
def get_screening_history():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
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
                risk_reasons,
                screening_date
            FROM public.screening_history
            ORDER BY screening_date DESC
            """
        )

        records = cursor.fetchall()

        cursor.close()
        conn.close()

        history = []

        for record in records:
            history.append({
                "id": record[0],
                "screening_id": record[1],
                "filename": record[2],
                "applicant_name": record[3],
                "document_type": record[4],
                "risk_score": record[5],
                "risk_level": record[6],
                "status": record[7],
                "review_status": record[8],
                "officer_notes": record[9],
                "reviewed_at": record[10],
                "ocr_confidence": record[11],
                "validation_score": record[12],
                "tampering_score": record[13],
                "face_detected": record[14],
                "risk_reasons": record[15],
                "screening_date": record[16]
            })

        return {
            "history": history,
            "total": len(history)
        }

    except Exception as e:

        return {
            "history": [],
            "total": 0,
            "error": str(e)
        }
        
     # ----------------------------------------------------
# SAVE SCREENING HISTORY
# ----------------------------------------------------

@router.post("/history")
def save_screening_history(data: dict):

    try:
        conn = get_db_connection()
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
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            RETURNING id
            """,
            (
                data.get("screening_id"),
                data.get("filename"),
                data.get("applicant_name"),
                data.get("document_type"),
                data.get("risk_score"),
                data.get("risk_level"),
                data.get("status"),
                data.get("review_status", "PENDING"),
                data.get("officer_notes"),
                data.get("reviewed_at"),
                data.get("ocr_confidence"),
                data.get("validation_score"),
                data.get("tampering_score"),
                data.get("face_detected"),
                json.dumps(data.get("risk_reasons", []))
            )
        )

        record_id = cursor.fetchone()[0]

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "success": True,
            "message": "Screening history saved successfully.",
            "id": record_id,
            "screening_id": data.get("screening_id")
        }

    except Exception as e:

        return {
            "success": False,
            "message": "Failed to save screening history.",
            "error": str(e)
        }   
        
        
# ----------------------------------------------------
# SCREENING HISTORY
# ----------------------------------------------------

@router.get("/screening-history")
def get_screening_history():
    
    

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
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
                risk_reasons,
                screening_date
            FROM public.screening_history
            ORDER BY screening_date DESC
            """
        )

        records = cursor.fetchall()

        cursor.close()
        conn.close()

        history = []

        for record in records:
            history.append({
                "id": record[0],
                "screening_id": record[1],
                "filename": record[2],
                "applicant_name": record[3],
                "document_type": record[4],
                "risk_score": record[5],
                "risk_level": record[6],
                "status": record[7],
                "review_status": record[8],
                "officer_notes": record[9],
                "reviewed_at": record[10],
                "ocr_confidence": record[11],
                "validation_score": record[12],
                "tampering_score": record[13],
                "face_detected": record[14],
                "risk_reasons": record[15],
                "screening_date": record[16]
            })

        return {
            "count": len(history),
            "history": history
        }

    except Exception as e:

        return {
            "count": 0,
            "history": [],
            "error": str(e)
        }

@router.get("/security-alerts")
def get_security_alerts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                alert_id,
                screening_id,
                filename,
                applicant_name,
                document_type,
                risk_score,
                risk_level,
                alert_type,
                description,
                status,
                created_at
            FROM public.security_alerts
            ORDER BY created_at DESC
            """
        )

        records = cursor.fetchall()

        cursor.close()
        conn.close()

        alerts = []

        for record in records:
            alerts.append({
                "id": record[0],
                "alert_id": record[1],
                "screening_id": record[2],
                "filename": record[3],
                "applicant_name": record[4],
                "document_type": record[5],
                "risk_score": record[6],
                "risk_level": record[7],
                "alert_type": record[8],
                "description": record[9],
                "status": record[10],
                "created_at": record[11]
            })

        return {
            "count": len(alerts),
            "alerts": alerts
        }

    except Exception as e:
        return {
            "count": 0,
            "alerts": [],
            "error": str(e)
        }       
# ----------------------------------------------------
# UPDATE OFFICER REVIEW
# ----------------------------------------------------

@router.put("/screening-history/{screening_id}/review")
def update_officer_review(
    screening_id: str,
    review_status: str,
    officer_notes: str = ""
):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE public.screening_history
            SET
                review_status = %s,
                officer_notes = %s,
                reviewed_at = CURRENT_TIMESTAMP,
                status = CASE
                    WHEN %s = 'PENDING' THEN 'REVIEW'
                    ELSE 'REVIEWED'
                END
            WHERE screening_id = %s
            RETURNING
                screening_id,
                review_status,
                officer_notes,
                reviewed_at,
                status
            """,
            (
                review_status,
                officer_notes,
                review_status,
                screening_id
            )
        )

        record = cursor.fetchone()

        conn.commit()

        cursor.close()
        conn.close()

        if not record:
            return {
                "success": False,
                "message": "Screening record not found"
            }

        return {
            "success": True,
            "message": "Officer review updated successfully",
            "record": {
                "screening_id": record[0],
                "review_status": record[1],
                "officer_notes": record[2],
                "reviewed_at": record[3],
                "status": record[4]
            }
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }