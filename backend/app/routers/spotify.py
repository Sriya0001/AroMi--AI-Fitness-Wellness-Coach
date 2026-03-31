from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.spotify_service import spotify_service
from app.core.config import settings
import json

router = APIRouter(prefix="/spotify", tags=["spotify"])

@router.get("/authorize")
async def authorize(current_user: User = Depends(get_current_user)):
    auth_manager = spotify_service.get_auth_manager()
    # Pass user_id in state to link back in callback
    authorize_url = auth_manager.get_authorize_url(state=str(current_user.id))
    return {"authorization_url": authorize_url}

@router.get("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    user_id = request.query_params.get("state")
    error = request.query_params.get("error")
    
    if error:
        print(f"DEBUG: Spotify auth error: {error}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/workout?spotify=error&detail={error}")

    if not code or not user_id:
        print("DEBUG: Spotify callback missing code or state")
        raise HTTPException(status_code=400, detail="Required parameters missing")
    
    try:
        auth_manager = spotify_service.get_auth_manager()
        token_info = auth_manager.get_access_token(code)
        
        if not token_info:
            print("DEBUG: Failed to retrieve token info from Spotify")
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/workout?spotify=error&detail=token_fail")

        # Save to user
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user:
            user.spotify_token_data = json.dumps(token_info)
            db.add(user)
            db.commit()
            print(f"DEBUG: Successfully saved Spotify token for user {user_id}")
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/workout?spotify=success")
        else:
            print(f"DEBUG: User {user_id} not found during Spotify callback")
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/workout?spotify=error&detail=user_not_found")
            
    except Exception as e:
        print(f"DEBUG: Exception in Spotify callback: {str(e)}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/workout?spotify=error&detail=exception")

@router.get("/playlists")
async def get_workout_playlists(
    query: str = "workout",
    current_user: User = Depends(get_current_user)
):
    if not current_user.spotify_token_data:
        raise HTTPException(status_code=400, detail="Spotify account not linked")
    
    playlists = spotify_service.get_playlists(current_user.spotify_token_data, query)
    return {"playlists": playlists}
