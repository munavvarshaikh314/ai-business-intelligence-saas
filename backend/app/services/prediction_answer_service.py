import json
from fastapi import HTTPException
from app.services.ml_model_service import MLModelService
from app.services.ml_prediction_service import MLPredictionService
from app.services.llm_service import LLMService
from app.services.logging_service import LoggingService
from app.utils.confidence_utils import label_confidence
from app.utils.prediction_explanation import build_prediction_explanation

class PredictionAnswerService:

    @staticmethod
    def answer(dataset_id: str, user_id: str, question: str) -> dict:

        # Check model exists
        try:
            model_info = MLModelService.get_model_info(user_id, dataset_id)
        except HTTPException:
            return {
                "answer": (
                    "No prediction model has been trained for this dataset yet. "
                    "Please upload a CSV file — the system will auto-train a model within seconds."
                ),
                "confidence": 0.0,
                "confidence_label": "low",
                "guardrail": "no_model",
                "query_type": "PREDICTION",
                "sources": [],
            }

        target_col = model_info["target_column"]
        model_type = model_info["model_type"]
        metrics = model_info.get("metrics", {})
        model_name = model_info["model_name"]

        # Load feature columns so Gemini knows what to extract
        from app.ml.predictor import Predictor
        meta = Predictor.load_feature_meta(model_name)
        feature_columns = meta.get("feature_columns", [])
        defaults = meta.get("defaults", {})

        # Extract feature values from question using Gemini
        input_data = {}
        if feature_columns:
            extraction_prompt = f"""You are a feature extraction agent for ML predictions.

The model predicts: "{target_col}" ({model_type}).
Required feature columns: {feature_columns}

Extract any feature values mentioned in the user question as a JSON object.
Only include values explicitly mentioned in the question.
Return empty dict {{}} if no values are mentioned — the system will use defaults.

User question: {question}

Return ONLY valid JSON:"""
            try:
                raw = LLMService.generate_text(extraction_prompt)
                raw = raw.strip().replace("```json", "").replace("```", "").strip()
                if raw and raw != "{}":
                    input_data = json.loads(raw)
                    LoggingService.info(f"EXTRACTED FEATURES = {input_data}")
            except Exception as e:
                LoggingService.warning(f"Feature extraction failed: {e}")
                input_data = {}

        # Run prediction — predictor fills missing columns with defaults
        try:
            pred_result = MLPredictionService.predict(user_id, dataset_id, input_data)
        except HTTPException as e:
            return {
                "answer": f"Prediction could not be completed: {e.detail}",
                "confidence": 0.0,
                "confidence_label": "low",
                "guardrail": "prediction_failed",
                "query_type": "PREDICTION",
                "sources": [],
            }
        except Exception as e:
            LoggingService.error(f"Prediction error: {e}")
            return {
                "answer": "Prediction failed. Please retrain the model by re-uploading your CSV.",
                "confidence": 0.0,
                "confidence_label": "low",
                "guardrail": "prediction_error",
                "query_type": "PREDICTION",
                "sources": [],
            }

        prediction = pred_result.get("prediction")
        LoggingService.info(f"PREDICTION RESULT = {pred_result}")
        confidence = pred_result.get("confidence")

        if confidence is None:
         confidence = 0.0
        used_defaults = pred_result.get("used_defaults", [])

        # Format answer
        defaults_note = ""
        if used_defaults:
            defaults_note = f" (Based on average values for: {', '.join(used_defaults[:3])}{'...' if len(used_defaults) > 3 else ''})"

        format_prompt = f"""You are a senior business analyst presenting ML prediction results to a non-technical business owner.

Prediction details:
- Predicted {target_col}: {prediction}
- Input values used: {json.dumps(input_data) if input_data else 'average historical values'}
- Default values applied for: {', '.join(used_defaults[:5]) if used_defaults else 'none'}
- Model accuracy: {json.dumps(metrics)}

User question: {question}

Write a 3-4 sentence business-friendly interpretation:
1. Mention the key input values used (category, region, quantity, price etc if available)
2. State the predicted {target_col} clearly with ₹ symbol
3. Give a brief business interpretation — is this high, moderate, or low?
4. Add one specific caveat about what could change this prediction

Rules:
- Never use technical terms like regression, model, features, ML, dataset
- Never use markdown formatting like ** or ## or bullet points
- Write in flowing sentences like a human business advisor
- Use ₹ symbol for all monetary values
- Be specific — mention actual values, not generic statements"""

        # try:
        #     formatted_answer = LLMService.generate_text(format_prompt)
        #     LoggingService.info(f"FORMATTED ANSWER = {formatted_answer}")
        # except Exception:
        #     formatted_answer = (
        #         f"Predicted {target_col}: {prediction:.2f}.{defaults_note}"
        #         if isinstance(prediction, float)
        #         else f"Predicted {target_col}: {prediction}.{defaults_note}"
        #     )
        formatted_answer = build_prediction_explanation(
        target_col=target_col,
        prediction=prediction,
        model_type=model_type,
        input_data=input_data,
        used_defaults=used_defaults,
        metrics=metrics,  # ← add this
)

        guardrail = "used_defaults" if used_defaults else None

        return {
            "answer": formatted_answer,
            "prediction": prediction,
            "confidence": confidence,
            "confidence_label": label_confidence(confidence),
            "guardrail": guardrail,
            "target_column": target_col,
            "model_type": model_type,
            "used_defaults": used_defaults,
            "input_data": input_data,
            "query_type": "PREDICTION",
            "sources": [{"model": model_name, "metrics": metrics}],
        }

