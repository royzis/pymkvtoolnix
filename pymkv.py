import subprocess
import re

class MkvTrack:
	def __init__(self, str_encode='utf-8'):
		self.type = ''
		self.name = ''
		self.id = 0
		self.language = ''
		self.codec = ''
		self.default = ''
		# Spec data for a video track
		self.video_width = 0
		self.video_height = 0
		# Spec data for an audio track
		self.audio_freq = 0
		self.audio_chans = 0
		self.str_encode = str_encode
		self.compare_result = ''

	def get_id(self):
		return self.id

	def set_id(self, id):
		self.id = id

	def set_type(self, type):
		self.type = type

	def get_type(self):
		return self.type

	def set_name(self, name):
		self.name = name

	def get_name(self):
		return self.name

	def set_default(self, deflt):
		self.default = deflt

	def set_language(self, lang):
		self.language = lang

	def get_language(self):
		return self.language

	def set_codec(self, codec):
		self.codec = codec

	def get_compare_result(self):
		return self.compare_result

	def __str__(self):
		spec = ''
		if self.type == 'video':
			if self.video_height != 0 or self.video_width != 0:
				spec = u"%dx%d" % (self.video_width, self.video_height)
		elif self.type == 'audio':
			if self.audio_freq != 0 or self.audio_chans != 0:
				spec = u"%d Hz, %d ch" % (self.audio_freq, self.audio_chans)
		# Convert string to unicode to manage correct string format widths
		utype = self.type.decode(self.str_encode, 'replace')
		uname = self.name.decode(self.str_encode, 'replace')
		ucodec = self.codec.decode(self.str_encode, 'replace')
		ulang = self.language.decode(self.str_encode, 'replace')
		udefault = self.default.decode(self.str_encode, 'replace')
		s = u"%2d | %-9s | %-40.40s | %-20.20s | %-4.4s | %-3s | %-20.20s" % (self.id, utype, uname, ucodec, ulang, udefault, spec)
		# Convert the formatted string back
		return s.encode(self.str_encode, 'replace')

	@staticmethod
	def header():
		return "%2s | %-9s | %-40s | %-20s | %-4s | %3s | %-20.20s" % ('id', 'Type', 'Name', 'Codec', 'Lang', 'Dft', 'Spec')

	@staticmethod
	def separator():
		return (2+9+40+20+4+3+20+(6*3))*'-'

	def parse_string(self, s):
		o = re.search('track ID for mkvmerge \& mkvextract: (\d+)', s)
		if o is not None:
			self.set_id(int(o.group(1)))
		else:
			o = re.search('Track type: (\S+)', s)
			if o is not None:
				self.set_type(o.group(1))
			else:
				o = re.search('Default flag: (\d)', s)
				if o is not None:
					self.set_default(o.group(1))
				else:
					o = re.search('Name: (.+)', s)
					if o is not None:
						self.set_name(o.group(1))
					else:
						o = re.search('Language: (\S+)',s)
						if o is not None:
							self.set_language(o.group(1))
						else:
							o = re.search('Codec ID: (.+)',s)
							if o is not None:
								self.set_codec(o.group(1))
							else:
								if self.type == 'video':
									o = re.search('Pixel width: (\d+)', s)
									if o is not None:
										self.video_width = int(o.group(1))
									else:
										o = re.search('Pixel height: (\d+)', s)
										if o is not None:
											self.video_height = int(o.group(1))
								elif self.type == 'audio':
									o = re.search('Sampling frequency: (\d+)', s)
									if o is not None:
										self.audio_freq = int(o.group(1))
									else:
										o = re.search('Channels: (\d+)', s)
										if o is not None:
											self.audio_chans = int(o.group(1))

	def __eq__(self, other):
		""" Compare two tracks information. Returns True if tracks are equal, False otherwise. Then compare_result
		property contains what field was different """
		self.compare_result = 'id'
		if self.id != other.id:
			return False
		self.compare_result = 'type'
		if self.type != other.type:
			return False
		self.compare_result = 'default'
		if self.default != other.default:
			return False
		self.compare_result = 'language'
		if self.language != other.language:
			return False
		self.compare_result = 'codec'
		if self.codec != other.codec:
			return False
		self.compare_result = ''	
		return True



def run_mkvinfo(mkvfile):
	try:
		r = subprocess.check_output(['mkvinfo', mkvfile])
	except OSError:
		l = ["Cant execute mkvinfo. Is it even installed?"]		# Return error as a list with 1 element similar to mkvinfo error
	except subprocess.CalledProcessError:						# Didn't see that yet, mkvinfo always returns 0
		l = ["Unsuccessful mkvinfo exit code. Check the syntax"]		
	else:
		l = r.splitlines()
	return l

def run_mkvpropedit(mkvfile, default_track, non_default_tracks):
	cmd = ['mkvpropedit', mkvfile, '--edit', 'track', str(default_track), '--set', 'flag-default=1']
	for t in non_default_tracks:
		cmd+=['--edit', 'track', str(t), '--set', 'flag-default=0']
	print "Executing", cmd
	#res = subprocess.call(cmd)

def parse_mkv_file(mkvfile, mkv_encoding='utf-8'):
	l = run_mkvinfo(mkvfile)
	if len(l) < 3:
		raise Exception, l[0]
	else:
		curtrack = None
		tracklist = []
		for s in l:
			if re.search('\\+ A track', s) != None:
				if curtrack is not None:
					tracklist.append(curtrack)
				curtrack = MkvTrack(mkv_encoding)
			else:
				if curtrack is not None:
					curtrack.parse_string(s)
		if curtrack is not None:
			tracklist.append(curtrack)
	return tracklist

def compare_mkv_tracks(tracks1, tracks2):
	""" Compares list of tracks tracks1 with list of tracks tracks2. Returns an empty string if the tracks are equal or a string
	explaining the different otherwise """
	if len(tracks1) != len(tracks2):
		return "Not same number of tracks"
	ltracks2 = tracks2	# Local copy of tracks 2 since we'll pop the elements from there
	tlen = len(tracks2)
	for t1 in tracks1:
		t2 = None
		for i in range(tlen):
			if t1.get_id() == ltracks2[i].get_id():
				t2 = ltracks2.pop(i)
				break
		if t2 is None:		# Same Id not found
			return "Track " + str(t1.get_id()) + " not found"
		if not t1 == t2:
			return "Different " + t1.get_compare_result() + " in track " + str(t1.get_id())
	if len(ltracks2) != 0:
		# We should never get here: tracks2 had more tracks than already checked. This is impossible as far as we
		# compared the lengthes already
		return "Still have uncompared tracks"
	return ''