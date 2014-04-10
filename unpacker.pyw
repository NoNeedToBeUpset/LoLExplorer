#!/usr/bin/env python
import os
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from math import ceil, log
import raf
import util

# moar TODO: make GUI more responsive within files (as opposed to between, now)
# best approach is probably threads, but since I'm lazy that can wait

class Unpacker(tk.Frame):
	def __init__(self, master=None):
		# create a shitty, ugly GUI
		tk.Frame.__init__(self, master)
		self.grid()
		self.settingsCanvas = tk.Canvas(self)
		self.settingsCanvas.grid()
		self.lolbase = tk.Entry(self.settingsCanvas, width=80)
		for guess in util.loldirguesses:
			if os.path.exists(guess):
				self.lolbase.insert(0, guess)
				break
		self.lolbase.grid()
		self.selBaseDirButt = tk.Button(self.settingsCanvas, text='LoL Base Path', command=self.setBaseLoLPath)
		self.selBaseDirButt.grid(column=1, row=0)
		self.extractbase = tk.Entry(self.settingsCanvas, width=80)
		self.extractbase.grid(column=0, row=1)
		self.extractbaseButt = tk.Button(self.settingsCanvas, text='Extract into', command=self.setExtractBase)
		self.extractbaseButt.grid(column=1, row=1)
		self.goButton = tk.Button(self.settingsCanvas, text='Unpack', command=self.startjob)
		self.goButton.grid()
		self.progCanv = tk.Canvas(self)
		self.progCanv.grid()
		self.progress = tk.Text(self.progCanv, height=20, width=80)
		self.progress.pack(side="left")
		self.progScroll = tk.Scrollbar(self.progCanv)
		self.progScroll.pack(side="right", fill="y", expand=True)
		self.progress['yscrollcommand'] = self.progScroll.set

		# this is where information about an ongoing job is stored
		self.job = {
			'active': False,
			'curfile': 0,
			'nfiles': 0,
			'files': [],
			'basepath': '',
			'extractpath': '',
			'format': ''}

	# startjob - initialize self.job and start processing it
	def startjob(self):
		# first off, you are NOT allowed to start two jobs at once, disable goButton
		self.goButton['state'] = tk.DISABLED

		# store paths
		self.job['basepath'] = self.lolbase.get() + "/RADS/projects/lol_game_client/filearchives"
		self.job['extractpath'] = self.extractbase.get()

		# find all .raf-files in basepath
		self.progmsg('Searching ' + self.job['basepath'] + ' for archive files...')
		self.progress.update_idletasks()
		self.job['files'] = util.findAllRafsIn(self.job['basepath'])
		self.job['files'].reverse()

		# save the last info and set job to active
		# futureproofing: make self.job an array (queue)?
		self.job['curfile'] = 1
		self.job['nfiles'] = len(self.job['files'])

		# example format output is [ 83%  80/127] path/to/current/file.raf
		# args are		      ^    ^   ^  ^
		self.job['format'] = "[%3d%% %" + str(ceil(log(self.job['nfiles'])/log(10))) + "d/%d] %s"
		self.job['active'] = True

		# schedule this job to start .5 seconds from now (arbitrary timeout pulled out of an ass)
		self.after(500, self.stepjob)

	# proceed with the next step of the job
	def stepjob(self):
		file = ''
		try:
			file = self.job['files'].pop()
		except IndexError:
			self.progmsg('Extraction complete.')
			tkinter.messagebox.showinfo(title='Extraction complete', message='All files have been extracted into ' + self.job['extractpath'])
			self.goButton['state'] = tk.NORMAL
			self.job['active'] = False
			return

		ftmp = file.split('/filearchives')[1]
		self.progmsg(self.job['format'] % (int(100*self.job['curfile']/self.job['nfiles']), self.job['curfile'], self.job['nfiles'], ftmp))
		r = raf.RAF(file)
		r.extractAll(basedir=self.job['extractpath'])	
		self.job['curfile'] += 1
		# based on nothing, .15 sec timeout is awesome between files
		self.after(150, self.stepjob)

	# prints a message to progresswindow
	def progmsg(self, msg, scrollDown=True):
		self.progress.insert(tk.END, msg + "\n")
		if scrollDown:
			self.progress.see(tk.END)

	def setBaseLoLPath(self):
		self.lolbase.delete(0, tk.END)
		ret = tkinter.filedialog.askdirectory()
		self.lolbase.insert(0, ret)

	def setExtractBase(self):
		self.extractbase.delete(0, tk.END)
		ret = tkinter.filedialog.askdirectory()
		self.extractbase.insert(0, ret)

def main():
	root = tk.Tk()
	up = Unpacker(root)
	up.master.title('RAF Unpacker')
	up.mainloop()

if __name__ == '__main__':
	main()
