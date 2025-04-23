from fastapi import Query


def chat_paginator(
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=100)
):
    offset = (page - 1) * page_size
    return {"limit": page_size,"offset": offset}