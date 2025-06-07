import pandas as pd
import io
from typing import List, Dict, Union
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---------- CSV / DataFrame Utilities ----------

def validate_csv_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Check if all required columns exist in the given DataFrame.
    """
    if df is None or df.empty:
        return False  # ✅ Vérification si le DataFrame est vide
    return all(col in df.columns for col in required_columns)


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """
    Convert a DataFrame to a UTF-8 encoded CSV in bytes.
    """
    if df.empty:
        raise ValueError("❌ The DataFrame is empty, cannot convert to CSV.")  # ✅ Protection contre les erreurs
    return df.to_csv(index=False).encode("utf-8")


def read_csv(uploaded_file) -> pd.DataFrame:
    """
    Read a CSV file from an uploaded file-like object.
    """
    try:
        return pd.read_csv(uploaded_file)
    except pd.errors.EmptyDataError:
        raise ValueError("❌ The uploaded CSV file is empty.")
    except pd.errors.ParserError:
        raise ValueError("❌ Error parsing the CSV file. Check formatting.")
    except Exception as e:
        raise ValueError(f"❌ Unknown error while reading CSV: {e}")  # ✅ Meilleure gestion des erreurs


def get_summary_stats(df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute summary statistics for the 'predicted_yield' column.
    Returns: dictionary with min, max, average, and standard deviation.
    """
    column_name = "predicted_yield"
    if df.empty or column_name not in df.columns:
        return {"error": "❌ Column 'predicted_yield' not found in DataFrame"}  # ✅ Avertissement

    return {
        "min": df[column_name].min(),
        "max": df[column_name].max(),
        "avg": df[column_name].mean(),
        "std": df[column_name].std(),
    }


def group_by_user(history_df: pd.DataFrame) -> Union[pd.Series, None]:
    """
    Group predictions by username and compute average predicted yield per user.
    """
    if history_df.empty or "username" not in history_df.columns or "predicted_yield" not in history_df.columns:
        return None  # ✅ Évite les erreurs

    return history_df.groupby("username")["predicted_yield"].mean()

# ---------- Disease Prediction Utility ----------

def predict_disease(symptoms: List[str]) -> str:
    """
    Simple disease prediction based on symptoms.
    
    Args:
        symptoms: List of observed symptoms

    Returns:
        Predicted disease name
    """
    disease_dict = {
        "yellow leaves": "Nitrogen Deficiency",
        "black spots": "Fungal Infection",
        "wilting": "Root Rot",
        "leaf curling": "Virus Infection"
    }

    for symptom in symptoms:
        if symptom.lower() in disease_dict:
            return f"⚠️ Possible Disease: {disease_dict[symptom.lower()]}"
    
    return "✅ No disease detected. Further analysis required."

# ---------- PDF Report Generation ----------

def generate_pdf_report(username: str, inputs: Dict[str, Union[str, float]], prediction: float, suggestion: str, filename: str = "report.pdf") -> io.BytesIO:
    """
    Generate a PDF report summarizing the prediction result.

    Args:
        username: Name of the user
        inputs: Dictionary of input features
        prediction: Predicted yield value
        suggestion: Textual recommendation or suggestion
        filename: (unused, optional name for download)

    Returns:
        BytesIO buffer containing the PDF data
    """
    if not username or not inputs or prediction is None:
        raise ValueError("❌ Missing required report information!")  # ✅ Vérification avant génération

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Smart Yield Predictor Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"User: {username}")
    c.drawString(50, height - 100, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 📌 Séparation visuelle claire pour les entrées
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 140, "Input Parameters:")
    y = height - 160
    c.setFont("Helvetica", 12)

    for key, value in inputs.items():
        c.drawString(70, y, f"{key}: {value}")
        y -= 20

    c.drawString(50, y - 10, f"Predicted Yield: {prediction} quintals/ha")
    c.drawString(50, y - 30, f"Suggestion: {suggestion}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
if __name__ == "__main__":
    print("🚀 Utils module successfully loaded!")
