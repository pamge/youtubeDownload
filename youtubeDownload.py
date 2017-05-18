#!/usr/local/bin/python3
import os
import re
import sys
import csv
import youtube_dl
from urllib import request
from itertools import islice

YOUTUBE_HOST = 'https://www.youtube.com'

class Logger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		print(msg)

YDL_OPTS = {
	'age_limit': 87,
	'useid': True,
	'logger': Logger(),
	'format': 'bestaudio/best',
	'outtmpl': '%(id)s.%(ext)s',
	'postprocessors': [
		{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}
	],
}

def download_song(song):
	try:
		# check mp3 is existed
		if os.path.isfile('%d.mp3' % song['id']):
			print('[PASSED] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
			return True
		# search song in youtube
		name = song['name'].replace(' ', '+')
		artist = song['artist'].replace(' ', '+')
		youtube_search_url = YOUTUBE_HOST + '/results?search_query=%s+%s' % (name, artist)
		youtube_search_content = request.urlopen(youtube_search_url).read().decode('utf-8')
		match_youtube_ids = re.findall('watch\?v=([^"]+)', youtube_search_content)
		if len(match_youtube_ids) <= 0:
			print('[SEAECH FAILED] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
			return False
		# download 
		YDL_OPTS['outtmpl'] = str(song['id']) + '.%(ext)s'
		with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
			ydl.download([YOUTUBE_HOST + '/watch?v=%s' % match_youtube_ids[0]])
			print('[DOWNLOADED] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
			return True
		print('[UNKNOWN FAILED] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
		return False
	except:
		print('[UNKNOWN FAILED] id: %d, name: %s, artist: %s' % (song['id'], song['name'], song['artist']))
		print('%s %s' % (sys.exc_info()[0], sys.exc_info()[1]))
	exit(-1)

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
	if len(sys.argv) != 2:
		print('Usage: %s Collection_Canonicals.csv' % sys.argv[0])
		exit(-1)
	for song in read_songs_from_csv(sys.argv[1]):
		download_song(song)

if __name__ == '__main__':
	main()
