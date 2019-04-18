# import tkinter
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from tkinter import *

class Timer:
    def __init__(self, parent):
        self.seconds = 0
        self.label = tk.Label(parent, text="0 s", font="Arial 30", width=10)
        self.label.pack()
        self.label.after(1000, self.refresh_label)

    def refresh_label(self):
        self.seconds += 1
        self.label.configure(text="%i s" % self.seconds)
        self.label.after(1000, self.refresh_label)

class ShowNodes:
	def __init__(self, parent):
		self.parent = parent
		self.lbl1 = Label(parent, text="Node List:", fg='black', font=("Helvetica", 16, "bold"))
		self.lbl2 = Label(parent, text="Node Information:", fg='black', font=("Helvetica", 16,"bold"))
		self.lbl1.grid(row=0, column=0, sticky=W)
		self.lbl2.grid(row=0, column=1, sticky=W)


		frm = Frame(parent)
		frm.grid(row=1, column=0, sticky=N+S)
		parent.rowconfigure(1, weight=1)
		parent.columnconfigure(1, weight=1)

		self.scrollbar = Scrollbar(frm, orient="vertical")
		self.scrollbar.pack(side=RIGHT, fill=Y)

		self.listNodes = Listbox(frm, width=20, yscrollcommand=self.scrollbar.set, font=("Helvetica", 12))
		self.listNodes.pack(expand=True, fill=Y)
		
		self.scrollbar.config(command=self.listNodes.yview)


		for i in range(50):
			self.listNodes.insert(END , "Node " + str(i))

		self.listselection = Listbox(parent, height = 4, font = ("Helvetica", 12))
		self.listselection.grid(row = 1, column = 1, sticky = E+W+N)

		for i in range(4):
			self.listselection.insert(END, "X : "+ str(i))

		self.listselection.after(200, self.refresh)
    	

	def refresh(self):
		tp = self.listNodes.curselection()
		self.listselection.delete(0, END)
		self.listselection.insert(END, "Node id: " + str(tp))
		self.listselection.after(200, self.refresh)


def run():
    root = tk.Tk()
    root.geometry("400x500")
    timer = ShowNodes(root)
    root.mainloop()