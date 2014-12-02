

import sys
from pymkv import MkvTrack, parse_mkv_file

def print_tracks(tracklist):
	print MkvTrack.header()
	print MkvTrack.separator()
	for t in tracklist:
		print t

try:
	t = parse_mkv_file(sys.argv[1])
	print_tracks(t)
except Exception, s:
	print "ERROR:", s
	raise
