import os, sys 
from flask import Flask

base_path = os.path.dirname(__file__)
class_path = os.path.join(base_path, "classes/")
config_path = os.path.join(base_path, "dbpush/")
report_path = os.path.join(class_path, "pdfkit/")
schedule_path = os.path.join(class_path, "schedule/")
managers_path = os.path.join(class_path, "managers/")

sys.path.insert(0, base_path)
sys.path.insert(1, class_path)
sys.path.insert(2, managers_path)
sys.path.insert(3, config_path)
sys.path.insert(4, schedule_path)
sys.path.insert(5, report_path)

WSGI_PATH_PREFIX = ''

from flask import redirect, url_for
import managers, logging_managers, services, moulder_services, cms_services, wet_weight_services, packing_services, oven_services, bori_services

# import logging
# import logging.config
# from logging import getLogger, INFO, ERROR, WARNING, CRITICAL, NOTSET, DEBUG
# from concurrent_log_handler import ConcurrentRotatingFileHandler
# import os

class Config:
    def __init__(self, app, WSGI_PATH_PREFIX):
        self.app = app
        # register managers and then services
        print ' * WSGIPrefix set to %s'%WSGI_PATH_PREFIX
        self.logging_mgrs = logging_managers.register_managers(app, WSGI_PATH_PREFIX)
        self.mgrs = managers.register_managers(app, WSGI_PATH_PREFIX)
        self.srvs = services.register_services(app, WSGI_PATH_PREFIX)
        self.msrvs = moulder_services.register_services(app, WSGI_PATH_PREFIX)
        self.cmssrvs = cms_services.register_services(app, WSGI_PATH_PREFIX)
        self.wwsrvs = wet_weight_services.register_services(app, WSGI_PATH_PREFIX)
        self.packing_services = packing_services.register_services(app, WSGI_PATH_PREFIX)
        self.oven_services = oven_services.register_services(app, WSGI_PATH_PREFIX)
        self.bori_services = bori_services.register_services(app, WSGI_PATH_PREFIX)

    def reload(self):
        self.mgrs.reload()

# create application
application = Flask(__name__)
application.config['CONFIG_PATH'] = config_path
cfg = None

@application.route(WSGI_PATH_PREFIX + '/')
def root():
    return redirect(url_for('page'))

@application.route(WSGI_PATH_PREFIX + '/home')
def page():
    return application.send_static_file('index.html')

@application.route(WSGI_PATH_PREFIX + '/reload')
def reload():
    cfg.reload()
    return redirect(url_for('ct_page'))

def set_wsgi_prefix(prefix='/'):
    WSGI_PATH_PREFIX = prefix
    cfg = Config(application, WSGI_PATH_PREFIX)

if __name__ == '__main__':
    WSGI_PATH_PREFIX = '/api_analyze'
    # try:
    #     logging.config.fileConfig('logging.conf')
    #     log = getLogger()
    #     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #     print "==============================================", os.path.abspath
    #     # Use an absolute path to prevent file rotation trouble.
    #     logfile = os.path.abspath("serverlogs.log")
    #     # Rotate log after reaching 512K, keep 5 old copies.
    #     rotateHandler = ConcurrentRotatingFileHandler(logfile, "a", 512*1024, 5)
    #     log.addHandler(rotateHandler)
    #     log.setLevel(INFO)
    #     log.setLevel(ERROR)
    #     log.setLevel(WARNING)
    #     log.setLevel(CRITICAL)
    #     log.setLevel(NOTSET)
    #     log.setLevel(DEBUG)
    cfg = Config(application, WSGI_PATH_PREFIX)
    dport = int(sys.argv[1]) if len(sys.argv) > 1 else 20040
    application.run(host='0.0.0.0',port=dport,debug=True,use_reloader=True,processes=1,static_files={'/':'dist'})
    # except Exception as e:
    #     print "Exception Occured....", e
    #     log.exception("Fatal error in main exception", exc_info=True)
    #     log.exception(str(e))
    # finally:
    #     print "In Finally"
    #     log.exception("Fatal error in main finally", exc_info=True)
# else:
#     cfg = Config(application, WSGI_PATH_PREFIX)