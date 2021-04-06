import logging
import utils
import os
import fnmatch
import string
from obsfucation import Obfuscation
from typing import List, Set

import re
import random

logger = logging.getLogger(
    "{0}".format(__name__)
)
list=["x,v,c,n"]



def obfuscate(obfuscation: Obfuscation):
    logging.info("Running {0} obsfucator".format(__name__))
    try:
        for smali_file in obfuscation.smali_files:
            with utils.edit_file(smali_file) as (in_file, out_file):
                skip_lines = False
                class_name = None
                for line in in_file:
                    if skip_lines:
                        out_file.write(line)
                        continue
                    if not class_name:
                        class_match = utils.class_pattern.match(line)
                        # If this is an enum class, skip it.
                        if " enum " in line:
                            skip_remaining_lines = True
                            out_file.write(line)
                            continue
                        if line.startswith("# virtual methods"):
                            skip_remaining_lines = True
                            out_file.write(line)
                            continue
                        # Method declared in class.
                        method_match = utils.method_pattern.match(line)
                        if (
                                method_match
                                and "<init>" not in line
                                and "<clinit>" not in line
                                and " native " not in line
                                and " abstract " not in line
                                and " onCreate" not in line
                                and "Landroid/os" not in line
                                and "Ljava/lang" not in line
                                and "Landroidx" not in line
                        ):
                            # Create lists with random parameters to be added to the method
                            # signature. Add 3 overloads for each method and for each overload
                            # use 4 random params.
                            for params in list:
                                new_param = "".join(params)
                                # Update parameter list and add void return type.
                                overloaded_signature = line.replace(
                                    "({0}){1}".format(
                                        method_match.group("method_param"),
                                        method_match.group("method_return"),
                                    ),
                                    "({0}{1})V".format(
                                        method_match.group("method_param"), new_param
                                    ),
                                )
                                out_file.write(overloaded_signature)
                                out_file.write("\t.locals 0\n\n"
                                               "\tconst/16 p1, 0x2a\n\n")
                                out_file.write("\treturn-void\n\n")
                                out_file.write(".end method\n\n\n")



                            # Print original method.
                            out_file.write(line)
                        else:
                            out_file.write(line)

    except Exception as e:
        logger.error(
            'Error during execution of "{0}" obfuscator: {1}'.format(
                __name__, e
            )
        )
        raise
