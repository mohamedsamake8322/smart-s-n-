from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from .models import SoilAnalysis, CropSelection, FertilizerRecommendation
from SmartFertilizerPro.core.smart_fertilizer_engine import SmartFertilizerEngine
from SmartFertilizerPro.core.regional_context import RegionalContext

app = FastAPI(title="Smart Fertilizer API", version="1.0.0")

# Initialize the fertilizer engine
fertilizer_engine = SmartFertilizerEngine()
regional_context = RegionalContext()

class FertilizerRequest(BaseModel):
    soil_analysis: SoilAnalysis
    crop_selection: CropSelection
    region: str
    area_hectares: float
    target_yield: float
    local_currency: str = "USD"

@app.post("/generate-fertilizer-plan", response_model=FertilizerRecommendation)
async def generate_fertilizer_plan(request: FertilizerRequest):
    """
    Generate a comprehensive fertilizer recommendation based on soil analysis and crop requirements
    """
    try:
        # Get regional context
        region_data = regional_context.get_region_data(request.region)

        # Generate fertilizer recommendation
        recommendation = fertilizer_engine.generate_recommendation(
            soil_analysis=request.soil_analysis,
            crop_selection=request.crop_selection,
            region_data=region_data,
            area_hectares=request.area_hectares,
            target_yield=request.target_yield,
            currency=request.local_currency
        )

        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/regions")
async def get_available_regions():
    """Get list of supported regions"""
    return regional_context.get_available_regions()

@app.get("/crops")
async def get_available_crops():
    """Get list of supported crops"""
    return fertilizer_engine.get_available_crops()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Smart Fertilizer API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
