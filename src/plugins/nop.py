import logging
import utils
import re
from obsfucation import Obfuscation

logger = logging.getLogger(
    "{0}".format(__name__)
)

def obfuscate(obsfucation: Obfuscation):
	logging.info("Running {0} obsfucator".format(__name__))
	
	try:
		# Target to junk invoking, moving and constants.
		op_codes = utils.get_op_codes()
		pattern = re.compile(r"\s+(?P<op_code>\S+)")
		
		# Start reading of smali files
		for smali_file in obsfucation.smali_files:
			with utils.edit_file(smali_file) as (in_file, out_file):
				control = False # Prevent accidental edits
				for line in in_file:
				
					# Output the original line first
					control = True # Turn off control to write
					out_file.write(line)
					
					#Check if current starting line contains op code
					matched = pattern.match(line)
					if matched:
						# Check if the op_code matched is within targeted op codes
						op_code = matched.group("op_code")
						if op_code in op_codes:
							count = utils.get_ran_int(5,10)
							out_file.write("\tnop\n" * count)
					control = False 	# Always set control off to prevent edits
				
	except Exception as e:
		logger.error(
			'Error during execution of "{0}" obfuscator: {1}'.format(
				__name__, e
			)
		)
		raise