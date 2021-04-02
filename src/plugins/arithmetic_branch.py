import utils
from obsfucation import Obfuscation
import re
import logging
import random
import string

logger = logging.getLogger(
    "{0}".format(__name__)
)


def obfuscate(obfuscation: Obfuscation):
    logging.info('Running "{0}" obfuscator'.format(__name__))

    try:
        for smali_file in obfuscation.smali_files:
            with utils.edit_file(smali_file) as (in_file, out_file):
                edit_method = False  # Flag that determines when to edit a method by inserting the obfuscation
                start_label = None  # Set the start_label to null
                end_label = None  # Set the end_label to null

                # Loop through the lines of text or data read from the input file
                for line in in_file:
                    # Check if it is a method that is not abstract or native and the flag edit_method is False
                    if (line.startswith(
                            ".method ") and " abstract " not in line and " native " not in line and not edit_method):

                        # Beginning of the method. We are now entering the method
                        out_file.write(line)  # Write the line of text or data to the output file
                        edit_method = True  # set edit_method flag to True. This allows the obfuscation to take place

                    # Checks if the end of the method has been reached and if edit_method flag is True
                    elif line.startswith(".end method") and edit_method:
                        # End of the method. We are now exiting the method

                        # Check if start_label and end_label are not null(None)
                        if start_label and end_label:
                            out_file.write("\t:{0}\n".format(
                                end_label))  # Insert the string end_label at the end of the method. This label marks the beginning of a section or block of code
                            out_file.write("\tgoto/32 :{0}\n".format(
                                start_label))  # Insert the 'goto' instruction and the string start label at the end of the method. When this code is executed it will jump to the section marked by this label
                            start_label = None  # Set the start_label to null
                            end_label = None  # Set the end_label to null-
                        out_file.write(line)  # Write the line of text or data to the output file
                        edit_method = False  # Set the edit_method flag to False

                    # Checks if edit_method flag is True
                    elif edit_method:
                        # We are now inside the method
                        out_file.write(line)  # Write the line of text or data to the output file
                        match = re.compile(r"\s+\.locals\s(?P<local_count>\d+)").match(
                            line)  # If zero or more characters at the beginning of string match the regular expression pattern, a corresponding match object is returned. If the string does not match the pattern, None is returned

                        # Check the number of registers available(for example: .locals 5)
                        if match and int(match.group("local_count")) >= 2:
                            # If two or more registers are available, we add a fake branch at the beginning of the method
                            # One branch will continue from the beginning of the method where it was added
                            # The other branch will go to the end of the method and it will then be returned to the beginning through a 'goto' instruction

                            v0 = random.randint(1, 32)  # Set a random integer value between 1 and 32 to v0
                    v1 = random.randint(1, 32)  # Set a random integer value between 1 and 32 to v1

                    start_label = "".join(random.choices(string.ascii_letters,
                                                         k=16))  # Set a string with random sequence of ascii characters of length 16. This will be used for the start label
                end_label = "".join(random.choices(string.ascii_letters,
                                                   k=16))  # Set a string with random sequence of ascii characters of length 16. This will be used for the end label
                tmp_label = "".join(random.choices(string.ascii_letters,
                                                   k=16))  # Set a string with random sequence of ascii characters of length 16. This will be used for the temporary label

                out_file.write("\n\tconst v0, {0}\n".format(
                    v0))  # Write to the output file an instruction that will assign value in variable v0 to the register v0 (for example: const v0, 12)
                out_file.write("\tconst v1, {0}\n".format(
                    v1))  # Write to the output file an instruction that will assign value in variable v1 to the register v1 (for example: const v1, 5)
                out_file.write(
                    "\tadd-int v0, v0, v1\n")  # Write to the output file an operation instruction that will add the values in registers v0 and v1 and insert the result in register v0 (for example: v0 = v0 + v1)
                out_file.write(
                    "\trem-int v0, v0, v1\n")  # Write to the output file an operation instruction that will calculate the modulus of values in registers v0 and v1 and insert the result in register v0 (for example: v0 = v0 % v1)
                out_file.write("\tif-gtz v0, :{0}\n".format(
                    tmp_label))  # Write to the output file a value judgement or conditional instruction that will check if the value if the value in register v0 is greater than zero. If True the condition will be executed by jumping to the section marked by the label 'tmp_label'. If False the instruction below it will be executed(for example:if-gtz v0, :condition)
                out_file.write("\tgoto/32 :{0}\n".format(
                    end_label))  # Write to the output file a 'goto' instruction that will cause the execution of code to jump to the section marked by the label 'end_label' (for example: goto :goto_label)
                out_file.write("\t:{0}\n".format(
                    tmp_label))  # Write to the output file the label 'tmp_label' (for example: :WejHkfuIndHKsjDf)
                out_file.write("\t:{0}\n".format(
                    start_label))  # Write to the output file the label 'start_label' (for example: :kguIOmfjtpqhGZBj)

        else:
            out_file.write(line)  # Write the line of text or data to the output file

    except Exception as e:
        logger.error(
            'Error during execution of "{0}" obfuscator: {1}'.format(
                __name__, e
            )
        )
    raise
