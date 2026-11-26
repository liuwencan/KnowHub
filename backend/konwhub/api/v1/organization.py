from fastapi import APIRouter, Depends, HTTPException, Request

from konwhub.api.dependencies import require_staff
from konwhub.schemas.api import DepartmentRequest, RoleRequest, RoleDepartmentRequest, UserRoleRequest, UserUpdateRequest

router = APIRouter(tags=["organization"])


def service(request: Request):
    value = request.app.state.organization
    if value is None:
        raise HTTPException(status_code=503, detail="Database is not configured")
    return value


def present(item):
    return {column.name: getattr(item, column.name) for column in item.__table__.columns}


@router.get("/departments")
def list_departments(request: Request, _: object = Depends(require_staff)):
    return [present(item) for item in service(request).list("departments")]


@router.post("/departments", status_code=201)
def create_department(payload: DepartmentRequest, request: Request, _: object = Depends(require_staff)):
    return present(service(request).create_department(payload))


@router.patch("/departments/{department_id}")
def update_department(department_id: int, payload: DepartmentRequest, request: Request, _: object = Depends(require_staff)):
    item = service(request).update_department(department_id, payload)
    if not item: raise HTTPException(status_code=404, detail="Department not found")
    return present(item)


@router.delete("/departments/{department_id}")
def delete_department(department_id: int, request: Request, _: object = Depends(require_staff)):
    if not service(request).delete_department(department_id): raise HTTPException(status_code=404, detail="Department not found")
    return {"success": True}


@router.get("/roles")
def list_roles(request: Request, _: object = Depends(require_staff)):
    return [present(item) for item in service(request).list("roles")]


@router.post("/roles", status_code=201)
def create_role(payload: RoleRequest, request: Request, _: object = Depends(require_staff)):
    try: return present(service(request).create_role(payload))
    except ValueError as error: raise HTTPException(status_code=409, detail=str(error)) from error


@router.patch("/roles/{role_id}")
def update_role(role_id: int, payload: RoleRequest, request: Request, _: object = Depends(require_staff)):
    item = service(request).update_role(role_id, payload)
    if not item: raise HTTPException(status_code=404, detail="Role not found")
    return present(item)


@router.delete("/roles/{role_id}")
def delete_role(role_id: int, request: Request, _: object = Depends(require_staff)):
    if not service(request).delete_role(role_id): raise HTTPException(status_code=404, detail="Role not found")
    return {"success": True}


@router.get("/users")
def list_users(request: Request, _: object = Depends(require_staff)):
    return [present(item) for item in service(request).list("users")]


@router.get("/users/{user_id}")
def get_user(user_id: int, request: Request, _: object = Depends(require_staff)):
    with service(request)._session() as session:
        from konwhub.infrastructure.persistence.repositories import OrganizationRepository
        item = OrganizationRepository(session).get_user(user_id)
    if not item or item.deleted_at is not None: raise HTTPException(status_code=404, detail="User not found")
    return present(item)


@router.patch("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdateRequest, request: Request, _: object = Depends(require_staff)):
    item = service(request).update_user(user_id, payload)
    if not item: raise HTTPException(status_code=404, detail="User not found")
    return present(item)


@router.delete("/users/{user_id}")
def delete_user(user_id: int, request: Request, _: object = Depends(require_staff)):
    if not service(request).delete_user(user_id): raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}


@router.post("/user-roles", status_code=201)
def add_user_role(payload: UserRoleRequest, request: Request, _: object = Depends(require_staff)):
    try: return present(service(request).add_user_role(payload))
    except ValueError as error: raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/users/{user_id}/roles")
def list_user_roles(user_id: int, request: Request, _: object = Depends(require_staff)):
    return [present(item) for item in service(request).list("user_roles", user_id)]


@router.post("/role-departments", status_code=201)
def add_role_department(payload: RoleDepartmentRequest, request: Request, _: object = Depends(require_staff)):
    try: return present(service(request).add_role_department(payload))
    except ValueError as error: raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/roles/{role_id}/departments")
def list_role_departments(role_id: int, request: Request, _: object = Depends(require_staff)):
    return [present(item) for item in service(request).list("role_departments", role_id)]
