from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Protocol, TypeIs

from django.conf import settings
from user_agents import parse

if TYPE_CHECKING:
    from django.http import HttpRequest
    from user_agents.parsers import UserAgent


# In-memory cache - shared across requests
@lru_cache(maxsize=getattr(settings, "USER_AGENTS_CACHE_SIZE", 50))
def get_user_agent(request: HttpRequest) -> UserAgent | str:
    # Tries to get UserAgent objects from cache before constructing a UserAgent
    # from scratch because parsing regexes.yaml/json (ua-parser) is slow
    if not hasattr(request, "META"):
        return ""

    ua_string = request.META.get("HTTP_USER_AGENT", "")

    if not isinstance(ua_string, str):
        ua_string = ua_string.decode("utf-8", "ignore")
    user_agent = parse(ua_string)
    return user_agent


def get_and_set_user_agent(request: HttpRequest) -> UserAgent | str:
    # If request already has ``user_agent``, it will return that, otherwise
    # call get_user_agent and attach it to request so it can be reused
    if not request:
        return parse("")
    elif not has_user_agent(request):
        request.user_agent = get_user_agent(request)

    assert has_user_agent(request)
    return request.user_agent


class HasUserAgent(Protocol):
    @property
    def user_agent(self) -> UserAgent: ...


def has_user_agent(request: object) -> TypeIs[HasUserAgent]:
    """TypeGuard, adds HasUserAgent type if returns True"""
    return hasattr(request, "user_agent")
