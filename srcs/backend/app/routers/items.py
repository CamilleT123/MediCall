from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import database, crud, schemas

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.post("/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(database.get_db)):
    return crud.create_item(db, item)
