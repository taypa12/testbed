import logging
from typing import List, Set

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class VariableRename(obfuscator_category.IRenameObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()

        self.ignore_package_names = []

        self.is_adding_variables = True

        self.max_variables_to_add = 0
        self.added_variables = 0

    def rename_variable(self, variable_name: str) -> str:
        variable_md5 = util.get_string_md5(variable_name)
        return "f{0}".format(variable_md5.lower()[:8])

    def get_sdk_class_names(self, smali_files: List[str]) -> Set[str]:
        class_names: Set[str] = set()
        for smali_file in smali_files:
            with open(smali_file, "r", encoding="utf-8") as current_file:
                for line in current_file:
                    class_match = util.class_pattern.match(line)
                    if class_match:

                        if class_match.group("class_name").startswith(
                                ("Landroid", "Ljava")
                        ):
                            class_names.add(class_match.group("class_name"))

                        break
        return class_names

    def rename_variable_declarations(
            self, smali_files: List[str], interactive: bool = False
    ) -> Set[str]:
        renamed_variables: Set[str] = set()

        for smali_file in util.show_list_progress(
                smali_files,
                interactive=interactive,
                description="Renaming variables declarations",
        ):
            with util.inplace_edit_file(smali_file) as (in_file, out_file):
                class_name = None
                for line in in_file:
                    ignore = False

                    if not class_name:
                        class_match = util.class_pattern.match(line)
                        if class_match:
                            class_name = class_match.group("class_name")

                    variable_match = util.field_pattern.match(line)

                    if class_name.startswith(tuple(self.ignore_package_names)):
                        ignore = True

                    if variable_match:
                        variable_name = variable_match.group("variable_name")

                        if not ignore and "$" not in variable_name:

                            line = line.replace(
                                "{0}:".format(variable_name),
                                "{0}:".format(self.rename_variable(variable_name)),
                            )
                            out_file.write(line)

                            if self.added_variables < self.max_variables_to_add:
                                for _ in range(util.get_random_int(1, 4)):
                                    out_file.write("\n")
                                    out_file.write(
                                        line.replace(
                                            ":",
                                            "{0}:".format(util.get_random_string(8)),
                                        )
                                    )
                                    self.added_variables += 1

                            variable = "{variable_name}:{variable_type}".format(
                                variable_name=variable_match.group("variable_name"),
                                variable_type=variable_match.group("variable_type"),
                            )
                            renamed_variables.add(variable)
                        else:
                            out_file.write(line)
                    else:
                        out_file.write(line)

        return renamed_variables

    def rename_variable_references(
            self,
            variables_to_rename: Set[str],
            smali_files: List[str],
            sdk_classes: Set[str],
            interactive: bool = False,
    ):
        for smali_file in util.show_list_progress(
                smali_files,
                interactive=interactive,
                description="Renaming variable references",
        ):
            with util.inplace_edit_file(smali_file) as (in_file, out_file):
                for line in in_file:

                    variable_usage_match = util.variable_usage_pattern.match(line)
                    if variable_usage_match:
                        variable = "{variable_name}:{variable_type}".format(
                            variable_name=variable_usage_match.group("variable_name"),
                            variable_type=variable_usage_match.group("variable_type"),
                        )
                        class_name = variable_usage_match.group("variable_object")
                        variable_name = variable_usage_match.group("variable_name")
                        if variable in variables_to_rename and (
                                not class_name.startswith(("Landroid", "Ljava"))
                                or class_name in sdk_classes
                        ):

                            out_file.write(
                                line.replace(
                                    "{0}:".format(variable_name),
                                    "{0}:".format(self.rename_variable(variable_name)),
                                )
                            )
                        else:
                            out_file.write(line)
                    else:
                        out_file.write(line)

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        self.ignore_package_names = obfuscation_info.get_ignore_package_names()

        try:
            sdk_class_declarations = self.get_sdk_class_names(
                obfuscation_info.get_smali_files()
            )
            renamed_variable_declarations: Set[str] = set()

            self.max_variables_to_add = (
                obfuscation_info.get_remaining_variables_per_obfuscator()
            )
            self.added_variables = 0

            if obfuscation_info.is_multidex():
                for index, dex_smali_files in enumerate(
                        util.show_list_progress(
                            obfuscation_info.get_multidex_smali_files(),
                            interactive=obfuscation_info.interactive,
                            unit="dex",
                            description="Processing multidex",
                        )
                ):
                    self.max_variables_to_add = (
                        obfuscation_info.get_remaining_variables_per_obfuscator()[index]
                    )
                    self.added_variables = 0
                    renamed_variable_declarations.update(
                        self.rename_variable_declarations(
                            dex_smali_files, obfuscation_info.interactive
                        )
                    )
            else:
                renamed_variable_declarations = self.rename_variable_declarations(
                    obfuscation_info.get_smali_files(), obfuscation_info.interactive
                )

            self.rename_variable_references(
                renamed_variable_declarations,
                obfuscation_info.get_smali_files(),
                sdk_class_declarations,
                obfuscation_info.interactive,
            )

        except Exception as e:
            self.logger.error(
                'Error during execution of "{0}" obfuscator: {1}'.format(
                    self.__class__.__name__, e
                )
            )
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
