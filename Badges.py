import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog, ttk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import os
import sys


# Determine the directory of the script, considering if it's bundled or not
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    script_dir = sys._MEIPASS
else:
    # Running in a normal Python environment
    script_dir = os.path.dirname(os.path.abspath(__file__))

# Directory containing your .ttf files
font_dir = os.path.join(script_dir, 'fonts')

# Get a list of all .ttf files in the directory
font_files = [f for f in os.listdir(font_dir) if f.endswith('.ttf')]

# Register each font with pdfmetrics
for font_file in font_files:
    font_name = os.path.splitext(font_file)[0]  
    pdfmetrics.registerFont(TTFont(font_name, os.path.join(font_dir, font_file)))


# Function to create the PDF
def create_pdf(names, word_var, font, logo_path1, logo_path2, custom_word=None):
    
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    
    if not file_path:
        return

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    cell_width = width / 3
    cell_height = height / 6  

    num_names = len(names)
    max_names_per_page = 12
    num_pages = (num_names - 1) // max_names_per_page + 1 

    for page_num in range(num_pages):

        # Add the names to the cells
        for i in range(max_names_per_page):
            name_idx = page_num * max_names_per_page + i
            if name_idx < num_names:
                name = names[name_idx]
                x = (i % 3) * cell_width
                y = height - ((i // 3 % 4 + 1) * cell_height)

                # Add the logos to the top corners of the cell
                for logo_path, offset in zip([logo_path1, logo_path2], [0, cell_width - 2*cm]):  
                    if logo_path:
                        logo = Image.open(logo_path)
                        logo = logo.convert("RGBA")  
                        logo_width, logo_height = logo.size
                        aspect = logo_height / float(logo_width)
                        
                        # Adjust the size to make the logo slightly bigger
                        logo_width *= 1.5
                        logo_height *= 1.5
                        
                        logo_width = min(logo_width, 2*cm)  
                        logo_height = min(logo_height, 2*cm)  

                        # Draw the image onto the canvas
                        c.saveState()
                        c.translate(x + offset, y + cell_height - logo_height)
                        c.drawImage(logo_path, 0, 0, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
                        c.restoreState()

                # Add the name to the middle of the cell
                c.setFont(f"{font}", 20)  # Bigger, bold font
                c.drawCentredString(x + cell_width / 2, y + cell_height / 2, name)

                # Add the user-specified word to the middle-bottom of the cell
                if word_var == "Other" and custom_word:
                    c.setFont("Helvetica", 14)  # Not bold
                    c.drawCentredString(x + cell_width / 2, y + cell_height / 4, custom_word)
                else:
                    c.setFont("Helvetica", 14)  # Not bold
                    c.drawCentredString(x + cell_width / 2, y + cell_height / 4, word_var)

                # Draw a border around the cell
                c.rect(x, y, cell_width, cell_height)

        c.showPage()

    c.save()

# Create the GUI
root = tk.Tk()
root.title("Badges Generator")


style = ttk.Style()
style.theme_use('clam')

main_frame = ttk.Frame(root, padding="20")
main_frame.grid(row=0, column=0, sticky="nsew")


# Function to open the file dialog
def browse_files(entry):
    filename = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, filename)

# Function to switch between Entry and OptionMenu
def switch_word_entry(*args):
    if word_var.get() == "Other":
        word_entry.config(state="normal")
        #word_optionmenu.config(state="enabled")
    else:
        word_entry.config(state="disabled")
        #word_optionmenu.config(state="normal")


names_label = ttk.Label(main_frame, text="Enter names (separated by space):")
names_label.grid(row=0, column=0, sticky="w", pady=5)

names_entry = ttk.Entry(main_frame, width=50)
names_entry.grid(row=1, column=0, sticky="w", pady=5)

options = ["Choose", "Candidate", "Faculty", "Volunteer", "Other"]
word_label = ttk.Label(main_frame, text="Select the status:")
word_label.grid(row=2, column=0, sticky="w", pady=5)

word_var = tk.StringVar(root)
word_var.set(options[0])  
word_var.trace("w", lambda *args: switch_word_entry(word_var.get()))  

word_optionmenu = ttk.OptionMenu(main_frame, word_var, *options)
word_optionmenu.grid(row=3, column=0, sticky="w", pady=5)

word_entry = ttk.Entry(main_frame, width=20, state="disabled")
word_entry.grid(row=4, column=0, sticky="w", pady=5)

font_label = ttk.Label(main_frame, text="Select a font for the names:")
font_label.grid(row=5, column=0, sticky="w", pady=5)

available_fonts = sorted(tkFont.families())

font_var = tk.StringVar(root)
font_var.set("Helvetica")  

font_names = [os.path.splitext(os.path.basename(font_file))[0] for font_file in font_files]
font_optionmenu = ttk.OptionMenu(main_frame, font_var, *available_fonts)
font_optionmenu.grid(row=6, column=0, sticky="w", pady=5)

font_optionmenu.grid(row=6, column=0, sticky="w", pady=5)


font_preview_label = ttk.Label(main_frame, text="Font Preview")
font_preview_label.grid(row=7, column=0, sticky="w", pady=5)

def show_font_preview(*args):
    selected_font = font_var.get()
    font = tkFont.Font(family=selected_font, size=12)
    font_preview_label.config(font=font, text=f"Font preview")

font_var.trace_add("write", show_font_preview)
show_font_preview()

logo1_label = ttk.Label(main_frame, text="Select the logo on the Left:")
logo1_label.grid(row=8, column=0, sticky="w", pady=5)

logo1_entry = ttk.Entry(main_frame, width=50)
logo1_entry.grid(row=9, column=0, sticky="w", pady=5)

logo1_button = ttk.Button(main_frame, text="Browse", command=lambda: browse_files(logo1_entry))
logo1_button.grid(row=9, column=1, sticky="w", pady=5)

logo2_label = ttk.Label(main_frame, text="Select the logo on the Right:")
logo2_label.grid(row=10, column=0, sticky="w", pady=5)

logo2_entry = ttk.Entry(main_frame, width=50)
logo2_entry.grid(row=11, column=0, sticky="w", pady=5)

logo2_button = ttk.Button(main_frame, text="Browse", command=lambda: browse_files(logo2_entry))
logo2_button.grid(row=11, column=1, sticky="w", pady=5)

submit_button = ttk.Button(main_frame, text="Create Badges", command=lambda: create_pdf(names_entry.get().split(' '), word_var.get(), font_var.get(), logo1_entry.get(), logo2_entry.get(), word_entry.get() if word_var.get() == "Other" else None))
submit_button.grid(row=12, column=0, sticky="w", pady=10)


# Set styles for the main frame
style.configure("Main.TFrame", background="#F0F0F0", borderwidth=2)

for child in main_frame.winfo_children():
    child.grid_configure(padx=10)

root.mainloop()
