from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.sql import func
from typing import List, Optional
from datetime import datetime
import secrets
import string

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_optional_user
from app.models.models import Link, User
from app.schemas.schemas import (
    LinkCreate, LinkUpdate, LinkResponse, 
    LinkStatsResponse, LinkSearchResponse
)
from app.services.cache_service import CacheService
from app.core.config import settings

router = APIRouter()
cache_service = CacheService()

def generate_short_code(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@router.post("/links/shorten", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_short_link(
    link_data: LinkCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    short_code = link_data.custom_alias
    if short_code:
        result = await db.execute(
            select(Link).where(Link.short_code == short_code)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom alias already exists"
            )
    else:
        while True:
            short_code = generate_short_code()
            result = await db.execute(
                select(Link).where(Link.short_code == short_code)
            )
            if not result.scalar_one_or_none():
                break
    
    new_link = Link(
        short_code=short_code,
        original_url=str(link_data.original_url),
        user_id=current_user.id if current_user else None,
        expires_at=link_data.expires_at,
        is_custom=bool(link_data.custom_alias)
    )
    
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    
    await cache_service.cache_link(new_link)
    
    return LinkResponse(
        short_code=new_link.short_code,
        short_url=f"{settings.BASE_URL}/api/{new_link.short_code}",
        original_url=new_link.original_url,
        expires_at=new_link.expires_at,
        is_custom=new_link.is_custom
    )

@router.get("/{short_code}")
async def redirect_to_original(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    cached_link = await cache_service.get_cached_link(short_code)
    
    if cached_link:
        link = cached_link
    else:
        result = await db.execute(
            select(Link).where(
                and_(
                    Link.short_code == short_code,
                    Link.is_active == True
                )
            )
        )
        link = result.scalar_one_or_none()
        
        if link:
            await cache_service.cache_link(link)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    if link.expires_at and link.expires_at < datetime.utcnow():
        link.is_active = False
        await db.commit()
        await cache_service.invalidate_cache(short_code)
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )
    
    link.clicks += 1
    link.last_clicked_at = datetime.utcnow()
    await db.commit()
    
    await cache_service.invalidate_cache(short_code)
    
    return {"original_url": link.original_url}

@router.get("/links/{short_code}/stats", response_model=LinkStatsResponse)
async def get_link_stats(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    if link.user_id and link.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return LinkStatsResponse(
        short_code=link.short_code,
        original_url=link.original_url,
        clicks=link.clicks,
        created_at=link.created_at,
        last_clicked_at=link.last_clicked_at,
        expires_at=link.expires_at,
        is_active=link.is_active
    )

@router.put("/links/{short_code}", response_model=LinkResponse)
async def update_link(
    short_code: str,
    link_data: LinkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    if link.user_id and link.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    link.original_url = str(link_data.original_url)
    await db.commit()
    await db.refresh(link)
    
    await cache_service.invalidate_cache(short_code)
    
    return LinkResponse(
        short_code=link.short_code,
        short_url=f"{settings.BASE_URL}/api/{link.short_code}",
        original_url=link.original_url,
        expires_at=link.expires_at,
        is_custom=link.is_custom
    )

@router.delete("/links/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Link).where(Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    if link.user_id and link.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    await db.delete(link)
    await db.commit()
    
    await cache_service.invalidate_cache(short_code)

@router.get("/links/search", response_model=List[LinkSearchResponse])
async def search_links(
    original_url: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    query = select(Link).where(
        and_(
            Link.original_url.contains(original_url),
            Link.is_active == True
        )
    )
    
    if current_user:
        query = query.where(
            or_(
                Link.user_id == current_user.id,
                Link.user_id == None
            )
        )
    else:
        query = query.where(Link.user_id == None)
    
    result = await db.execute(query)
    links = result.scalars().all()
    
    return [
        LinkSearchResponse(
            short_code=link.short_code,
            original_url=link.original_url,
            clicks=link.clicks,
            created_at=link.created_at
        )
        for link in links
    ]

@router.get("/links/expired/history")
async def get_expired_links_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Link).where(
            and_(
                Link.expires_at < datetime.utcnow(),
                Link.user_id == current_user.id
            )
        )
    )
    links = result.scalars().all()
    
    return [
        {
            "short_code": link.short_code,
            "original_url": link.original_url,
            "expires_at": link.expires_at,
            "clicks": link.clicks,
            "created_at": link.created_at
        }
        for link in links
    ]