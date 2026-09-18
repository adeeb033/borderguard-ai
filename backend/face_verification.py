from fastapi import APIRouter, UploadFile, File, HTTPException,Form
from deepface import DeepFace
import tempfile
import os
import requests

router = APIRouter(
    prefix="/face-verification",
    tags=["Face Verification"]
)


@router.post("/verify")
async def verify_face(
    document_face: UploadFile = File(...),
    live_face: UploadFile = File(...),
    document_number: str = Form(...)
):

    document_temp = None
    live_temp = None

    try:
        # Document number is received from the screening result
        if not document_number:
                raise HTTPException(
        status_code=400,
        detail="Document number is required for reference face verification."
    )

        # Read uploaded images
        document_contents = await document_face.read()
        live_contents = await live_face.read()

        # Create temporary files
        document_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        )

        live_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        )

        document_file.write(document_contents)
        live_file.write(live_contents)

        document_file.close()
        live_file.close()

        document_temp = document_file.name
        live_temp = live_file.name

        # Face verification using FaceNet
        result = DeepFace.verify(
            img1_path=document_temp,
            img2_path=live_temp,
            model_name="Facenet",
            detector_backend="opencv"
        )

                # Reference face verification
        reference_face_result = None

        reference_face_path = os.path.join(
            os.path.dirname(__file__),
            "reference_faces",
            f"{document_number}.jpg"
        )

        if os.path.exists(reference_face_path):
            reference_face_result = DeepFace.verify(
                img1_path=reference_face_path,
                img2_path=live_temp,
                model_name="Facenet",
                detector_backend="opencv"
            )

        verified = bool(result.get("verified", False))
        distance = float(result.get("distance", 0))
        threshold = float(result.get("threshold", 0))
        confidence = float(result.get("confidence", 0))

        if verified:
            status = "MATCH"
            message = (
                "The live face matches the face detected "
                "on the document."
            )
        else:
            status = "MISMATCH"
            message = (
                "The live face does not match the face "
                "detected on the document."
            )

        reference_verified = None
        reference_distance = None
        reference_threshold = None
        reference_confidence = None

        if reference_face_result:
            reference_verified = bool(
                reference_face_result.get("verified", False)
            )
            reference_distance = float(
                reference_face_result.get("distance", 0)
            )
            reference_threshold = float(
                reference_face_result.get("threshold", 0)
            )
            reference_confidence = float(
                reference_face_result.get("confidence", 0)
            )

        return {
            "success": True,
            "status": status,
            "verified": verified,
            "distance": distance,
            "threshold": threshold,
            "confidence": confidence,
            "model": "Facenet",

            "reference_face_verification": {
                "available": reference_face_result is not None,
                "verified": reference_verified,
                "status": (
                    "MATCH"
                    if reference_verified is True
                    else "MISMATCH"
                    if reference_verified is False
                    else "NOT AVAILABLE"
                ),
                "distance": reference_distance,
                "threshold": reference_threshold,
                "confidence": reference_confidence
            },

            "message": message
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        # Delete temporary files
        if document_temp and os.path.exists(document_temp):
            os.remove(document_temp)

        if live_temp and os.path.exists(live_temp):
            os.remove(live_temp)