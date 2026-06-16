import random


# ── Template banks ─────────────────────────────────────────────────────────────

REGRESSION_INTROS = [
    "Based on {context}the estimated {target} is {value}.",
    "For {context}our analysis predicts a {target} of {value}.",
    "Looking at {context}the projected {target} comes out to {value}.",
    "With {context}the forecasted {target} is approximately {value}.",
    "Analyzing {context}we estimate the {target} at {value}.",
]

REGRESSION_MIDDLES = [
    "This figure is derived from historical patterns in your data.",
    "This estimate reflects trends observed across your past records.",
    "Your historical data suggests this as the most likely outcome.",
    "This projection is calculated from patterns in similar past transactions.",
    "This is based on what your data has shown in comparable scenarios.",
]

REGRESSION_CLOSINGS = [
    "Actual results may vary depending on market conditions and business factors.",
    "Consider external factors like seasonality or promotions that could shift this.",
    "Use this as a planning baseline — real outcomes may differ based on current conditions.",
    "Monitor actual performance against this estimate to refine future predictions.",
    "Recent market changes not reflected in your data could affect the actual outcome.",
]

CLASSIFICATION_INTROS = [
    "Based on {context}the predicted {target} is '{prediction}'.",
    "For {context}the model predicts '{prediction}' as the most likely {target}.",
    "Analyzing {context}the expected {target} is '{prediction}'.",
    "With {context}our system classifies the {target} as '{prediction}'.",
]

CLASSIFICATION_MIDDLES = [
    "This prediction is based on patterns observed in similar historical records.",
    "Similar past cases in your data suggest this classification.",
    "Your historical data strongly associates these inputs with this outcome.",
    "This reflects the most common outcome for similar records in your dataset.",
]

CLASSIFICATION_CLOSINGS = [
    "Actual outcomes may vary depending on future conditions and additional factors.",
    "Consider reviewing comparable cases to validate this prediction.",
    "Monitor results over time to improve the model's accuracy with more data.",
    "This is a probability-based estimate — edge cases may produce different results.",
]

DEFAULTS_NOTES = [
    "Some inputs were not specified, so average historical values were used.",
    "Missing inputs were filled with typical values from your historical data.",
    "Average values from past records were assumed for unspecified inputs.",
    "Where inputs were not provided, the system used median values from training data.",
]

LOW_ACCURACY_NOTES = [
    "Note: The model has limited training data — consider uploading more records for better accuracy.",
    "More training data would improve prediction reliability.",
    "Accuracy may improve as more data is added to this dataset.",
]


def build_prediction_explanation(
    target_col: str,
    prediction,
    model_type: str,
    input_data: dict = None,
    used_defaults: list = None,
    metrics: dict = None,
) -> str:

    target = target_col.replace("_", " ").strip()

    monetary_keywords = [
        "sales", "revenue", "profit", "income",
        "amount", "price", "cost", "salary", "expense", "budget"
    ]
    is_money = any(k in target_col.lower() for k in monetary_keywords)

    # Build input context string
    context = ""
    if input_data:
        parts = [
            f"{k.replace('_', ' ')}: {v}"
            for k, v in list(input_data.items())[:3]
        ]
        if parts:
            context = f"{', '.join(parts)} — "

    # Format prediction value
    if isinstance(prediction, float):
        value = f"₹{prediction:,.2f}" if is_money else f"{prediction:,.2f}"
    elif isinstance(prediction, int):
        value = f"₹{prediction:,}" if is_money else f"{prediction:,}"
    else:
        value = str(prediction)

    # Defaults note
    defaults_note = ""
    if used_defaults and len(used_defaults) > 0:
        defaults_note = " " + random.choice(DEFAULTS_NOTES)

    # Low accuracy warning
    accuracy_note = ""
    if metrics and isinstance(metrics.get("r2"), (int, float)):
        if metrics["r2"] < 0.3:
            accuracy_note = " " + random.choice(LOW_ACCURACY_NOTES)

    # ── Classification ─────────────────────────────────────────────────────────
    if model_type == "classification":
        intro = random.choice(CLASSIFICATION_INTROS).format(
            context=context,
            target=target,
            prediction=prediction,
        )
        middle = random.choice(CLASSIFICATION_MIDDLES)
        closing = random.choice(CLASSIFICATION_CLOSINGS)
        return f"{intro} {middle} {closing}{defaults_note}{accuracy_note}"

    # ── Regression ─────────────────────────────────────────────────────────────
    if isinstance(prediction, (int, float)):
        intro = random.choice(REGRESSION_INTROS).format(
            context=context,
            target=target,
            value=value,
        )
        middle = random.choice(REGRESSION_MIDDLES)
        closing = random.choice(REGRESSION_CLOSINGS)
        return f"{intro} {middle} {closing}{defaults_note}{accuracy_note}"

    # Fallback
    return f"The predicted {target} is {prediction}.{defaults_note}"