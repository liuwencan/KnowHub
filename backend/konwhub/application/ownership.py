from fastapi import HTTPException


def ensure_owner(owner_id: str, principal_id: str) -> None:
    if owner_id != principal_id:
        raise HTTPException(status_code=404, detail="Resource not found")


def ensure_permission(permissions: set[str], required: str) -> None:
    if required not in permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
