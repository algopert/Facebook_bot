class NetworkError(Exception):
    pass


class UrlMisMatchError(Exception):
    pass


class CheckPointError(Exception):
    pass


class NotLoggedIn(Exception):
    pass


class PostUnavailable(Exception):
    pass


class AlreadyReactedError(Exception):
    """
    Exception raised when a reaction to post is already present for selected actor
    """
    pass


class ProfileTemporarilyBlockedError(Exception):
    """
    Exception raised when a user profile is blocked while reacting to a post
    """
    pass


class LoopingExpanders(Exception):
    """
    Exception raised when clicking on all expanders is stuck due to comment or post being deleted
    """
    pass


class InvalidComment(Exception):
    """
     Exception raised when clicking on all expanders is stuck due to comment had been deleted
    """
