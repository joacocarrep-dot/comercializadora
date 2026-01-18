


"""
Módulo de seguridad para autenticación y autorización JWT.

Proporciona funciones para:
- Crear y verificar tokens JWT
- Hashear y verificar contraseñas
- Dependencias de FastAPI para autenticación y autorización
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.settings import settings
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de autenticación HTTP Bearer
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con un hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de contraseña almacenado
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para una contraseña.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de acceso.
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": "user_id"})
        expires_delta: Tiempo de expiración personalizado. Si no se proporciona,
                      se usa ACCESS_TOKEN_EXPIRE_MINUTES de settings.
        
    Returns:
        str: Token JWT firmado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de refresh.
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración personalizado. Si no se proporciona,
                      se usa REFRESH_TOKEN_EXPIRE_DAYS de settings.
        
    Returns:
        str: Token JWT de refresh firmado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        Dict[str, Any]: Datos decodificados del token
        
    Raises:
        UnauthorizedException: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Verificar que el token no haya expirado
        expire = payload.get("exp")
        if expire is None:
            raise UnauthorizedException(
                message="Token sin fecha de expiración",
                details={"token_error": "missing_expiration"}
            )
        
        if datetime.utcnow() > datetime.fromtimestamp(expire):
            raise UnauthorizedException(
                message="Token expirado",
                details={"token_error": "expired_token"}
            )
        
        return payload
        
    except JWTError as e:
        raise UnauthorizedException(
            message="Token inválido",
            details={"token_error": str(e)}
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Dependencia de FastAPI para obtener el usuario actual.
    
    Args:
        credentials: Credenciales de autorización HTTP Bearer
        session: Sesión de base de datos
        
    Returns:
        User: Usuario autenticado
        
    Raises:
        UnauthorizedException: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials
    
    # Verificar token
    payload = await verify_token(token)
    
    # Extraer user_id del token
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(
            message="Token no contiene identificación de usuario",
            details={"token_error": "missing_subject"}
        )
    
    # Buscar usuario en la base de datos
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(int(user_id))
    
    if user is None:
        raise UnauthorizedException(
            message="Usuario no encontrado",
            details={"user_id": user_id}
        )
    
    if not user.is_active:
        raise ForbiddenException(
            message="Usuario desactivado",
            details={"user_id": user_id}
        )
    
    return user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependencia de FastAPI para verificar que el usuario es administrador.
    
    Args:
        current_user: Usuario actual (inyectado por get_current_user)
        
    Returns:
        User: Usuario administrador
        
    Raises:
        ForbiddenException: Si el usuario no es administrador
    """
    if not current_user.is_admin:
        raise ForbiddenException(
            message="Se requieren privilegios de administrador",
            details={"user_id": current_user.id, "is_admin": False}
        )
    
    return current_user


async def authenticate_user(
    username: str, 
    password: str, 
    session: AsyncSession
) -> Optional[User]:
    """
    Autentica un usuario con nombre de usuario y contraseña.
    
    Args:
        username: Nombre de usuario o email
        password: Contraseña en texto plano
        session: Sesión de base de datos
        
    Returns:
        Optional[User]: Usuario autenticado o None si la autenticación falla
    """
    user_repo = UserRepository(session)
    
    # Buscar usuario por email o nombre de usuario
    user = await user_repo.get_by_email(username)
    if not user:
        user = await user_repo.get_by_username(username)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    if not user.is_active:
        return None
    
    return user


def create_tokens_for_user(user: User) -> Dict[str, str]:
    """
    Crea tokens de acceso y refresh para un usuario.
    
    Args:
        user: Usuario para el cual crear los tokens
        
    Returns:
        Dict[str, str]: Tokens de acceso y refresh
    """
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


async def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    """
    Crea un nuevo token de acceso a partir de un refresh token.
    
    Args:
        refresh_token: Token de refresh válido
        
    Returns:
        Dict[str, str]: Nuevo token de acceso
        
    Raises:
        UnauthorizedException: Si el refresh token es inválido
    """
    # Verificar que el token sea un refresh token
    payload = await verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise UnauthorizedException(
            message="Token no es un refresh token",
            details={"token_error": "invalid_token_type"}
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(
            message="Refresh token no contiene identificación de usuario",
            details={"token_error": "missing_subject"}
        )
    
    # Crear nuevo token de acceso
    new_access_token = create_access_token(data={"sub": user_id})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }



