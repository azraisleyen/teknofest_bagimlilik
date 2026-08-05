from .base import *  # noqa: F403,F401

DEBUG = True
ENABLE_DISPLAY_UI = env_bool("ENABLE_DISPLAY_UI", True)  # noqa: F405
ENABLE_DISPLAY_SIMULATOR = env_bool("ENABLE_DISPLAY_SIMULATOR", True)  # noqa: F405
if ENABLE_DEMO_UI:
    INSTALLED_APPS += ["apps.demo"]  # noqa: F405