# import json
# from fastapi import HTTPException
# from app.services.ml_model_service import MLModelService
# from app.services.ml_prediction_service import MLPredictionService
# from app.services.llm_service import LLMService
# from app.services.logging_service import LoggingService
# from app.utils.confidence_utils import label_confidence


# class PredictionAnswerService:

#     @staticmethod
#     def answer(dataset_id: str, user_id: str, question: str) -> dict:

#         # Check if model exists
#         try:
#             model_info = MLModelService.get_model_info(user_id, dataset_id)
#         except HTTPException:
#             return {
#                 "answer": (
#                     "No prediction model has been trained for this dataset yet. "
#                     "Please upload a CSV file — the system will auto-train a model within seconds. "
#                     "Or go to Analytics → Train Model to train manually."
#                 ),
#                 "confidence": 0.0,
#                 "confidence_label": "low",
#                 "guardrail": "no_model",
#                 "query_type": "PREDICTION",
#                 "sources": [],
#             }

#         target_col = model_info["target_column"]
#         model_type = model_info["model_type"]
#         metrics = model_info.get("metrics", {})

#         # Extract features from question using Gemini
#         extraction_prompt = f"""
# You are a feature extraction agent for ML predictions.
# The model predicts: "{target_col}" ({model_type}).

# Extract feature values mentioned in the user question as a JSON object.
# Only include values explicitly mentioned. Use null for anything not mentioned.

# User question: {question}

# Return ONLY valid JSON. Example:
# {{"region": "North", "category": "Electronics", "quantity": 5}}
# """
#         try:
#             raw = LLMService.generate_text(extraction_prompt)
#             raw = raw.strip().replace("```json", "").replace("```", "").strip()
#             input_data = json.loads(raw)
#         except Exception as e:
#             LoggingService.warning(f"Feature extraction failed: {e}")
#             input_data = {}

#         # Run prediction
#         try:
#             pred_result = MLPredictionService.predict(user_id, dataset_id, input_data)
#         except HTTPException as e:
#             return {
#                 "answer": f"Prediction could not be completed: {e.detail}",
#                 "confidence": 0.0,
#                 "confidence_label": "low",
#                 "guardrail": "prediction_failed",
#                 "query_type": "PREDICTION",
#                 "sources": [],
#             }
#         except Exception as e:
#             return {
#                 "answer": "Prediction failed due to an unexpected error. Please check your data and try again.",
#                 "confidence": 0.0,
#                 "confidence_label": "low",
#                 "guardrail": "prediction_error",
#                 "query_type": "PREDICTION",
#                 "sources": [],
#             }

#         prediction = pred_result.get("prediction")
#         confidence = pred_result.get("confidence") or 0.0

#         # Format answer using Gemini
#         format_prompt = f"""
# You are a helpful business analyst presenting ML prediction results.

# Model predicted:
# - Target: {target_col}
# - Prediction: {prediction}
# - Model type: {model_type}
# - Confidence: {round(confidence * 100, 1) if confidence else "N/A"}%
# - Model accuracy metrics: {json.dumps(metrics)}

# User question: {question}

# Write a clear, 2-3 sentence business-friendly answer.
# Include the prediction value and confidence.
# Do not use technical ML jargon.
# If confidence is below 60%, add a note that the prediction should be treated as an estimate only.
# """
#         try:
#             formatted_answer = LLMService.generate_text(format_prompt)
#         except Exception:
#             formatted_answer = (
#                 f"Predicted {target_col}: {prediction}. "
#                 f"Confidence: {round(confidence * 100, 1)}%."
#             )

#         guardrail = "low_confidence_estimate" if confidence < 0.6 else None

