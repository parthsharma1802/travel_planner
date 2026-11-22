from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.services.grok_service import grok_service

router = APIRouter(prefix="/chat", tags=["SmartTrip AI Assistant"])

class ChatMessageInput(BaseModel):
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text content")

class TravelChatRequest(BaseModel):
    message: Optional[str] = Field(None)
    messages: Optional[List[ChatMessageInput]] = Field(None)
    system_prompt: Optional[str] = Field(None)
    model: Optional[str] = Field(None)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    landmark_context: Optional[Dict[str, Any]] = Field(None, description="Landmark recognition result from CV model")

from typing import List, Optional, Dict, Any, Union

class TravelPreferences(BaseModel):
    starting_point: Optional[Union[str, int]] = Field(None, description="Starting city/point of journey")
    destination: Optional[Union[str, int]] = Field(None)
    dates: Optional[Union[str, int]] = Field(None)
    duration: Optional[Union[str, int]] = Field(None)
    budget: Optional[Union[str, int, float]] = Field(None, description="User's exact budget input")
    travelers: Optional[Union[str, int]] = Field(None)
    transport: Optional[Union[str, int]] = Field(None)
    spiritual_focus: Optional[Union[str, int]] = Field(None)
    interests: List[Any] = Field(default_factory=list)
    travel_style: Optional[Union[str, int]] = Field(None)

class TravelChatResponse(BaseModel):
    status: str = "success"
    message: str = Field(...)
    intent: str = Field(...)
    preferences: TravelPreferences = Field(...)
    quiz: Optional[Dict[str, Any]] = Field(None)
    itinerary: Optional[Dict[str, Any]] = Field(None, description="Structured premium itinerary for UI rendering")
    route_data: Optional[Dict[str, Any]] = Field(None)
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Ranked recommendations from RecommendationEngine")
    landmark_context: Optional[Dict[str, Any]] = Field(None, description="Landmark recognition metadata")
    train_data: Optional[Dict[str, Any]] = Field(None, description="Verified live train schedules from RailKit / IndianRailApi")
    flight_data: Optional[Dict[str, Any]] = Field(None, description="Verified live flight schedules & fares from Google Flights")
    hotel_data: Optional[Dict[str, Any]] = Field(None, description="Hotel reference rates and external booking links")
    model: str = Field(...)
    usage: Optional[Dict[str, Any]] = None

@router.post("", response_model=TravelChatResponse)
async def chat_completion(request: TravelChatRequest):
    try:
        formatted_messages = []
        if request.messages:
            formatted_messages = [msg.model_dump() for msg in request.messages]
        elif request.message:
            formatted_messages = [{"role": "user", "content": request.message}]
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide 'message' or 'messages'.")

        result = await grok_service.generate_smart_trip_response(
            messages=formatted_messages,
            system_prompt=request.system_prompt,
            model=request.model,
            temperature=request.temperature or 0.7,
            landmark_context=request.landmark_context
        )

        return TravelChatResponse(
            status="success",
            message=result["message"],
            intent=result["intent"],
            preferences=TravelPreferences(**result["preferences"]),
            quiz=result.get("quiz"),
            itinerary=result.get("itinerary"),
            route_data=result.get("route_data"),
            recommendations=result.get("recommendations"),
            landmark_context=result.get("landmark_context"),
            train_data=result.get("train_data"),
            flight_data=result.get("flight_data"),
            hotel_data=result.get("hotel_data"),
            model=result["model"],
            usage=result.get("usage")
        )

    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
