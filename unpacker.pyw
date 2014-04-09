#!/usr/bin/env python
import tkinter as tk
import tkinter.filedialog
from math import ceil, log
import raf
import util

class Unpacker(tk.Frame):
	def __init__(self, master=None):
		# create a shitty GUI
		tk.Frame.__init__(self, master)
		self.grid()
		self.settingsCanvas = tk.Canvas(self)
		self.settingsCanvas.grid()
		self.lolbase = tk.Entry(self.settingsCanvas, width=80)
		self.lolbase.grid()
		self.selBaseDirButt = tk.Button(self.settingsCanvas, text='LoL Base Path', command=self.setBaseLoLPath)
		self.selBaseDirButt.grid(column=1, row=0)
		self.extractbase = tk.Entry(self.settingsCanvas, width=80)
		self.extractbase.grid(column=0, row=1)
		self.extractbaseButt = tk.Button(self.settingsCanvas, text='Extract into', command=self.setExtractBase)
		self.extractbaseButt.grid(column=1, row=1)
		self.goButton = tk.Button(self.settingsCanvas, text='Unpack', command=self.go)
		self.goButton.grid()
		self.progress = tk.Text(self, height=20, width=80)
		self.progress.grid(column=0, row=2)

	def go(self):
		basepath = self.lolbase.get() + "/RADS/projects/lol_game_client/filearchives"
		self.progmsg('Searching ' + basepath + ' for archive files...\n')
		files = util.findAllRafsIn(basepath)
		files.sort()
		self.progmsg(str(len(files)) + ' found, extracting into ' + self.extractbase.get())

		i = 1
		fmt = "[%3d%% %" + str(ceil(log(len(files))/log(10))) + "d/%d] %s"
		for f in files:
			self.progmsg(fmt % (int(100*i/len(files)), i, len(files), f))
			print(fmt % (int(100*i/len(files)), i, len(files), f))
			self.progress.update_idletasks()
			r = raf.RAF(f)
			r.extractAll(basedir=self.extractbase.get())
			i += 1
		self.progmsg('Extraction complete.')

	def progmsg(self, msg):
		self.progress.insert(tk.END, msg + "\n")

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
