import tkinter as tk
import tkinter.font as tkfont
import re
import json
import os

class SmartChatWidget(tk.Text):

    def __init__(self, *args, headings_theme=None, listbox_bg=None, listbox_fg=None, console_bg=None, button_bg=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.markdown_enabled = True
        self.raw_text = ""
        # Determine code background: use listbox_bg,
        # but if it matches console_bg (no contrast), use button_bg so not same color
        if listbox_bg and console_bg and listbox_bg == console_bg:
            self.listbox_bg = button_bg if button_bg else "#333333"
        else:
            self.listbox_bg = listbox_bg if listbox_bg else "#333333"
        self.listbox_fg = listbox_fg if listbox_fg else "white"  # Default to white if not provided

        #Hardcoded fallback headings if theme doesnt load
        glm = [ "#9DD9D2",  "#9DD9D2",  "#9DD9D2", "#F0F2F5", "#F0F2F5"] # Primary Action/Accent, Success/Highlight, Text, Background
        pastels= ["#FF69B4", "#77DD77", "#4A90E2", "#FFEE8C", "#CCCCCC"] # pink, pastel green, light blue, light yellow
        matrix = [ "#00FF00", "#00FF00", "#00FF00", "#00FF00", "#00FF00"] # all green for that classic matrix vibe
        aquatic = ["#7FDBFF", "#39CCCC", "#3D9970", "#2ECC40", "#01FF70"] #['#7FDBFF', '#39CCCC', '#3D9970', '#2ECC40', '#01FF70']

        ### New load from zait rather than JSON prevents race ##
         # Use passed headings_theme or hardcoded array as fallback
        if headings_theme is not None:
            header_theme = headings_theme
        else:
            # Fallback: load default theme (remove lines 32-49 duplicate loading)
            header_theme = glm
        # Get the actual font configuration to ensure consistent sizing
        default_font = tkfont.Font(font=self.cget("font"))
        font_family = default_font.actual()["family"]
        font_size = default_font.actual()["size"]
        #background and regular text color are inherited from the default Text widget settings, so we don't need to set those explicitly here, but we can easily add custom colors for headers and other elements to make it look nicer
        #header_theme = None
        arrayOfHeaderThemes = [glm, pastels, matrix, aquatic]
        #header_theme = arrayOfHeaderThemes[2] # For now, we just use the pastel theme for all headers, but we could easily expand this to have different themes or allow user customization in the future.
        self.header_theme = header_theme #new line
        #header_theme = t['headings']
        # Setup tags - bold and a simple color for headers
        # Use the same font family and size as the default, but with bold weight
        self.tag_configure("BOLD", font=(font_family, int(font_size * 1.1), "bold"))
        self.tag_configure("ITALIC", font=(font_family, font_size, "italic"))
        # Tag for bold text within bullet points - includes both bold weight and bullet margins
        self.tag_configure("BULLET_BOLD", font=(font_family, int(font_size * 1.1), "bold"), lmargin1=6, lmargin2=38)
        # Tag for bold text within indented bullet points
        self.tag_configure("BULLET_MORE_BOLD", font=(font_family, int(font_size * 1.1), "bold"), lmargin1=40, lmargin2=88)
        # Tag for italic text within bullet points - includes both italic style and bullet margins
        self.tag_configure("BULLET_ITALIC", font=(font_family, font_size, "italic"), lmargin1=6, lmargin2=38)
        # Tag for italic text within indented bullet points
        self.tag_configure("BULLET_MORE_ITALIC", font=(font_family, font_size, "italic"), lmargin1=40, lmargin2=88)
        # Tags for headings within bullet points - combine heading styling with bullet margins
        self.tag_configure("BULLET_H1", font=(font_family, font_size + 14), foreground=header_theme[0], lmargin1=6, lmargin2=38)
        self.tag_configure("BULLET_H2", font=(font_family, font_size + 6, "bold"), foreground=header_theme[1], lmargin1=6, lmargin2=38)
        self.tag_configure("BULLET_H3", font=(font_family, font_size + 2, "bold"), foreground=header_theme[2], lmargin1=6, lmargin2=38)
        self.tag_configure("BULLET_H4", font=(font_family, font_size, "bold"), foreground=header_theme[3], lmargin1=6, lmargin2=38)
        # Tags for headings within indented bullet points
        self.tag_configure("BULLET_MORE_H1", font=(font_family, font_size + 14), foreground=header_theme[0], lmargin1=40, lmargin2=88)
        self.tag_configure("BULLET_MORE_H2", font=(font_family, font_size + 6, "bold"), foreground=header_theme[1], lmargin1=40, lmargin2=88)
        self.tag_configure("BULLET_MORE_H3", font=(font_family, font_size + 2, "bold"), foreground=header_theme[2], lmargin1=40, lmargin2=88)
        self.tag_configure("BULLET_MORE_H4", font=(font_family, font_size, "bold"), foreground=header_theme[3], lmargin1=40, lmargin2=88)
        self.tag_configure(
            "CODE",
            font=("Consolas", font_size),
            background=self.listbox_bg,
            foreground=self.listbox_fg,
            lmargin1=0,    # No margin for first line (critical for ASCII art alignment)
            lmargin2=0,    # No margin for wrapped lines (critical for ASCII art alignment)
            rmargin=10,     # Stop the background 40px before the right edge
            spacing1=0,     # No extra spacing at top for proper ASCII art alignment
            spacing3=0      # No extra spacing at bottom for proper ASCII art alignment
            #selectbackground="#555555" # Prevents highlight from looking weird
            )
        self.tag_configure("H1", font=(font_family, font_size + 14), foreground=header_theme[0]) # pink
        self.tag_configure("H2", font=(font_family, font_size + 6, "bold"), foreground=header_theme[1]) # Pastel Green
        self.tag_configure("H3", font=(font_family, font_size + 2, "bold"), foreground=header_theme[2]) # Light Blue
        self.tag_configure("H4", font=(font_family, font_size, "bold"), foreground=header_theme[3]) # A nice light yellow
        #10pt fot pixell about 6px wide so +6 spaces is about 36px, which should be enough to clear the bullet character and some padding
        # use  int(font_size *0.9) of whatever instead of font_size if you want bullets smaller 
        self.tag_configure("BULLET", font=(font_family, font_size), lmargin1=6, lmargin2=38) # Wrapped line starts under first word (after bullet)
        self.tag_configure("BULLET_MORE", font=(font_family, font_size), lmargin1=40, lmargin2=88) # Wrapped line starts with +6 spaces (36px)
        self.tag_configure("HorizontalRule", foreground=header_theme[4]) # Light grey for horizontal rules

    def update_headings_theme(self, new_headings_theme, listbox_bg=None, listbox_fg=None, console_bg=None, button_bg=None):
        """Updates the headings theme colors and refreshes the view."""
        self.header_theme = new_headings_theme
        # Update listbox_bg if provided, but check for contrast with console_bg
        if listbox_bg is not None:
            if console_bg and listbox_bg == console_bg:
                self.listbox_bg = button_bg if button_bg else "#333333"
            else:
                self.listbox_bg = listbox_bg
        # Update listbox_fg if provided
        if listbox_fg is not None:
            self.listbox_fg = listbox_fg
        # Get the actual font configuration to ensure consistent sizing
        import tkinter.font as tkfont
        default_font = tkfont.Font(font=self.cget("font"))
        font_family = default_font.actual()["family"]
        font_size = default_font.actual()["size"]
        
        # Update tag configurations with new colors
        self.tag_configure("H1", font=(font_family, font_size + 14), foreground=self.header_theme[0])
        self.tag_configure("H2", font=(font_family, font_size + 6, "bold"), foreground=self.header_theme[1])
        self.tag_configure("H3", font=(font_family, font_size + 2, "bold"), foreground=self.header_theme[2])
        self.tag_configure("H4", font=(font_family, font_size, "bold"), foreground=self.header_theme[3])
        self.tag_configure("HorizontalRule", foreground=self.header_theme[4])
        self.tag_configure("CODE", background=self.listbox_bg, foreground=self.listbox_fg)
        # Refresh the view to apply new colors
        self.refresh_view()

    def toggle_markdown(self):
        self.markdown_enabled = not self.markdown_enabled
        self.refresh_view()

    def refresh_view(self):
        # 1. Store what's currently there before we wipe it
        # (Only if raw_text is empty, otherwise we use the stored raw_text)
        if not self.raw_text:
            self.raw_text = self.get("1.0", tk.END).strip()

        self.config(state="normal")
        self.delete("1.0", tk.END)
        
        if self.markdown_enabled:
            # Re-run the working logic
            self._simple_format(self.raw_text)
        else:
            # Just put the plain text back
            self.insert("1.0", self.raw_text)
            
        self.config(state="disabled")
        self.see(tk.END)  # Auto-scroll to bottom after rendering

    def format_new_content(self):
        # 1. Store what's currently there before we wipe it
        # (Only if raw_text is empty, otherwise we use the stored raw_text)
        if not self.raw_text:
            self.raw_text = self.get("1.0", tk.END).strip()
        self.config(state="normal")       
        if self.markdown_enabled:
            # Re-run the working logic
            self._simple_format(self.raw_text)
        else:
            # Just put the plain text back
            self.insert("1.0", self.raw_text)
            self.config(state="disabled")
    #before changin
    def _simple_format(self, content):
        lines = content.split('\n')
        in_code_block = False ###
        for line in lines:
            #stripped = line.strip()
            # --- Order of checks matters ---
            # Check for the ASCII/Code fence
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                #add space empty lines
                display_line = line if line.strip() else " "
                # This is where the magic happens for the Space Wizard
                self.insert("end", display_line + "\n", "CODE")
                continue
            # start of actual parsing
            # 1. Horizontal Rules (---, ***, ___, or extended versions)
            if re.match(r'^[-*_]{3,}\s*$', line.strip()):
                self.insert("end", "\n")
                # Use Unicode horizontal line character for a continuous line
                self.insert("end", "─" * 40, "HorizontalRule")
                self.insert("end", "\n")
                continue
            
            # 2. Headings (Check these before bullets, as # doesn't conflict with *)
            if line.startswith('# '):
                self._insert_formatted_line(line[2:], "H1")
                continue
            elif line.startswith('## '):
                self._insert_formatted_line(line[3:], "H2")
                continue
            elif line.startswith('### '):
                self._insert_formatted_line(line[4:], "H3")
                continue
            elif line.startswith('#### '):
                self._insert_formatted_line(line[5:], "H4")
                continue

            # 3. Indented Bullet Points (Basic handling)
            if line.startswith('    * ') or line.startswith('    ○ '):
                # Remove leading spaces and '* ', then strip any remaining leading spaces
                stripped = line.strip()[2:]
                # Check if the bullet text contains a heading
                if stripped.startswith('# '):
                    # It's H1 heading within indented bullet point - strip the # and keep the rest
                    heading_text = stripped[2:].lstrip()
                    clean_line = "    ○ " + heading_text
                    self.insert("end", clean_line + "\n", "BULLET_MORE_H1")
                elif stripped.startswith('## '):
                    # It's H2 heading within indented bullet point
                    heading_text = stripped[3:].lstrip()
                    clean_line = "    ○ " + heading_text
                    self.insert("end", clean_line + "\n", "BULLET_MORE_H2")
                elif stripped.startswith('### '):
                    # It's H3 heading within indented bullet point
                    heading_text = stripped[4:].lstrip()
                    clean_line = "    ○ " + heading_text
                    self.insert("end", clean_line + "\n", "BULLET_MORE_H3")
                elif stripped.startswith('#### '):
                    # It's H4 heading within indented bullet point
                    heading_text = stripped[5:].lstrip()
                    clean_line = "    ○ " + heading_text
                    self.insert("end", clean_line + "\n", "BULLET_MORE_H4")
                else:
                    # Normal indented bullet point
                    clean_line = "    ○ " + stripped.lstrip()
                    self._insert_formatted_line(clean_line, "BULLET_MORE")
                continue

            # 4. Bullet Points
            if line.strip().startswith('* ') or line.strip().startswith('•'):
                # Replace '* ' with a bullet character and remove extra spaces after bullet
                stripped = line.strip()[1:]  # Remove '*'
                # Check if the bullet text contains a heading
                if stripped.startswith('# '):
                    # It's H1 heading within bullet point - strip the # and keep the rest
                    heading_text = stripped[2:].lstrip()
                    clean_line = "  • " + heading_text
                    self.insert("end", clean_line + "\n", "BULLET_H1")
                elif stripped.startswith('## '):
                    # It's H2 heading within bullet point
                    heading_text = stripped[3:].lstrip()
                    clean_line = "  • " + heading_text
                    self.insert("end", clean_line + "\n", "BULLET_H2")
                elif stripped.startswith('### '):
                    # It's H3 heading within bullet point
                    heading_text = stripped[4:].lstrip()
                    clean_line = "  • " + heading_text
                    self.insert("end", clean_line + "\n", "BULLET_H3")
                elif stripped.startswith('#### '):
                    # It's H4 heading within bullet point
                    heading_text = stripped[5:].lstrip()
                    clean_line = "  • " + heading_text
                    self.insert("end", clean_line + "\n", "BULLET_H4")
                else:
                    # Normal bullet point
                    clean_line = "  • " + stripped.lstrip()  # Remove any remaining leading spaces
                    # We still need to process bold/italic inside the bullet point
                    self._insert_formatted_line(clean_line, "BULLET")
                continue

            # 5. Default: Handle lines with Bold, Italic, or Plain text
            # We use a helper to handle mixing bold/italic in the same line
            self._insert_formatted_line(line)
            
    def _insert_formatted_line(self, line, base_tag=None):
        """Helper to insert a line handling mixed bold/italic formatting."""
        # Regex to find bold (**...**) or italic (*...*)
        # We split by the pattern but keep the delimiters
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*)', line)
        
        for part in parts:
            if not part: continue
            
            if part.startswith('**') and part.endswith('**'):
                # It's bold - strip the ** markers
                bold_text = part[2:-2]
                # If there's a base_tag (like BULLET), use the appropriate bold variant tag
                if base_tag == "BULLET":
                    self.insert("end", bold_text, "BULLET_BOLD")
                elif base_tag == "BULLET_MORE":
                    self.insert("end", bold_text, "BULLET_MORE_BOLD")
                elif base_tag:
                    self.insert("end", bold_text, (base_tag, "BOLD"))
                else:
                    self.insert("end", bold_text, "BOLD")
            elif part.startswith('*') and part.endswith('*'):
                # It's italic (ensure it's not a bullet point leftover)
                italic_text = part[1:-1]
                # If there's a base_tag (like BULLET), use the appropriate italic variant tag
                if base_tag == "BULLET":
                    self.insert("end", italic_text, "BULLET_ITALIC")
                elif base_tag == "BULLET_MORE":
                    self.insert("end", italic_text, "BULLET_MORE_ITALIC")
                elif base_tag:
                    self.insert("end", italic_text, (base_tag, "ITALIC"))
                else:
                    self.insert("end", italic_text, "ITALIC")
            else:
                # It's plain text
                if base_tag:
                    self.insert("end", part, base_tag)
                else:
                    self.insert("end", part)
        
        # Add the newline at the end of the processed line
        if base_tag:
            self.insert("end", "\n", base_tag)
        else:
            self.insert("end", "\n")
