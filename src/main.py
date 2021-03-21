import logging
import os

from obsfucation import Obfuscation

logger = logging.getLogger(
    "[{0}]".format(__name__)
)

if "LOG_LEVEL" in os.environ:
    log_level = os.environ["LOG_LEVEL"]
else:
    # By default log only the error messages.
    log_level = logging.INFO

# For the plugin system log only the error messages and ignore the log level set by
# the user.
logging.getLogger("yapsy").level = logging.ERROR

# Logging configuration.
logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s][%(name)s][%(funcName)s()] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    level=log_level,
)

import sys, getopt
from os import path
from pathlib import Path

import importlib 

input_file = ''
plugins_module = "plugins"
plugins = ["rename_variables"]

root_dir = path.dirname(path.dirname(path.realpath(__file__)))
temp_dir = path.join(root_dir, "tmp")
output_apk = path.join(root_dir, "output.apk")
Path(temp_dir).mkdir(parents=True, exist_ok=True)

def print_help():
	print('Usage: test.py <inputfile> <outputfile>')

def parse_args(argv):
	logger.info("Parsing {0} args".format(len(argv)))
	global input_file
	global output_apk
	global plugins

	argv_len = len(argv)
	
	if (argv_len == 0): 
		print_help()
		sys.exit("Missing arguments")

	input_file = argv[0]
	if (not path.isabs(input_file)):
				path.join(root_dir, input_file)

	if (argv_len >= 2): 
		output_apk = argv[1]
		if (not path.isabs(output_apk)):
			path.join(root_dir, output_apk)

	if (argv_len >= 3): 
		plugins = argv[2].split(",")

def main(argv):
	parse_args(argv)
	
	logger.info('Input file: {0}'.format(input_file))
	logger.info('Output apk: {0}'.format(output_apk))

	obfuscation = Obfuscation(
        input_file,
        "tmp",
        output_apk,
    )

	logger.info("Decompiling APK...")

	obfuscation.decompile_apk()

	logger.info("Completed decompiling APK")

	logger.info('Obfuscating with plugins: {0} \n'.format(plugins))
	
	for plugin in plugins:
		logger.info('Starting "{0}" plugin'.format(plugin))
		module = importlib.import_module("{0}.{1}".format(plugins_module, plugin))
		module.obfuscate(obfuscation)
		
	logger.info("Compiling obsfucated APK...")
	obfuscation.compile_apk()


if __name__ == '__main__':
	main(sys.argv[1:])
