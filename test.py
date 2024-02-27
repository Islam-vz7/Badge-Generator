import tkinter as tk
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
    font_name = os.path.splitext(font_file)[0]  # Remove the .ttf extension
    pdfmetrics.registerFont(TTFont(font_name, os.path.join(font_dir, font_file)))


# Function to create the PDF
def create_pdf(names, word_var, font, logo_path1, logo_path2, custom_word=None):
    # Ask the user to choose the file path and name for saving the PDF
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    
    if not file_path:
        return

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    cell_width = width / 3
    cell_height = height / 6  # Smaller, rectangular cells

    num_names = len(names)
    max_names_per_page = 12
    num_pages = (num_names - 1) // max_names_per_page + 1 # Calculate number of pages needed

    for page_num in range(num_pages):

        # Add the names to the cells
        for i in range(max_names_per_page):
            name_idx = page_num * max_names_per_page + i
            if name_idx < num_names:
                name = names[name_idx]
                x = (i % 3) * cell_width
                y = height - ((i // 3 % 4 + 1) * cell_height)

                # Add the logos to the top corners of the cell
                for logo_path, offset in zip([logo_path1, logo_path2], [0, cell_width - 2*cm]):  # Different logos
                    if logo_path:
                        logo = Image.open(logo_path)
                        logo = logo.convert("RGBA")  # Ensure RGBA mode for transparency
                        logo_width, logo_height = logo.size
                        aspect = logo_height / float(logo_width)
                        
                        # Adjust the size to make the logo slightly bigger
                        logo_width *= 1.5
                        logo_height *= 1.5
                        
                        logo_width = min(logo_width, 2*cm)  # Limit the maximum width
                        logo_height = min(logo_height, 2*cm)  # Limit the maximum height

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

# Function to open the file dialog
def browse_files(entry):
    filename = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, filename)

# Function to switch between Entry and OptionMenu
def switch_word_entry(value):
    if value == "Other":
        word_entry.config(state="normal")
        word_optionmenu.config(state="enabled")
    else:
        word_entry.config(state="disabled")
        word_optionmenu.config(state="normal")

# Create the GUI
root = tk.Tk()
root.title("Badges Generator")

# Set the theme to 'clam'
style = ttk.Style()
style.theme_use('clam')

main_frame = ttk.Frame(root, padding="20")
main_frame.grid(row=0, column=0, sticky="nsew")

names_label = ttk.Label(main_frame, text="Enter names (separated by space):")
names_label.grid(row=0, column=0, sticky="w", pady=5)

names_entry = ttk.Entry(main_frame, width=50)
names_entry.grid(row=1, column=0, sticky="w", pady=5)

options = ["Candidate", "Faculty", "Volunteer"]
word_label = ttk.Label(main_frame, text="Select the status:")
word_label.grid(row=2, column=0, sticky="w", pady=5)

word_var = tk.StringVar(root)
word_var.set(options[0])  # default value
word_var.trace("w", lambda *args: switch_word_entry(word_var.get()))  # call switch_word_entry when the variable changes

word_optionmenu = ttk.OptionMenu(main_frame, word_var, *options, "Other")
word_optionmenu.grid(row=3, column=0, sticky="w", pady=5)

word_entry = ttk.Entry(main_frame, width=20, state="disabled")
word_entry.grid(row=4, column=0, sticky="w", pady=5)

font_label = ttk.Label(main_frame, text="Select a font for the names:")
font_label.grid(row=5, column=0, sticky="w", pady=5)

font_var = tk.StringVar(root)
font_var.set("Helvetica")  # default value

font_names = [os.path.splitext(os.path.basename(font_file))[0] for font_file in font_files]
font_optionmenu = ttk.OptionMenu(main_frame, font_var, *font_names)
font_optionmenu.grid(row=6, column=0, sticky="w", pady=5)

logo1_label = ttk.Label(main_frame, text="Select the logo on the Left:")
logo1_label.grid(row=7, column=0, sticky="w", pady=5)

logo1_entry = ttk.Entry(main_frame, width=50)
logo1_entry.grid(row=8, column=0, sticky="w", pady=5)

logo1_button = ttk.Button(main_frame, text="Browse", command=lambda: browse_files(logo1_entry))
logo1_button.grid(row=8, column=1, sticky="w", pady=5)

logo2_label = ttk.Label(main_frame, text="Select the logo on the Right:")
logo2_label.grid(row=9, column=0, sticky="w", pady=5)

logo2_entry = ttk.Entry(main_frame, width=50)
logo2_entry.grid(row=10, column=0, sticky="w", pady=5)

logo2_button = ttk.Button(main_frame, text="Browse", command=lambda: browse_files(logo2_entry))
logo2_button.grid(row=10, column=1, sticky="w", pady=5)

submit_button = ttk.Button(main_frame, text="Create Badges", command=lambda: create_pdf(names_entry.get().split(' '), word_var.get(), font_var.get(), logo1_entry.get(), logo2_entry.get(), word_entry.get() if word_var.get() == "Other" else None))
submit_button.grid(row=11, column=0, sticky="w", pady=10)


# Set styles for the main frame
style.configure("Main.TFrame", background="#F0F0F0", borderwidth=2)

for child in main_frame.winfo_children():
    child.grid_configure(padx=10)

root.mainloop()
