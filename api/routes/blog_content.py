from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from ..oauth2 import get_current_user
from ..schemas import BlogContent, BlogContentResponse, db

router = APIRouter(prefix="/blog", tags=["Blog Content"])


# Blog CRUD
@router.post(
    "", response_description="Create blog content", response_model=BlogContentResponse
)
async def create_blog(
    blog_content: BlogContent, current_user=Depends(get_current_user)
):
    try:
        blog_content = jsonable_encoder(blog_content)

        # Add aditional info
        blog_content["author_name"] = current_user["name"]
        blog_content["author_id"] = current_user["_id"]
        blog_content["created_at"] = str(datetime.utcnow())

        new_blog_content = await db["blogPost"].insert_one(blog_content)
        print(new_blog_content.inserted_id)

        return await db["blogPost"].find_one({"_id": new_blog_content.inserted_id})
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "", response_description="Get blog posts", response_model=List[BlogContentResponse]
)
async def get_blogs(limit: int = 10, order_by: str = "created_at"):
    try:
        return (
            await db["blogPost"]
            .find({"$query": {}, "$orderby": {order_by: -1}})
            .to_list(limit)
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{id}",
    response_description="Get blog post by id",
    response_model=Optional[BlogContentResponse],
)
async def get_blog_by_id(id: str):
    blog_post = await db["blogPost"].find_one({"_id": id})
    if blog_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )

    return blog_post


@router.put(
    "/{id}",
    response_description="Update blog content",
    response_model=Optional[BlogContentResponse],
)
async def update_blog(
    id: str, blog_content: BlogContent, current_user=Depends(get_current_user)
):
    blog_post = await db["blogPost"].find_one({"_id": id})
    if blog_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog post {id} not found",
        )
    if blog_post["author_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorised to edit blog post {id}",
        )

    try:
        blog_content = {k: v for k, v in blog_content.dict().items() if v is not None}
        updated_result = await db["blogPost"].update_one(
            {"_id": id}, {"$set": blog_content}
        )
        updated_blog_post = await db["blogPost"].find_one({"_id": id})
        if (
            len(blog_content) >= 1
            and updated_result.modified_count == 1
            and updated_blog_post is not None
        ):
            return updated_blog_post

        existing_blog_post = await db["blogPost"].find_one({"_id": id})
        if existing_blog_post is not None:
            return existing_blog_post
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{id}", response_description="Delete blog post")
async def delete_blog_post(id: str, current_user=Depends(get_current_user)):
    blog_post = await db["blogPost"].find_one({"_id": id})
    if blog_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog post {id} not found",
        )
    if blog_post["author_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorised to delete blog post {id}",
        )

    try:
        delete_result = await db["blogPost"].delete_one({"_id": id})
        if delete_result.deleted_count == 1:
            return HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail=f"Successfully deleted blog post {id}",
            )

        raise HTTPException()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
