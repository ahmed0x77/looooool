# app.py 


import os
if (__name__ != "__main__"): # Check if its runing inside `railway host`
    from gevent import monkey 
    monkey.patch_all() # This  cant run in windows cuz its frezzing the apis
    os.environ['PRODUCTION_SERVER'] = 'true'
    print('PRO server starting....000000004 man fuck')
else:
    print('DEV server starting....000000001')
    os.environ['PRODUCTION_SERVER'] = 'false'

import os
os.environ['TZ'] = 'UTC' # to fix warning from flask_apscheduler


import logging
import sys
import colorama
from flask_caching import Cache
from flask_apscheduler import APScheduler # Import APScheduler
from flask import Flask, Request, jsonify, request, send_from_directory
import binascii
import warnings



app_cache = False

app = Flask(__name__)

#--------------- DDOS ATTACK PROTECTION (FROM RECIVING LARGE FILES) ------------------
# 1. App‑level body limit (rejects any request over 16 MB with a 413)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# 2. Further multipart/Form limits
Request.max_form_memory_size = 500 * 1024   # 500 KB for non‑file fields
Request.max_form_parts      = 1_000         # up to 1,000 multipart parts

#----------------- Initialize Scheduler -------------------
scheduler = APScheduler()
app.config['SCHEDULER_API_ENABLED'] = True
aps_logger = logging.getLogger('apscheduler.scheduler') # dont show `scheduler:Added job ` message
aps_logger.setLevel(logging.WARNING)  # dont show `scheduler:Added job ` message
scheduler.init_app(app)
scheduler.start()
import Tasks # leave it here to load the tasks



warnings.filterwarnings("ignore", message=".*CACHE_TYPE is set to null, caching is effectively disabled.*") # HIDE CACHE WARNING ABOUT ITS DISABLED
cache = Cache()
if app_cache:
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
else:
    cache.init_app(app, config={'CACHE_TYPE': 'null'})


#-- this is to make the cache remember different body for the api
def make_cache_key(*args, **kwargs): 
    # Create a cache key based on the request path and its body 
    request_data = request.get_data(as_text=True)
    return request.path + request_data

app.secret_key = binascii.hexlify(os.urandom(24)).decode() #مش عارف هو مهم اوي ولا لا


# @app.before_request
# def log_request_info():
#     logging.info(f"Endpoint called: {request.endpoint}, Method: {request.method}, Path: {request.path}")

@app.route('/favicon.ico') #this fix that when calling
def favicon():
    return send_from_directory('imgs', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

#------ Show a better error message in the console ------
import traceback
from colorama import Fore, Style
colorama.init(autoreset=True)
@app.errorhandler(Exception)
def handle_user_code_exception(e):
    # Extract the traceback frames
    tb_list = traceback.extract_tb(e.__traceback__)
    short_trace = Fore.YELLOW + "*** Traceback (most recent call last) ***\n" + Style.RESET_ALL
    for frame in tb_list:
        if not "Programs\\Python" in frame.filename and not "lib\\" in frame.filename:
            short_trace += Fore.CYAN + f'File "{frame.filename.replace(sys.path[0], "")}", line {frame.lineno}, in {frame.name}\n' + Style.RESET_ALL
            if frame.line:
                short_trace += Fore.GREEN + f"   {frame.line.strip()}\n" + Style.RESET_ALL
    short_trace += Fore.RED + f"\n{type(e).__name__}: {e}\n" + Style.RESET_ALL
    logging.error(short_trace)
    return jsonify({"error": "Something went wrong"}), 500

#### other way of hide unnessary error #####
# logging.getLogger('werkzeug').setLevel(logging.ERROR)
# # Remove or adjust the traceback limit so we can get one frame's info
# sys.tracebacklimit = 1  # Shows only the last frame


from flask import request
@app.route("/speed_test_POST", methods=["POST"])
def speed_test_POST():
    recived_data = request.get_json()
    invite_code = recived_data.get('invite_code', None)
    return jsonify({"invite_code": invite_code}), 200,

@app.route("/speed_test_GET", methods=["GET"])
def speed_test_GET():
    invite_code = request.args.get('invite_code', None)
    return jsonify({"invite_code": invite_code}), 200



@app.route("/crash_me2", methods=['POST', 'GET'])
def _crash_main_appuu():
    import os
    import signal
    import logging
    logging.warning("RemoteApp: /crash_me endpoint called. Sending SIGKILL.")
    os.kill(os.getpid(), signal.SIGKILL)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
