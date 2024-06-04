import os


def get_save_path():
    if os.getenv("BENCHAI_SAVEDIR"):
        save_path = os.getenv("BENCHAI_SAVEDIR")
    else:
        save_path = os.path.join(os.path.expanduser("~"), ".cache", "benchai")

    pth = os.path.join(
        save_path, "agent", "sessions"
    )

    return pth


def get_live_session_path(session_name):

    pth = os.path.join(
        get_save_path(), session_name
    )

    return pth
