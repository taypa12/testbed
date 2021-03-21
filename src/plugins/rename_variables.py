import logging

from obsfucation import Obfuscation

logger = logging.getLogger(
    "{0}".format(__name__)
)

def obfuscate(obsfucation: Obfuscation):
    logging.info("Running {0} obsfucator".format(__name__))
    print(obsfucation.smali_files)
        