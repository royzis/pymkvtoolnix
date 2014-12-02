

import sys
import getopt
import os
from pymkv import MkvTrack, parse_mkv_file

def print_tracks(tracklist):
	print MkvTrack.header()
	print MkvTrack.separator()
	for t in tracklist:
		print t

def usage():
	print "TODO usage here"

def main(argv):
	if len(argv) < 2:
		usage()
		sys.exit(1)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hvca:s:", ["help", "version", "check", "audio:", "subtitle:"])
	except getopt.GetoptError as err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(1)
	check_consistency = False
	new_default_audio = None
	new_default_subtitle = None
	for o, a in opts:
		if o in ("-v", "--version"):
			print "TODO Version 0.0"
			sys.exit(0)
		elif o in ("-h", "--help"):
			usage()
			sys.exit(0)
		elif o in ("-c", "--check"):
			check_consistency = True
		elif o in ("-a", "--audio"):
			new_default_audio = a
		elif o in ("-s", "--subtitle"):
			new_default_subtitle = a
		else:
			print "Bad option '%s'" % o
			exit(1)
	if len(args) == 0:
		print "No filename specified"
		exit(1)

	if check_consistency and (new_default_audio is not None or new_default_subtitle is not None):
		print "Consistency checking cant be specified with audio/subtitle defaults change"
		exit(2)

	if os.path.isdir(args[0]):
		if check_consistency:
			print "Directory provided. Specify a MKV file for consistency checking"
			exit(2)
		elif new_default_subtitle is None and new_default_audio is None:
			print "Directory provided. Specify a MKV file to get info"
			exit(2)
		work_dir = args[0]
		work_file = ''
	elif os.path.isfile(args[0]):
		work_file = os.path.realpath(args[0])
		work_dir = os.path.dirname(work_file)
	else:
		print "File/directory doesn't exist. Specify existing MKV file or a directory with MKV files"
		exit(2)


	if work_file != '':
		try:
			ref_tracks = parse_mkv_file(work_file)
		except Exception, s:
			print "MKV parsing error:", s
			raise
		if not check_consistency:
			print_tracks(ref_tracks)
		else:
			allfiles = [ f for f in os.listdir(work_dir) if os.path.isfile(os.path.join(work_dir,f)) ]
			print "Checking consistency for these files"
			for f in allfiles:
				f1 = os.path.join(work_dir, f)
				if f1 != work_file:
					print f

main(sys.argv)