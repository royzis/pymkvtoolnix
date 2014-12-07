

import sys
import getopt
import os
from pymkv import MkvTrack, parse_mkv_file, compare_mkv_tracks, run_mkvpropedit

def print_tracks(tracklist):
	print MkvTrack.header()
	print MkvTrack.separator()
	for t in tracklist:
		print str(t)

def usage():
	print "TODO usage here"

def get_absolute_track(track_name, track_type, tracks):
	if track_name.startswith(':'):
		# Relative number or name
		if track_name[1:].isdigit():
			# Relative number
			track_found = 0
			for t in tracks:
				if t.get_type() == track_type:
					track_found += 1
					if track_found == int(track_name[1:]):
						return t.get_id()
			return -1
		else:
			# Track name
			for t in tracks:
				if t.get_name() == track_name[1:]:
					return t.get_id()
			return -1
	else:
		# Track number or language
		if track_name.isdigit():
			# Track number
			i = int(track_name)
			if tracks[i].get_type() == track_type:
				return tracks[i].get_id()
			else:
				return -1
		else:
			# Language
			for t in tracks:
				if t.get_type() == track_type:
					if t.get_language() == track_name:
						return t.get_id()
			return -1

def get_other_tracks(tracks, track_type, default_track):
	result = []
	for t in tracks:
		if t.get_type() == track_type and t.get_id() != default_track:
			result.append(t.get_id())
	return result



def set_new_defaults(fname, audio_track, subtitle_track, tracks):
	if subtitle_track is not None:
		tid = get_absolute_track(subtitle_track, 'subtitles', tracks)
		print "Set default subtitle track", tid, "for", fname
		run_mkvpropedit(fname, tid, get_other_tracks(tracks, 'subtitles', tid))
	if audio_track is not None:
		tid = get_absolute_track(audio_track, 'audio', tracks)
		print "Set default audio track", tid, "for", fname
		run_mkvpropedit(fname, tid, get_other_tracks(tracks, 'audio', tid))

def get_all_mkv_files(workdir):
	allfiles = [ f for f in os.listdir(workdir) if os.path.isfile(os.path.join(workdir,f)) ]
	result = []
	for f in allfiles:
		if not f.lower().endswith('.mkv'):
			continue					# We check only MKV files
		f1 = os.path.join(workdir, f)
		result.append(f1)
	return result

def main(argv):
	if len(argv) < 2:
		usage()
		sys.exit(1)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hvca:s:e:", ["help", "version", "check", "audio=", "subtitle=", "mkv-encoding="])
	except getopt.GetoptError as err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(1)
	check_consistency = False
	new_default_audio = None
	new_default_subtitle = None
	mkv_encoding = 'utf-8'
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
		elif o in ("-e", "--mkv-encoding"):
			mkv_encoding = a
		else:
			print "Bad option '%s'" % o
			exit(1)
	if len(args) == 0:
		print "No filename specified"
		exit(1)

	if check_consistency and (new_default_audio is not None or new_default_subtitle is not None):
		print "Consistency checking can't be specified with audio/subtitle defaults change"
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
		# File was specified, eiither print the tracks info or check the consitency with other files in the directory
		try:
			ref_tracks = parse_mkv_file(work_file, mkv_encoding)
		except Exception, s:
			print "MKV parsing error:", s
			raise
			exit(3)
		if check_consistency:
			allfiles = get_all_mkv_files(work_dir)
			# Checking consistency for these files"
			for f in allfiles:
				if f != work_file:				# Skip the reference file
					try:
						t = parse_mkv_file(f)
						result = compare_mkv_tracks(ref_tracks, t)
						if result != '' :
							print "*DIFFERENT", f
							print result
						else:
							print "*OK       ", f
					except Exception, s:
						print "*CANTPARSE", f
						print s
		elif new_default_subtitle is None and new_default_audio is None:
			print_tracks(ref_tracks)
		else:
			set_new_defaults(work_file, new_default_audio, new_default_subtitle, ref_tracks)
	else:
		# Working directoy specified
		allfiles = get_all_mkv_files(work_dir)
		for f in allfiles:
			try:
				tracks = parse_mkv_file(f, mkv_encoding)
			except Exception, s:
				print "MKV parsing error:", s
				exit(3)
			set_new_defaults(f, new_default_audio, new_default_subtitle, tracks)

main(sys.argv)