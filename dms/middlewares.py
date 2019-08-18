import typing

from passlib.hash import pbkdf2_sha256 as hasher
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    BaseUser,
    SimpleUser,
    UnauthenticatedUser,
)
from starlette.requests import Request

from dms import messages, state


class AdminAuthenticationBackend(AuthenticationBackend):
    async def authenticate(
        self, request: Request
    ) -> typing.Tuple[AuthCredentials, BaseUser]:

        auth = request.session.pop("auth", None)
        if auth:
            sun, spw = state.items.storage().split(":", 1)
            aun, apw = auth.split(":", 1)
            if sun and sun == aun and hasher.verify(apw, spw):
                request.session.update(user=hasher.hash(auth))
                messages.add(
                    request=request,
                    text="Logged in successfully",
                    type=messages.SUCCESS,
                )
                return AuthCredentials(scopes=["authenticated"]), SimpleUser("admin")
            messages.add(
                request=request, text="Invalid credentials", type=messages.DANGER
            )

        if "user" not in request.session:
            return AuthCredentials(scopes=["anonymous"]), UnauthenticatedUser()

        user = request.session["user"]
        if hasher.identify(user):
            return AuthCredentials(scopes=["authenticated"]), SimpleUser("admin")

        request.session.pop("user")
        return AuthCredentials(scopes=["anonymous"]), UnauthenticatedUser()
