
import logging
import os
import secrets
import string
from typing import List, Union

# from obfuscapk import util
from tool import Apktool

class Obfuscation(object):
    """
    This class holds the details and the internal state of an obfuscation operation.
    When obfuscating a new application, an instance of this class has to be instantiated
    and passed to all the obfuscators (in sequence).
    """

    def __init__(
        self,
        apk_path: str,
        working_dir_path: str = None,
        obfuscated_apk_path: str = None,
    ):
        self.logger = logging.getLogger(__name__)

        self.apk_path: str = apk_path
        self.working_dir_path: str = working_dir_path
        self.obfuscated_apk_path: str = obfuscated_apk_path

        # Random string (32 chars long) generation with ASCII letters and digits
        self.encryption_secret = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
        )

        self.logger.debug(
            'Auto-generated random secret key for encryption: "{0}"'.format(
                self.encryption_secret
            )
        )

        # Obsfuscation
        self.obsfucation: List[str] = []

        # How many obfuscators will add new fields/methods during this obfuscation
        # operation.
        self.obfuscators_adding_fields: int = 0
        self.obfuscators_adding_methods: int = 0

        self.is_decompiled: bool = False
        self.decompiled_apk_path: Union[str, None] = None
        self.manifest_file: Union[str, None] = None
        self.smali_files: List[str] = []
        self.multidex_smali_files: List[List[str]] = [] 
        self.native_lib_files: List[str] = []

        # Check if the apk file to obfuscate is a valid file.
        if not os.path.isfile(self.apk_path):
            self.logger.error('Unable to find file "{0}"'.format(self.apk_path))
            raise FileNotFoundError('Unable to find file "{0}"'.format(self.apk_path))

        # If no working directory is specified, use a new directory in the same
        # directory as the apk file to obfuscate.
        if not self.working_dir_path:
            self.working_dir_path = os.path.join(
                os.path.dirname(self.apk_path), "obfuscation_working_dir"
            )
            self.logger.debug(
                "No working directory provided, the operations will take place in the "
                'same directory as the input file, in the directory "{0}"'.format(
                    self.working_dir_path
                )
            )

        if not os.path.isdir(self.working_dir_path):
            try:
                os.makedirs(self.working_dir_path, exist_ok=True)
            except Exception as e:
                self.logger.error(
                    'Unable to create working directory "{0}": {1}'.format(
                        self.working_dir_path, e
                    )
                )
                raise

        # If the path of the output obfuscated apk is not specified, save it in the
        # working directory.
        if not self.obfuscated_apk_path:
            self.obfuscated_apk_path = "{0}_obfuscated.apk".format(
                os.path.join(
                    self.working_dir_path,
                    os.path.splitext(os.path.basename(self.apk_path))[0],
                )
            )
            self.logger.debug(
                "No obfuscated apk path provided, the result will be saved "
                'as "{0}"'.format(self.obfuscated_apk_path)
            )

    def decompile_apk(self) -> None:

        if self.is_decompiled: return

        # The input apk will be decompiled with apktool.
        apktool: Apktool = Apktool()

        # <working_directory>/<apk_path>/
        self.decompiled_apk_path = os.path.join(
            self.working_dir_path,
            os.path.splitext(os.path.basename(self.apk_path))[0],
        )
        try:
            apktool.decode(self.apk_path, self.decompiled_apk_path, force=True)

            # Path to the decompiled manifest file.
            self.manifest_file = os.path.join(
                self.decompiled_apk_path, "AndroidManifest.xml"
            )

            # A list containing the paths to all the smali files obtained with
            # apktool.
            self.smali_files = [
                os.path.join(root, file_name)
                for root, dir_names, file_names in os.walk(self.decompiled_apk_path)
                for file_name in file_names
                if file_name.endswith(".smali")
            ]

            # if self.ignore_libs:
            #     Normalize paths for the current OS ('.join(x, "")' is used to add
            #     a trailing slash).
            #     libs_to_ignore = list(
            #         map(
            #             lambda x: os.path.join(os.path.normpath(x), ""),
            #             util.get_libs_to_ignore(),
            #         )
            #     )
            #     filtered_smali_files = []

            #     for smali_file in self.smali_files:
            #         # Get the path without the initial part <root>/smali/.
            #         relative_smali_file = os.path.join(
            #             *(
            #                 os.path.relpath(
            #                     smali_file, self.decompiled_apk_path
            #                 ).split(os.path.sep)[1:]
            #             )
            #         )
            #         # Get only the smali files that are not part of known third
            #         # party libraries.
            #         if not any(
            #             relative_smali_file.startswith(lib)
            #             for lib in libs_to_ignore
            #         ):
            #             filtered_smali_files.append(smali_file)

            #     self.smali_files = filtered_smali_files

            # Sort the list of smali files to always have the list in the same
            # order.
            self.smali_files.sort()

            # Check if multidex.
            if os.path.isdir(
                os.path.join(self.decompiled_apk_path, "smali_classes2")
            ):
                self.is_multidex = True

                smali_directories = ["smali"]
                for i in range(2, 15):
                    smali_directories.append("smali_classes{0}".format(i))

                for smali_directory in smali_directories:
                    current_directory = os.path.join(
                        self.decompiled_apk_path, smali_directory, ""
                    )
                    if os.path.isdir(current_directory):
                        self.multidex_smali_files.append(
                            [
                                smali_file
                                for smali_file in self.smali_files
                                if smali_file.startswith(current_directory)
                            ]
                        )

            # A list containing the paths to the native libraries included in the
            # application.
            self.native_lib_files = [
                os.path.join(root, file_name)
                for root, dir_names, file_names in os.walk(
                    os.path.join(self.decompiled_apk_path, "lib")
                )
                for file_name in file_names
                if file_name.endswith(".so")
            ]

            # Sort the list of native libraries to always have the list in the
            # same order.
            self.native_lib_files.sort()

        except Exception as e:
            self.logger.error("Error during apk decoding: {0}".format(e))
            raise
        else:
            self.is_decompiled = True

    def compile_apk(self) -> None:

        if not self.is_decompiled:
            self.decode_apk()

        # The obfuscated apk will be built with apktool.
        apktool: Apktool = Apktool()

        try:
            apktool.build(self.decompiled_apk_path, self.obfuscated_apk_path)
        except Exception as e:
            self.logger.error("Error during apk building: {0}".format(e))
            raise