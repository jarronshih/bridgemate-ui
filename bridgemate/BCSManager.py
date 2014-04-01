from utils.Logger import get_logger
from utils.config import BCS_PATH
from subprocess import Popen

logger = get_logger()

class BCSManager(object):
    def __init__(self, bws_path, bcs_path=BCS_PATH):
        global logger
        logger = get_logger()
        logger.debug("Init BCSManager")
        self.bcs_path = bcs_path
        self.bws_path = bws_path
        self.process = None
        #logger.debug("Open Bridgemate Control Software")

    def command(self, opts=[]):
        self.close()

        cmd = '"%s" %s' % (self.bcs_path, ' '.join(opts))
        logger.debug("BCS cmd(%s)" % cmd)
        self.process = Popen(cmd)

    def open(self):
        self.command(["/f:[%s]" % self.bws_path, "/m", "/s","/r"])

    def close(self):
        if self.process:
            self.process.terminate()
        self.process = None

    def is_alive(self):
        return self.process and self.process.poll() is None
