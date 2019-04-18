import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkFont
import random
from tp import *

############# global variables ################
WINDOWWIDTH = 	600
WINDOWHEIGHT =	400


def show_graph_properties():
	pass

def list_all_nodes():
	run()
	pass


def list_all_edges():
	pass

def show_demo():
	pass

def instructions():
	pass

def MainWindow():
	global input_file_location, font, output_file_location, alert_message
	WINDOWWIDTH = 	600
	WINDOWHEIGHT =	400
	

	app = tk.Tk()
	
	font = tkFont.Font(family = 'Helvetica', size = 15)
	input_file_location = StringVar()
	output_file_location = StringVar()
	alert_message = StringVar()
	alert_message.set("")
	app.geometry(str(WINDOWWIDTH + 100) + "x" + str(WINDOWHEIGHT))

	menu = Menu(app)
	app.config(menu=menu)

	add_menu_more(menu)
	add_menu_help(menu)

	add_buttons(app)

	app.mainloop()


def add_menu_more(menu):
	More = Menu(menu)
	More.add_command(label="Show Graph Properties", command=show_graph_properties, font = font)
	More.add_command(label="List All Nodes", command=list_all_nodes, font = font)
	More.add_command(label="List All Edges", command=list_all_edges, font = font)
	menu.add_cascade(label="More", menu= More, font = font)

def add_menu_help(menu):
	Help = Menu(menu)
	Help.add_command(label="Instructions", command=instructions, font = font)
	Help.add_command(label="Show Demo", command=show_demo, font = font)
	menu.add_cascade(label="Help", menu= Help, font = font)


def add_buttons(app):
	global alert_box

	select_inputfile_button = Button(app, text = "Select File", command = select_input_file, font = font)
	select_inputfile_button.place(x = WINDOWWIDTH/4, y = WINDOWHEIGHT/3)

	inputfile_entry = Entry(app, textvariable = input_file_location, font = font)
	inputfile_entry.config(width = 25)
	inputfile_entry.place(x = WINDOWWIDTH/2, y = WINDOWHEIGHT/3)
	
	select_outputfile_button = Button(app, text = "Save File", command = save_output_file, font = font)
	select_outputfile_button.place(x = WINDOWWIDTH/4, y = WINDOWHEIGHT/2)

	outputfile_entry = Entry(app, textvariable = output_file_location, font = font)
	outputfile_entry.config(width = 25)
	outputfile_entry.place(x = WINDOWWIDTH/2, y = WINDOWHEIGHT/2)

	convert_button = Button(app, text = "Convert!", command = convert, font = font, activebackground = "green", fg = "white", bg = "black")
	convert_button.place(x = WINDOWWIDTH/2, y = 3 * WINDOWHEIGHT/4)

	alert_box = Label(app, textvariable = alert_message, font = font)
	alert_box.place(x = WINDOWWIDTH/2, y = 5 * WINDOWHEIGHT/ 8)


def select_input_file():
	filename = askopenfilename()
	input_file_location.set(filename)
	print filename

def save_output_file():
	filename = asksaveasfilename()
	output_file_location.set(filename)

def convert():
	global alert_message, alert_box
	successful = random.randint(0, 1)
	if successful:
		alert_message.set("Succefully Converted!!")
		alert_box.config(fg = "green")
	else:
		alert_message.set("Errors Occurred!!")
		alert_box.config(fg = "red")
	pass

font = None
input_file_location = None
output_file_location = None
alert_message = None
alert_box = None
MainWindow()