import re
from dataclasses import dataclass
from subprocess import PIPE, run
from sys import path
from typing import List

import obspython as obs
from flupy import flu

import window_control

# ------------------------------------------------------------

WINDOW_CAPTURE_XCOMPOSITE = "xcomposite_input"


def script_description():
    return "Window capture for dynamic window titles"


def script_properties():
    """
    Called to define user properties associated with the script. These
    properties are used to define how to show settings properties to a user.
    """
    props = obs.obs_properties_create()
    p = obs.obs_properties_add_list(
        props,
        "source",
        "Window Capture Source",
        obs.OBS_COMBO_TYPE_LIST,
        obs.OBS_COMBO_FORMAT_STRING,
    )
    if (sources := obs.obs_enum_sources()) is not None:
        for source in sources:
            source_id = obs.obs_source_get_id(source)
            if source_id == WINDOW_CAPTURE_XCOMPOSITE:
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_text(
        props,
        "executable",
        "Executable to Match (e.g. whatsapp.exe)",
        obs.OBS_TEXT_DEFAULT,
    )
    obs.obs_properties_add_text(
        props,
        "window_match",
        "Regex for Title to Match (e.g. .*video call",
        obs.OBS_TEXT_DEFAULT,
    )
    obs.obs_properties_add_button(props, "button", "Refresh", on_press_button)

    return props


def on_press_button(props, prop):
    capture_window()


def script_update(settings):
    """
    Called when the script’s settings (if any) have been changed by the user.
    """
    global config_source_name, config_executable, config_window_match, config_class
    print("Settings updated")
    config_source_name = obs.obs_data_get_string(settings, "source")
    config_executable = obs.obs_data_get_string(settings, "executable")
    config_window_match = obs.obs_data_get_string(settings, "window_match")
    # config_class = obs.obs_data_get_string(settings, "class")


def match_window(executable: str, re_title: str):
    def is_match(window: window_control.Window):
        return (
            window.executable_path.lower() == executable.lower()
            and re.search(re_title, window.title) is not None
        )

    print(f"Matching executable {executable} and window title: {re_title}")
    for window in window_control.create_windowlist():
        if is_match(window):
            return window
    return None


def on_event(event):
    #if event == obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:
    capture_window()


def capture_window():
    global config_source_name, config_executable, config_window_match
    print("*** Capturing Window ***")

    def is_source_match(source) -> bool:
        return (
            obs.obs_source_get_unversioned_id(source)
            == WINDOW_CAPTURE_XCOMPOSITE
            and obs.obs_source_get_name(source) == config_source_name
        )

    current_scene = obs.obs_frontend_get_current_scene()
    scene = obs.obs_scene_from_source(current_scene)
    scene_items = obs.obs_scene_enum_items(scene)
    sources = [
        obs.obs_sceneitem_get_source(scene_item) for scene_item in scene_items
    ]
    for source in sources:
        if is_source_match(source):
            print(f"Source matched: {obs.obs_source_get_name(source)}")
            window = match_window(config_executable, config_window_match)
            if window is not None:
                print(f"Found new window: {window.title}")

                cur_settings = obs.obs_source_get_settings(source)
                import json
                from pprint import pprint

                jsonData = json.loads(obs.obs_data_get_json(cur_settings))
                #pprint(jsonData)
                old_window_text: str = obs.obs_data_get_string(
                    cur_settings, "window"
                )
                new_window_text: str = f"{window.windowID}\r\n{window.title}\r\n{window.wmClass.name}"
                # if old_window_text != new_window.title:
                print(f"{old_window_text} -> {window.title}")
                obs.obs_data_set_string(
                    cur_settings, "capture_window", new_window_text
                )
                obs.obs_data_set_string(
                    cur_settings, "window", new_window_text
                )
                print("Updating settings for source")
                obs.obs_source_update(source, cur_settings)
                obs.obs_data_release(cur_settings)

    obs.sceneitem_list_release(scene_items)


def script_load(settings):
    print("Window Capture Script loaded")
    obs.obs_frontend_add_event_callback(on_event)
    capture_window()
