from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.restaurant import Restaurant

router = APIRouter(prefix="/restaurants", tags=["restaurants"])
@router.post("/")
def create_restaurant(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    restaurant = Restaurant(
        name=data["name"],
        address=data.get("address"),
        owner_id=current_user.id,
    )

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant

@router.get("/")
def list_restaurants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Restaurant)
        .filter(Restaurant.owner_id == current_user.id)
        .all()
    )
@router.put("/{restaurant_id}")
def update_restaurant(
    restaurant_id: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.id == restaurant_id,
            Restaurant.owner_id == current_user.id,
        )
        .first()
    )

    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found")

    restaurant.name = data.get("name", restaurant.name)
    restaurant.address = data.get("address", restaurant.address)

    db.commit()
    db.refresh(restaurant)
    return restaurant
@router.delete("/{restaurant_id}")
def delete_restaurant(
    restaurant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    restaurant = (
        db.query(Restaurant)
        .filter(
            Restaurant.id == restaurant_id,
            Restaurant.owner_id == current_user.id,
        )
        .first()
    )

    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(restaurant)
    db.commit()
    return {"message": "deleted"}