#         return {
#             "answer": formatted_answer,
#             "prediction": prediction,
#             "confidence": confidence,
#             "confidence_label": label_confidence(confidence),
#             "guardrail": guardrail,
#             "target_column": target_col,
#             "model_type": model_type,
#             "query_type": "PREDICTION",
#             "sources": [{"model": model_info["model_name"], "metrics": metrics}],
#         }




# import json
# from fastapi import HTTPException
# from app.services.ml_model_service import MLModelService
# from app.services.ml_prediction_service import MLPredictionService
# from app.services.llm_service import LLMService
# from app.services.logging_service import LoggingService


# class PredictionAnswerService:

#     @staticmethod
#     def answer(dataset_id: str, user_id: str, question: str) -> dict:
#         """
#         Full ML prediction pipeline connected to chat.
#         1. Load trained model info
#         2. Use Gemini to extract feature values from natural language question
#         3. Run prediction
#         4. Format human-readable answer
#         """

#         # Step 1 — Check if model exists
#         try:
#             model_info = MLModelService.get_model_info(user_id, dataset_id)
#         except HTTPException:
#             return {
#                 "answer": (
#                     "No prediction model is trained for this dataset yet. "
#                     "Please upload a CSV first — the system will auto-train a model. "
#                     "Or go to Analytics → Train Model to train manually."
#                 ),
#                 "confidence": 0.0,
#                 "query_type": "PREDICTION",
#                 "sources": []
#             }

#         target_col = model_info["target_column"]
#         model_type = model_info["model_type"]
#         metrics = model_info.get("metrics", {})

#         # Step 2 — Extract feature values from question using Gemini
#         extraction_prompt = f"""
# You are a feature extraction agent.

# The user wants a ML prediction. The model predicts: "{target_col}" ({model_type}).

# Extract feature values from the user question as a JSON object.
# Only include features that are clearly mentioned.
# Use null for missing values.

# User question: {question}

# Return ONLY valid JSON, nothing else. Example:
# {{"region": "North", "category": "Electronics", "quantity": 5}}
# """
#         try:
#             raw = LLMService.generate_text(extraction_prompt)
#             raw = raw.strip().replace("```json", "").replace("```", "").strip()
#             input_data = json.loads(raw)
#         except Exception as e:
#             LoggingService.warning(f"Feature extraction failed: {e}")
#             input_data = {}

#         # Step 3 — Run prediction
#         try:
#             pred_result = MLPredictionService.predict(user_id, dataset_id, input_data)
#         except HTTPException as e:
#             return {
#                 "answer": f"Prediction failed: {e.detail}",
#                 "confidence": 0.0,
#                 "query_type": "PREDICTION",
#                 "sources": []
#             }
#         except Exception as e:
#             return {
#                 "answer": "Prediction could not be completed. Please check your input data.",
#                 "confidence": 0.0,
#                 "query_type": "PREDICTION",
#                 "sources": []
#             }

#         prediction = pred_result.get("prediction")
#         confidence = pred_result.get("confidence") or 0.0

#         # Step 4 — Format answer using Gemini
#         format_prompt = f"""
# You are a helpful business analyst.

# A ML model predicted the following:
# - Target: {target_col}
# - Prediction: {prediction}
# - Model type: {model_type}
# - Confidence: {round(confidence * 100, 1) if confidence else "N/A"}%
# - Model metrics: {json.dumps(metrics)}

# User's original question: {question}

# Write a clear, concise, business-friendly answer in 2-3 sentences.
# Do not use technical jargon. Be direct about the prediction value.
# """
#         try:
#             formatted_answer = LLMService.generate_text(format_prompt)
#         except Exception:
#             # Fallback to simple answer if LLM fails
#             formatted_answer = (
#                 f"Predicted {target_col}: {prediction}. "
#                 f"Confidence: {round(confidence * 100, 1)}%."
#             )

#         return {
#             "answer": formatted_answer,
#             "prediction": prediction,
#             "confidence": confidence,
#             "target_column": target_col,
#             "model_type": model_type,
#             "query_type": "PREDICTION",
#             "sources": [{"model": model_info["model_name"], "metrics": metrics}]
#         }


# both are diffrent codes

# from app.services.prediction_service import PredictionService


# class PredictionAnswerService:

#     @staticmethod
#     def answer(dataset_id: str, user_id: str, question: str):
#         """
#         This is a placeholder prediction router.
#         Later we will parse question into structured payload.
#         """

#         # Simple example: call sales prediction with dummy payload
#         payload = type("obj", (object,), {"month": "next_month", "marketing_spend": None})

#         result = PredictionService.predict_sales(dataset_id, user_id, payload)

#         return {
#             "answer": f"Predicted Sales: {result['prediction']} (confidence: {result.get('confidence', 0)})",
#             "confidence": result.get("confidence", 0.0),
#             "sources": [],
#             "query_type": "PREDICTION"
#         }