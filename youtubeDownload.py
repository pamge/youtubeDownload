#!/usr/local/bin/python3
import os
import re
import sys
import csv
import youtube_dl
from urllib import request
from itertools import islice
from datetime import datetime
from urllib.parse import urlencode

class Logger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		pass

YOUTUBE_HOST = 'https://www.youtube.com'

REGEX_PATTERN = '<h3 class="yt-lockup-title "><a href="\/watch\?v=([^"&]+)[^>]+>([^<]+)'

YDL_OPTS = {
	'age_limit': 87,
	'useid': True,
	'logger': Logger(),
	'format': 'bestaudio/best',
	'postprocessors': [
		{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}
	],
}

def download_song(path, song):
	try:
		# check mp3 is existed
		if os.path.isfile(path + '%d.mp3' % song['id']):
			print('[PASSED] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
			return True
		# search song in youtube
		name = song['name'].replace(' ', '+')
		artist = song['artist'].replace(' ', '+')
		youtube_search_url = YOUTUBE_HOST + '/results?' + urlencode({'search_query': '%s+%s' % (name, artist)})
		youtube_search_content = request.urlopen(youtube_search_url).read().decode('utf-8')
		match_youtube_infos = re.findall(REGEX_PATTERN, youtube_search_content)
		# download
		YDL_OPTS['outtmpl'] = str(song['id']) + '.%(ext)s'
		for match_youtube_info in match_youtube_infos[0 : 5]:
			try:
				if match_youtube_info[1].find(song['name']) == -1:
					continue
				if match_youtube_info[1].find(song['artist']) == -1:
					continue
				with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
					ydl.download([YOUTUBE_HOST + '/watch?v=%s' % match_youtube_info[0]])
					print('[DOWNLOADED] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
					return True
			except KeyboardInterrupt:
				if os.path.isfile(path + '%d.mp3' % song['id']):
					os.remove(path + '%d.mp3' % song['id'])
				exit(0)
			except:
				print('[UNKNOWN FAILED IN FOR] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
				print('%s %s' % (sys.exc_info()[0], sys.exc_info()[1]))
				pass
		print('[UNKNOWN FAILED] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
		return False
	except KeyboardInterrupt:
		if os.path.isfile(path + '%d.mp3' % song['id']):
			os.remove(path + '%d.mp3' % song['id'])
		exit(0)
	except SystemExit:
		exit(0)
	except:
		print('[UNKNOWN FAILED] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
		print('%s %s' % (sys.exc_info()[0], sys.exc_info()[1]))
	return False

def read_songs_from_csv(path):
	try:
		with open(path, errors = 'ignore') as f:
			songs = []
			for song in csv.reader(islice(f, 1, None)):
				songs.append({
					'id': int(song[0]),
					'name': song[1],
					'artist': song[2]
				})

			return songs
	except:
		print('%s %s' % (sys.exc_info()[0], sys.exc_info()[1]))
	exit(-1)

def main():
	# parse parameter
	if len(sys.argv) < 2:
		print('Usage: %s Collection_Canonicals.csv [download path]' % sys.argv[0])
		exit(-1)
	path = ''
	if len(sys.argv) == 3:
		path = sys.argv[2]
		if path[-1] != '/' and path[-1] != '\\':
			print('download path should be %s/ or %s\\' % (path, path))
			exit(-1)
	# download song
	for song in read_songs_from_csv(sys.argv[1]):
		if download_song(path, song) == False:
			with open('error_log.txt', 'a') as f:
				f.write('[%s] ' % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
				f.write('id = %d, name = %s, artist = %s\n' % (song['id'], song['name'], song['artist']))

if __name__ == '__main__':
	main()
