"""[CARBON-RETEST] Run ReActDroid on one case of the CARBON benchmark.

This is main/run_recdroid.py (Main.__init__ / step / run) with only the changes
the harness needs:

  * crash_info is read from a JSON file instead of the ReCDroid CSV;
  * install_app() is not called: the harness installs and launches the APK the
    same way for every tool;
  * the loop also stops at a wall-clock deadline (the shared 1,800 s budget,
    extended by any time spent waiting out Gemini quota errors);
  * if the page observed at the start of a step is outside the app or empty,
    upstream's own recovery (relaunch_app) is applied first. Upstream only
    applies it to the page reached after an action; on an out-of-app start page
    its choose_action() raises KeyError('page_name'), which is what the
    previous run hit 1,662 times.

There is no FaxRes static-analysis output for these apps, so process_fax_res()
starts from an empty page model and predict() skips crash-page prediction, as
upstream does when the folder is missing.

Usage (from ReActDroid/main):  python run_case.py <case.json>
"""
import json
import os
import sys
import time

sys.path.append("..")
from tool.action import Action
from tool.environment import EmulatorEnv
from tool.memory import Memory
from tool.observe import Observer
from tool.process_static_analysis import process_fax_res
from llm.chat import Chat
from predict_page.predict_crash_page import predict
from main.utils import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s[%(name)s:%(lineno)s]: %(message)s')

# Folders upstream expects to exist (normally shipped in its Data archive).
DATA_DIRS = ["../Data/Temp", "../Data/Temp/backup", "../Data/Temp/logcat", "../Data/Temp/chat_log",
             "../Data/Temp/page_prompts", "../Data/AppState", "../Data/FaxRes"]


def prepare_data_dirs():
    for d in DATA_DIRS:
        os.makedirs(d, exist_ok=True)
    # get_current_screen() copies the previous screen to backup/ before taking
    # a new one, so both files must exist before the first observation.
    for placeholder in ["../Data/Temp/cur_screen.png", "../Data/Temp/cur_screen.xml"]:
        if not os.path.exists(placeholder):
            open(placeholder, "w").close()


def quota_wait():
    """Seconds spent waiting out Gemini quota errors; not counted against the budget."""
    try:
        from harness.gemini_client import usage_totals
        return usage_totals(os.environ.get("BASELINE_USAGE_FILE"))["backoff_s"]
    except Exception:
        return 0


class Main:
    def __init__(self, crash_info: dict):
        perform_logcat()
        self.env = EmulatorEnv(crash_info)
        self.memory = Memory(crash_info, self.env)
        fax_res = process_fax_res("../Data/FaxRes/" + crash_info["app_name"], self.memory, crash_info)
        predict_res = predict(crash_info["app_name"], crash_info["crash_desc"])
        if len(predict_res.keys()) > 0:
            predict_crash_page_id = predict_res["crash_page_id"]
            confidence = predict_res["Confidence"]
            if confidence == 5:
                crash_info["crash_page_id"] = predict_crash_page_id
        self.observer = Observer(self.env, self.memory, crash_info)
        self.action = Action(self.env, self.memory, self.observer)
        self.chat = Chat(self.memory, crash_info)

    def step(self):
        observe_res = self.observer.observe(add_visit_time=True)
        page_id = observe_res["page_id"]
        if page_id == "out of app" or page_id == "empty page":
            # [CARBON-RETEST] Upstream's recovery, applied before choose_action
            # (see module docstring).
            print("[ReActDroid-harness] RECOVER", page_id)
            self.env.relaunch_app()
            return
        choose_result = self.chat.choose_action(observe_res)
        choose_action_key = choose_result["action"]
        self.action.perform_action(page_id, choose_action_key)
        dst_observe = self.observer.observe(add_visit_time=False)
        dst_page = dst_observe["page_id"]
        self.memory.update_action(page_id, choose_action_key, dst_page)
        if dst_observe["page_id"] == "out of app" or dst_observe["page_id"] == "empty page":
            self.env.relaunch_app()
        elif choose_action_key != "Back to previous page":
            self.memory.stg.update_previous_page(dst_page, page_id)

    def run(self, deadline: float):
        time.sleep(3)
        start_time = time.time()
        for i in range(10000):
            if time.time() >= deadline + quota_wait():
                print("[ReActDroid-harness] DEADLINE after", i, "steps")
                break
            logging.info("Step " + str(i + 1))
            self.step()
            if check_crash():
                print("[ReActDroid-harness] CRASH_DETECTED step", i + 1)
                break
        end_time = time.time()
        print("Reproducing time:", end_time - start_time)


if __name__ == '__main__':
    with open(sys.argv[1], encoding="utf-8") as f:
        crash_info = json.load(f)
    budget = float(os.environ.get("REACTDROID_BUDGET_S", "1800"))
    deadline = float(os.environ.get("REACTDROID_DEADLINE", time.time() + budget))
    prepare_data_dirs()
    Main(crash_info).run(deadline)
