from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User as UserModel
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    MFASetupRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    SessionResponse,
    LoginHistoryResponse,
)
from app.schemas.user import User
from app.crud.user import (
    authenticate_user,
    update_last_login,
    enable_mfa,
    disable_mfa,
    change_password,
    get_user_by_email,
)
from app.crud.session import (
    create_session,
    refresh_session,
    revoke_session,
    revoke_all_sessions,
    get_user_sessions,
)
from app.crud.audit_log import (
    create_audit_log,
    get_user_audit_logs,
    get_failed_login_attempts,
)
from app.crud.password_reset import (
    create_password_reset_token,
    verify_password_reset_token,
    mark_password_reset_token_used,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_mfa_secret,
    get_mfa_totp_uri,
    generate_qr_code,
    generate_mfa_backup_codes,
    verify_mfa_code,
    is_password_expired,
)
from app.core.deps import get_current_user, get_request_info

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    User login endpoint

    Args:
        request: FastAPI Request object
        login_data: Login credentials (username, password, optional mfa_code)
        db: Database session

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    request_info = await get_request_info(request)

    # Authenticate user
    user = await authenticate_user(db, login_data.username, login_data.password)

    if not user:
        # Log failed login attempt
        await create_audit_log(
            db=db,
            action="LOGIN",
            resource_type="User",
            username=login_data.username,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason="Invalid credentials or account locked",
        )

        # Check if there have been multiple failed attempts
        failed_attempts = await get_failed_login_attempts(db, login_data.username)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if MFA is enabled
    if user.mfa_enabled:
        if not login_data.mfa_code:
            # Return response indicating MFA is required
            return TokenResponse(
                access_token="",
                refresh_token="",
                token_type="bearer",
                expires_in=0,
                mfa_required=True,
                mfa_setup_required=False,
            )

        # Verify MFA code
        if not verify_mfa_code(user.mfa_secret, login_data.mfa_code):
            await create_audit_log(
                db=db,
                action="LOGIN",
                resource_type="User",
                username=user.username,
                user_id=user.id,
                ip_address=request_info["ip_address"],
                user_agent=request_info["user_agent"],
                request_path=request_info["request_path"],
                request_method=request_info["request_method"],
                success=False,
                failure_reason="Invalid MFA code",
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code",
            )

    # Check if password is expired
    password_expired = is_password_expired(user.password_changed_at)

    # Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Create session
    await create_session(
        db=db,
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
    )

    # Update last login
    await update_last_login(db, user)

    # Log successful login
    await create_audit_log(
        db=db,
        action="LOGIN",
        resource_type="User",
        username=user.username,
        user_id=user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60,  # 30 minutes in seconds
        mfa_required=False,
        mfa_setup_required=password_expired,  # Prompt password change if expired
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token

    Args:
        refresh_data: Refresh token
        db: Database session

    Returns:
        TokenResponse with new access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Create new tokens (refresh token rotation)
    new_access_token = create_access_token(int(user_id))
    new_refresh_token = create_refresh_token(int(user_id))

    # Rotate session
    new_session = await refresh_session(
        db=db,
        old_refresh_token=refresh_data.refresh_token,
        new_access_token=new_access_token,
        new_refresh_token=new_refresh_token,
    )

    if not new_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=30 * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout current user and revoke session

    Args:
        request: FastAPI Request object
        current_user: Current authenticated user
        db: Database session
    """
    request_info = await get_request_info(request)

    # Get token from Authorization header
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

        # Revoke the session
        from app.core.security import hash_token
        from app.crud.session import get_session_by_token_hash

        token_hash = hash_token(token)
        session = await get_session_by_token_hash(db, token_hash)
        if session:
            await revoke_session(db, session.id, current_user.id)

    # Log logout
    await create_audit_log(
        db=db,
        action="LOGOUT",
        resource_type="User",
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout from all devices

    Args:
        request: FastAPI Request object
        current_user: Current authenticated user
        db: Database session
    """
    request_info = await get_request_info(request)

    # Revoke all sessions
    await revoke_all_sessions(db, current_user.id)

    # Log logout all
    await create_audit_log(
        db=db,
        action="LOGOUT_ALL",
        resource_type="User",
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


@router.get("/me", response_model=User, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse with user information
    """
    return UserResponse.model_validate(current_user)


@router.post("/mfa/setup", response_model=MFASetupResponse, status_code=status.HTTP_200_OK)
async def setup_mfa(
    request: Request,
    mfa_setup: MFASetupRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate MFA setup (generate secret and QR code)

    Args:
        request: FastAPI Request object
        mfa_setup: MFA setup request with password verification
        current_user: Current authenticated user
        db: Database session

    Returns:
        MFASetupResponse with secret, QR code, and backup codes

    Raises:
        HTTPException: If password verification fails
    """
    from app.crud.user import authenticate_user

    # Verify password before enabling MFA
    user = await authenticate_user(db, current_user.username, mfa_setup.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    # Generate MFA secret
    secret = generate_mfa_secret()

    # Generate backup codes
    backup_codes = generate_mfa_backup_codes()

    # Generate QR code
    totp_uri = get_mfa_totp_uri(secret, current_user.username)
    qr_code = generate_qr_code(totp_uri)

    # Log MFA setup initiation
    request_info = await get_request_info(request)
    await create_audit_log(
        db=db,
        action="MFA_SETUP_INITIATED",
        resource_type="User",
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return MFASetupResponse(
        secret=secret,
        qr_code_url=qr_code,
        backup_codes=backup_codes,
    )


@router.post("/mfa/verify", status_code=status.HTTP_204_NO_CONTENT)
async def verify_and_enable_mfa(
    request: Request,
    mfa_verify: MFAVerifyRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify MFA code and enable MFA for user

    Args:
        request: FastAPI Request object
        mfa_verify: MFA verification request with secret and code
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If MFA code verification fails
    """
    # Verify MFA code
    if not verify_mfa_code(mfa_verify.secret, mfa_verify.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code",
        )

    # Enable MFA for user
    await enable_mfa(db, current_user, mfa_verify.secret)

    # Log MFA enablement
    request_info = await get_request_info(request)
    await create_audit_log(
        db=db,
        action="MFA_ENABLED",
        resource_type="User",
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


@router.post("/mfa/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_mfa_endpoint(
    request: Request,
    mfa_setup: MFASetupRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disable MFA for user

    Args:
        request: FastAPI Request object
        mfa_setup: MFA setup request with password verification
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If password verification fails
    """
    from app.crud.user import authenticate_user

    # Verify password before disabling MFA
    user = await authenticate_user(db, current_user.username, mfa_setup.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    # Disable MFA
    await disable_mfa(db, current_user)

    # Log MFA disablement
    request_info = await get_request_info(request)
    await create_audit_log(
        db=db,
        action="MFA_DISABLED",
        resource_type="User",
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password_endpoint(
    request: Request,
    password_change: PasswordChangeRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user password

    Args:
        request: FastAPI Request object
        password_change: Password change request
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If old password is incorrect or new password doesn't meet requirements
    """
    try:
        await change_password(
            db,
            current_user,
            password_change.old_password,
            password_change.new_password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Log password change
    request_info = await get_request_info(request)
    await create_audit_log(
        db=db,
        action="PASSWORD_CHANGED",
        resource_type="User",
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


@router.post("/password-reset/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(
    password_reset: PasswordResetRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset (sends email with reset link)

    Args:
        password_reset: Password reset request with email
        request: FastAPI Request object
        db: Database session

    Note:
        This endpoint always returns 204 to prevent email enumeration
    """
    request_info = await get_request_info(request)

    # Find user by email
    user = await get_user_by_email(db, password_reset.email)

    if user:
        # Create password reset token
        reset_token = await create_password_reset_token(
            db=db,
            user=user,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
        )

        # TODO: Send email with reset link
        # For now, we'll just log the token (in production, send email)
        print(f"Password reset token for {user.email}: {reset_token.plain_token}")

        # Log password reset request
        await create_audit_log(
            db=db,
            action="PASSWORD_RESET_REQUESTED",
            resource_type="User",
            username=user.username,
            user_id=user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_password_reset(
    password_reset: PasswordResetConfirm,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm password reset with token and new password

    Args:
        password_reset: Password reset confirmation
        request: FastAPI Request object
        db: Database session

    Raises:
        HTTPException: If token is invalid or password doesn't meet requirements
    """
    from app.crud.user import reset_password

    # Verify reset token
    user = await verify_password_reset_token(db, password_reset.token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Reset password
    try:
        await reset_password(db, user, password_reset.new_password)

        # Mark token as used
        await mark_password_reset_token_used(db, password_reset.token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Log password reset
    request_info = await get_request_info(request)
    await create_audit_log(
        db=db,
        action="PASSWORD_RESET_COMPLETED",
        resource_type="User",
        username=user.username,
        user_id=user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


@router.get("/sessions", response_model=list[SessionResponse], status_code=status.HTTP_200_OK)
async def get_sessions(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active sessions for current user

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of SessionResponse objects
    """
    sessions = await get_user_sessions(db, current_user.id)

    return [
        SessionResponse(
            id=session.id,
            device_type=session.device_type,
            device_name=session.device_name,
            browser=session.browser,
            location=session.location,
            ip_address=session.ip_address,
            created_at=session.created_at,
            last_used_at=session.last_used_at,
            is_current=False,  # Will be updated by frontend
        )
        for session in sessions
    ]


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session_endpoint(
    session_id: int,
    request: Request,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a specific session

    Args:
        session_id: Session ID to revoke
        request: FastAPI Request object
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If session not found
    """
    success = await revoke_session(db, session_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Log session revocation
    request_info = await get_request_info(request)
    await create_audit_log(
        db=db,
        action="SESSION_REVOKED",
        resource_type="Session",
        username=current_user.username,
        user_id=current_user.id,
        resource_id=str(session_id),
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


@router.get("/login-history", response_model=list[LoginHistoryResponse], status_code=status.HTTP_200_OK)
async def get_login_history(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
):
    """
    Get login history for current user

    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Maximum number of records to return

    Returns:
        List of login history records
    """
    logs = await get_user_audit_logs(db, current_user.id, limit=limit)

    return [
        LoginHistoryResponse(
            id=log.id,
            timestamp=log.timestamp,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            success=log.success,
            failure_reason=log.failure_reason,
        )
        for log in logs
    ]
