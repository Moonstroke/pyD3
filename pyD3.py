#!/usr/bin/python3
# -*- coding: utf-8 -*-

from csv import excel
import os

def wadj(string, length, padchar):
	if len(string) > length:
		r = string[:length]
	else:
		r = string.ljust(length, padchar)
	return r

class TagError(KeyError):
	'''Exception raised when no valid tag is found.'''

class Track:
	'''This class is a structure for sound tracks.
It is linked to one file on the disk.
It supports: opening, reading and writing.'''
	
	try:
		genres = excel(open('genres.csv', 'rt').read(), skipinitialspace=True)
	except FileNotFoundError:
		genres = []
	
	def read(self):
		file = open(self.path, 'rb')
		file.seek(-128, 2) #set stream to index end - 128
		if file.read(3) != 'TAG': raise TagError('Invalid file')
		hasTAG = True
		self.tags['title'] = file.read(30)
		self.tags['artist'] = file.read(30)
		self.tags['album'] = file.read(30)
		self.tags['year'] = file.read(4)
		comment = file.read(30)
		num = ord(comment[-1])
		if ord(comment[-2]) == 0 and num != 0: # last digit is track number if penultimate is ASCII null
			self.tags['comment'] = comment[:-2]
			self.tags['tnum'] = num
		else:
			self.tags['comment'] = comment
			self.tags['tnum'] = 0
		
		try:
			genreindex = ord(file.read())
			self.tags['genre'] = self.genres[genreindex]
		except TypeError:
			print('zut')
		except IndexError:
			self.genre = ''
	
	def write(self):
		file = open(self.path, 'r+b')
		try:
			file.seek(-128 * self.hasTAG, 2) # flow to -128 if TAG has been found sooner, else to the end of file
		except AttributeError:
			print('`Track.read` must be called before `Track.write`!!')
		
		file.write(wadj(self.tags['title'], 30, '\0'))
		file.write(wadj(self.tags['artist'], 30, '\0'))
		file.write(wadj(self.tags['album'], 30, '\0'))
		file.write(wadj(self.tags['year'], 4, '\0'))
		if self.tags['tnum']:
			file.write(wadj(self.tags['comment'], 28, '\0') + '\0')
			file.write(self.tags['tnum'])
		else:
			file.write(wadj(self.tags['comment'], 30, '\0'))
		try:
			genreindex = genres.index(self.tags['genre'])
		except ValueError:
			genreindex = 255
		file.write(genreindex)
		
	
	def delete(self, tag='all'):
		if tag == 'all':
			for t in self.tags:
				self.delete(t)
		else:
			try:
				self.tags[tag] = ''
			except KeyError:
				raise TagError
		
	
	def __init__(self, path):
		self.path = path
		self.tags = {}
		self.read()
	
	def __repr__(self):
		r = '@' + self.path + ' : '
		if self.tags['artist']: r += self.tags['artist'] + ' - '
		if self.tags['title']:  r+= self.title + ' : '
		r += self.tags['album']
		if self.tags['tnum']:   r += '[' + self.tags['tnum'] + ']'
		if self.tags['year']:   r += ', ' + str(self.tags['year']) + ''
		if self.tags['genre']:  r += ', (' + self.tags['genre'] + ')'
		if self.tags['comment']: r += ', "' + self.tags['comment'] + '"'
		return r
	
	def __str__(self):
		return '''{0}

TITLE:   {title}
ARTIST:  {artist}
ALBUM:   {album}
YEAR:    {year}
GENRE:   {genre}
NUMBER:  {tnum}
COMMENT: {comment}
'''.format(self.path, **self.tags)
	
