import logging
import utils
from obsfucation import Obfuscation

logger = logging.getLogger(
    "{0}".format(__name__)
)


def obfuscate(obsfucation: Obfuscation):
    logging.info("Running {0} obsfucator".format(__name__))
    try:
        for smali_file in obsfucation.smali_files:
            with utils.edit_file(smali_file) as (in_file, out_file):
                control = False                        # Control for when to Insert respective Obfuscation.
                for line in in_file:
                    if (
                            line.startswith(".method ") and " abstract " not in line
                            and " native " not in line and not control
                    ):
                        out_file.write(line)
                        control = True
                        print(line)

                    else:
                        out_file.write(line)


    except Exception as e:
        logger.error(
            'Error during execution of "{0}" obfuscator: {1}'.format(
                __name__, e
            )
        )
        raise

    # print(obsfucation.smali_files)
