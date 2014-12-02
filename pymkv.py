import subprocess
import re

class MkvTrack:
	def __init__(self):
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

	def set_id(self, id):
		self.id = id

	def set_type(self, type):
		self.type = type

	def set_name(self, name):
		self.name = name

	def set_default(self, deflt):
		self.default = deflt

	def set_language(self, lang):
		self.language = lang

	def set_codec(self, codec):
		self.codec = codec

	def __str__(self):
		spec = ''
		if self.type == 'video':
			if self.video_height != 0 or self.video_width != 0:
				spec = "%dx%d" % (self.video_width, self.video_height)
		elif self.type == 'audio':
			if self.audio_freq != 0 or self.audio_chans != 0:
				spec = "%d Hz, %d ch" % (self.audio_freq, self.audio_chans)
		return "%2d | %-9s | %-40.40s | %-20.20s | %-4.4s | %-3s | %-20.20s" % (self.id, self.type, self.name, self.codec, self.language, self.default, spec)

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

def parse_mkv_file(mkvfile):
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
				curtrack = MkvTrack()
			else:
				if curtrack is not None:
					curtrack.parse_string(s)
		if curtrack is not None:
			tracklist.append(curtrack)
	return tracklist