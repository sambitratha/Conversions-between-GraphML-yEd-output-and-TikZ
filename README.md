# Conversions-between-GraphML-yEd-output-and-TikZ

## How to run
   - **In order to run this software, some dependencies have to be installed first.**
	 - **Tkinter**
	   -This is used for GUI purposes. It can be installed by typing ` pip install tkinter`
	 - **Lark**
	   -This library is used for generating a parse tree from a given grammar. It can be installed by typing `pip install lark`
	 - **Xml**
	   -This library is used to generate the final graphml output

   - **After installing the dependencies, clone or download the git repository in a folder and change the go to the downloaded folder in commandline.
   - From commandline, type ` python GUI.py`
   - This will run the GUI file, where user can select a tikz code in latex and save it as a graphml output.

## Functionalities covered
   - [x] ` \node` instruction
   - [x] ` \draw` instruction
   - [x] ` \foreach \x/\y in {..}` 
   - [x] drawing polar coordinates
   - [x] drawing edges without declaring nodes
   - [ ] handling math characters 
   - [ ] handling `every node ./style` for a given codeblock


