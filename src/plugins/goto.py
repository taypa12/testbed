import logging
import utils
from obsfucation import Obfuscation
import re

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
                    # Only add a GOTO if the Method is not abstract or native
                    if (
                            line.startswith(".method ") and " abstract " not in line
                            and " native " not in line and not control
                    ):
                        out_file.write(line)
                        control = True

                    # Checks for a method and validates if the control is True
                    elif control and re.search(r"\s+\.locals\s(?P<local_count>\d+)", line):
                        out_file.write(line)
                        out_file.write('\n\tgoto/32 :GotoEND\n')        # Jump to 'GotoEND' Label
                        out_file.write('\n\t:GotoStart\n')              # Add a Label for Jumping

                    # Checks for the end of a method and validates if the control is True
                    elif control and re.search(r'^([ ]*?)\.end method', line):
                        out_file.write("\n\t:GotoEND\n")                # Add a Label for Jumping called GotoEND
                        out_file.write("\n\tgoto/32 :GotoStart\n")      # Jump to 'GotoStart' Label
                        out_file.write(line)
                        control = False                                 # Turn off control to prevent any modification

                    # Write out line as per normal if no match
                    else:
                        out_file.write(line)

    except Exception as e:
        logger.error(
            'Error during execution of "{0}" obfuscator: {1}'.format(
                __name__, e
            )
        )
        raise


