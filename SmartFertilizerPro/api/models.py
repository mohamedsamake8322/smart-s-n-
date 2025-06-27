from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class SoilTexture(str, Enum):
    SANDY = "sandy"
    LOAMY = "loamy"
    CLAY = "clay"
    SILT = "silt"

class SoilAnalysis(BaseModel):
    ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH level")
    organic_matter: float = Field(..., ge=0.0, le=100.0, description="Organic matter percentage")
    nitrogen: float = Field(..., ge=0.0, description="Available nitrogen (ppm)")
    phosphorus: float = Field(..., ge=0.0, description="Available phosphorus (ppm)")
    potassium: float = Field(..., ge=0.0, description="Available potassium (ppm)")
    cec: float = Field(..., ge=0.0, description="Cation Exchange Capacity (cmol/kg)")
    texture: SoilTexture = Field(..., description="Soil texture classification")
    ec: Optional[float] = Field(None, ge=0.0, description="Electrical conductivity (dS/m)")
    calcium: Optional[float] = Field(None, ge=0.0, description="Available calcium (ppm)")
    magnesium: Optional[float] = Field(None, ge=0.0, description="Available magnesium (ppm)")
    sulfur: Optional[float] = Field(None, ge=0.0, description="Available sulfur (ppm)")
    zinc: Optional[float] = Field(None, ge=0.0, description="Available zinc (ppm)")
    iron: Optional[float] = Field(None, ge=0.0, description="Available iron (ppm)")
    manganese: Optional[float] = Field(None, ge=0.0, description="Available manganese (ppm)")
    boron: Optional[float] = Field(None, ge=0.0, description="Available boron (ppm)")

class CropSelection(BaseModel):
    crop_type: str = Field(..., description="Type of crop (e.g., maize, rice, wheat)")
    variety: str = Field(..., description="Specific variety of the crop")
    planting_season: str = Field(..., description="Planting season (wet/dry)")
    growth_duration: int = Field(..., ge=30, le=365, description="Growth duration in days")

class FertilizerType(BaseModel):
    name: str = Field(..., description="Fertilizer name")
    n_content: float = Field(..., ge=0.0, le=100.0, description="Nitrogen percentage")
    p_content: float = Field(..., ge=0.0, le=100.0, description="Phosphorus percentage")
    k_content: float = Field(..., ge=0.0, le=100.0, description="Potassium percentage")
    price_per_kg: float = Field(..., ge=0.0, description="Price per kilogram")
    availability: str = Field(..., description="Availability status")

class ApplicationTiming(BaseModel):
    stage: str = Field(..., description="Growth stage")
    days_after_planting: int = Field(..., ge=0, description="Days after planting")
    fertilizer_type: str = Field(..., description="Type of fertilizer to apply")
    amount_kg_per_ha: float = Field(..., ge=0.0, description="Amount in kg per hectare")
    application_method: str = Field(..., description="Application method")
    notes: Optional[str] = Field(None, description="Additional notes")

class NutrientBalance(BaseModel):
    total_n: float = Field(..., description="Total nitrogen recommendation (kg/ha)")
    total_p: float = Field(..., description="Total phosphorus recommendation (kg/ha)")
    total_k: float = Field(..., description="Total potassium recommendation (kg/ha)")
    secondary_nutrients: Dict[str, float] = Field(default_factory=dict, description="Secondary nutrients")
    micronutrients: Dict[str, float] = Field(default_factory=dict, description="Micronutrients")

class CostAnalysis(BaseModel):
    total_cost: float = Field(..., description="Total fertilizer cost")
    cost_per_hectare: float = Field(..., description="Cost per hectare")
    currency: str = Field(..., description="Currency used")
    fertilizer_breakdown: Dict[str, float] = Field(default_factory=dict, description="Cost breakdown by fertilizer type")

class FertilizerRecommendation(BaseModel):
    recommendation_id: str = Field(..., description="Unique recommendation ID")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    soil_analysis: SoilAnalysis
    crop_selection: CropSelection
    region: str = Field(..., description="Agricultural region")
    area_hectares: float = Field(..., description="Cultivation area in hectares")
    target_yield: float = Field(..., description="Target yield")
    
    # Core recommendations
    nutrient_balance: NutrientBalance
    application_schedule: List[ApplicationTiming]
    recommended_fertilizers: List[FertilizerType]
    
    # Analysis results
    cost_analysis: CostAnalysis
    expected_yield: float = Field(..., description="Expected yield with recommendations")
    roi_percentage: float = Field(..., description="Return on investment percentage")
    
    # Additional information
    climate_considerations: List[str] = Field(default_factory=list, description="Climate-related recommendations")
    risk_factors: List[str] = Field(default_factory=list, description="Potential risk factors")
    alternative_options: List[str] = Field(default_factory=list, description="Alternative fertilization options")
    
    # Metadata
    language: str = Field(default="en", description="Report language")
    units: str = Field(default="metric", description="Unit system used")
