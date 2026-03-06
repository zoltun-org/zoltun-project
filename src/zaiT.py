import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.constants import * # Importing constants from tkinter
import subprocess
import tkinterdnd2 as tkdnd
import tkinter.ttk as ttk
import threading
import json
import sys #for sys exit
import webbrowser #for the hyperlink
#import pywinstyles

#from datetime import datetime
from zai import ZaiClient
from mdWidgetDone import SmartChatWidget
from dotenv import load_dotenv
import os
import shutil
from apiSplash import show_splash_screen
from apiSplash import extract_assets
from apiSplash import noApiKey
from apiSplash import lighten
from apiSplash import get_theme_files

# Initialization logic before the App class
if __name__ == '__main__':
    # Run extraction if we are in the frozen executable
    if getattr(sys, 'frozen', False):
        extract_assets()
    print("End of dealing with build Starting zaiT...")
##
load_dotenv()
#check once
api_key = os.getenv("ZAI_API_KEY")

if not api_key:
    api_key = noApiKey()
    
class App:
    def __init__(self, root):
        ###TITLE COLOR CHANGE ### Breaks tons of stuff have to redo title bar from scratch to get it working
        #about for cumulative totals on tokens
        self.cumulative_input = 0
        self.cumulative_output = 0
        # Reload .env in case it was just created by noApiKey()
        # Minimal tkinter app"""
        self.root = root
        self.root.bind("<Control-Shift-Z>", self.snap_to_standard)
        ###ICON WORKING USES PNG 1024x1024####
        try:
            icon = tk.PhotoImage(file="zoltun.png")
            root.iconphoto(True, icon)
        except Exception as e:
            print(f"Could not load icon: {e}")
        #####WORKING ICON###
        load_dotenv(override=True)
        self.api_key = os.getenv("ZAI_API_KEY")
        if not self.api_key:
            # Final fallback check
            self.api_key = api_key

        self.root.title("Zoltun AI Open Platform v1.0")
        self.root.geometry("800x600")

        lighten("#D3D3D3", 30)
        ########## JSON ########## needs to be function
        #double = self.load_default_theme()
        #jsonNameTheme = self.load_default_theme() #working one
        returned = self.load_default_theme() #array return with nested key/val dict watch out
        #returned is a list with a nested key value dict so I can return all settings if needed at once
        self.maxR = returned[1]["max_tokens"]
        #print("maxR ",maxR)
        self.modelR = returned[1]["model"]
        self.endpointR = returned[1]["endpoint"]
        self.endpoints = returned[1]["endpoints"]
        jsonNameTheme = returned[0] #its 0 of return from func with full filepath not settings.json list

        #data = None #changed from string
        #checks if default or directory for json theme file
        if jsonNameTheme == "theme.json":
            data = open(jsonNameTheme)
        else:
            data = open('./theme/' + jsonNameTheme)
        print("Datatype before deserialization : "+ str(data))
        theme = data
        #theme = open('./theme/darktheme.json')
        print("Datatype before deserialization : "+ str(theme))
        t = json.load(theme)
        ##Prevent scope crashes
        self.t_type = t["t_type"]  # Set a safe default value
        ## end prevent scope crash
        if t["simple"] == "yes":
            aC = t["arrayOfColors"]
            zeroth = aC[0]
            self.bg_rightpanel = zeroth
            first = aC[1]
            self.console_bg = self.prompt_fg = self.button_border = self.button_fg = self.listbox_fg = self.label_fg = first
            second = aC[2]
            self.console_fg = self.prompt_bg = self.listbox_bg = second
            third = aC[3]
            self.button_bg = third
            fourth = aC[4]
            self.button_icon = fourth
            # Use headings from theme if available, otherwise None
            self.headings_theme = t.get("headings", None)
            self.font = t["font"]
            print("Font simple ", self.font)
        else:
            #print("bg_rightpanel", str(t['bg_rightpanel']))
            self.bg_rightpanel = t["bg_rightpanel"]
            self.button_bg = t["button_bg"]
            self.console_bg = t["console_bg"]
            self.console_fg = t["console_fg"]
            self.button_fg = t["button_fg"]
            self.button_icon = t["button_icon"]
            self.button_border = t["button_border"]
            self.t_type = t["t_type"]
            #self.not_type = t["not_type"]
            self.whichTheme = t["theme"]
            self.prompt_fg = t["prompt_fg"]
            self.prompt_bg = t["prompt_bg"]
            self.listbox_fg = t["listbox_fg"]
            self.listbox_bg = t["listbox_bg"]
            self.label_fg = t["label_fg"]
            self.label_bg = t["label_bg"]
            self.headings_theme = t["headings"]
            self.font = t["font"]
            print("Font complex ", self.font)
        # File list header
        #tk.Label(self.right_panel, text="Markdown Files", bg='lightblue', font=(self.font, 10, "bold")).pack(pady=5)
            
        ############ END JSON ########################

        ##Colors should be imported from a json
        opac = t["opacity"]
        #opac = str(d[opacity])
        self.root.attributes('-alpha', opac) # Set window transparency to 90%
        # Initialize conversation history for multi-turn support
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        # Track current filename for multi-turn conversations
        self.current_filename = None
        # Simple right panel for file list

        
        self.right_panel = tk.Frame(self.root, bg=self.bg_rightpanel, width=200)
        self.right_panel.pack(fill='y', side=tk.RIGHT)
        self.right_panel.pack_propagate(False)
        self.console_text = SmartChatWidget(state='disabled',
                                            bg=self.console_bg,
                                            fg=self.console_fg,
                                            headings_theme=self.headings_theme, #added for passing to mdwidget theme
                                            listbox_bg=self.listbox_bg, #pass listbox background color for code blocks
                                            listbox_fg=self.listbox_fg, #pass listbox foreground color for code text
                                            console_bg=self.console_bg, #pass console background for contrast check
                                            button_bg=self.button_bg, #pass button background as fallback for code background
                                            padx=30,  # This creates a 30px gap on BOTH sides
                                            pady=10
                                            )
        self.console_text.pack(expand=True, fill='both')
        
        ## DROPDOWN 1
        themesF = get_theme_files() #can prob get that other var from earlier
        print("themes available: ", themesF)
        # Create Dropdown (Combobox) BROKEN above prompt
        self.theme_combo = ttk.Combobox(self.right_panel, state="readonly") # state="readonly" prevents typing
        self.combo_style = ttk.Style()
        self.combo_style.theme_use('clam') #I have no idea why I need this
        if self.t_type == "matrix":
            self.combo_style.configure('TCombobox', foreground ="", fieldbackground=self.console_bg, background=self.console_bg) #background is arrow, foreground is text occasionally
        elif self.t_type == "inverse":
            self.combo_style.configure('TCombobox', foreground ="", fieldbackground=self.console_bg, background=self.console_fg) #background is arrow, foreground is text occasionally
        else: #PLACEHOLDER REPLACE if nec
            self.combo_style.configure('TCombobox', foreground ="", fieldbackground=self.console_bg, background=self.console_fg) 
        self.theme_combo.pack(pady=10, padx=0, fill='x')
        # Populate the Dropdown
        self.theme_combo['values'] = themesF
        if themesF:
            # Select the saved default theme if it exists in the list, otherwise select first item
            if jsonNameTheme in themesF:
                self.theme_combo.current(themesF.index(jsonNameTheme))
            else:
                self.theme_combo.current(0) # Select the first item by default
            self.theme_combo.bind("<<ComboboxSelected>>", self.apply_theme) # Bind selection event to apply_theme
            self.apply_theme() # Apply it immediately on startup
        ## End combobox

        # File list header
        self.file_list_header = tk.Label(self.right_panel, text="Other Markdown Files", fg=self.button_fg, bg=self.bg_rightpanel, font=(self.font, 10, "bold"))
        self.file_list_header.pack(pady=5)
        
        # File listbox - give it specific height instead of expand
        self.file_listbox = tk.Listbox(self.right_panel, fg=self.listbox_fg, bg=self.listbox_bg, height=8)
        self.file_listbox.pack(fill='both', padx=5, pady=5)
        self.file_listbox.bind('<Double-Button-1>', self.open_selected_file)

        # Session list header
        self.session_list_header = tk.Label(self.right_panel, text="Sessions", fg=self.button_fg, bg=self.bg_rightpanel, font=(self.font, 10, "bold"))
        self.session_list_header.pack(pady=5)

        # Session listbox - give it specific height instead of expand
        self.file_seshbox = tk.Listbox(self.right_panel, fg=self.listbox_fg, bg=self.listbox_bg, height=8)
        self.file_seshbox.pack(fill='both', padx=5, pady=5)
        self.file_seshbox.bind('<Button-1>', self.open_selected_file)
        #sort with os.path.getctime()
        
        # Refresh file list button
        self.refresh_button = tk.Button(self.right_panel, text="Refresh", command=self.refresh_file_list, bg=self.button_bg)
        self.refresh_button.pack(pady=5)
        
        # Clear console button
        self.clear_console_button = tk.Button(self.right_panel, text="Begin New Task", command=self.clear_console, bg=self.button_bg)
        self.clear_console_button.pack(pady=5)
        #tk.Button(self.right_panel, text="Refresh Sessions", command=self.refresh_sesh_list, bg=self.prompt_bg).pack(pady=5)

        self.toggle_btn = tk.Checkbutton(
            self.right_panel,
            text="Markdown",
            command=self.console_text.toggle_markdown,
            bg=self.button_bg,
            fg=self.button_fg,
            selectcolor=self.button_bg,  # Color of the checkmark
        )
        self.toggle_btn.pack()
        self.toggle_btn.select() # Set to OFF by default


        #token display for debugging purposes, we can remove this later or make it a toggle in the settings, for now we can just have it always on for testing
        self.tokens_group = tk.Frame(self.right_panel, bg=self.bg_rightpanel) # Group frame for token display
        self.tokens_group.pack(pady=10)
        self.tokens_group_l = tk.Label(self.tokens_group, text="Session #'s", fg=self.button_fg, bg=self.bg_rightpanel, font=(self.font, 10, "bold"))
        self.tokens_group_l.pack()

        #tk.Label(self.right_panel, text="Tokens", fg=button_fg, bg=bg_rightpanel, font=(self.font, 10, "bold")).pack(pady=2)
        ##########MODEL LABEL ############
        #### SHOULD BE DROPDOWN #######
        modelVar = self.modelR
        # Create Dropdown 2 for model selection
        self.model_combo = ttk.Combobox(self.tokens_group, state="normal") # state="normal" allows typing
        self.model_style = ttk.Style()
        self.model_style.theme_use('clam') #I have no idea why I need this
        # Style the model combobox to match theme
        if self.t_type == "matrix":
            self.model_style.configure('TCombobox', foreground ="", fieldbackground=self.console_bg, background=self.console_bg) #background is arrow, foreground is text occasionally
        elif self.t_type == "inverse":
            self.model_style.configure('TCombobox', foreground ="", fieldbackground=self.console_bg, background=self.console_fg) #background is arrow, foreground is text occasionally
        else: #PLACEHOLDER REPLACE if nec
            self.model_style.configure('TCombobox', foreground ="", fieldbackground=self.console_bg, background=self.console_fg)
        self.model_combo.pack(pady=10, padx=0, fill='x')##########
        self.model_combo.pack_forget() #################### hides the model dropdown, remove when more models
        # Load models from settings.json
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                modelF = settings.get("models", ["glm-4.7"])  # Default list if not found
        except Exception as e:
            print(f"Error loading models from settings.json: {e}")
            modelF = ["glm-4.7"]  # Fallback to default
        
        # Populate the Dropdown
        self.model_combo['values'] = modelF
        if modelF:
            # Select the saved default model if it exists in the list, otherwise select first item
            if self.modelR in modelF:
                self.model_combo.current(modelF.index(self.modelR))
            else:
                self.model_combo.current(0) # Select the first item by default
            # Bind selection event to apply_model
            self.model_combo.bind("<<ComboboxSelected>>", self.apply_model)
            # Apply it immediately on startup
            self.apply_model()
        ## End model combobox



        # Display current model
        #self.model_label = tk.Label(self.tokens_group, text=f"Model: {modelVar}" , fg=self.label_fg, bg=self.bg_rightpanel, font=(self.font, 8))
        #self.model_label.pack()
        self.total_tokens_label = tk.Label(self.tokens_group, text="Context: 0 (0)" , fg=self.label_fg, bg=self.bg_rightpanel, font=(self.font, 8))
        self.total_tokens_label.pack()
        self.input_tokens_label = tk.Label(self.tokens_group, text="Input: 0 (0)" , fg=self.label_fg, bg=self.bg_rightpanel, font=(self.font, 8))
        self.input_tokens_label.pack()
        self.output_tokens_label = tk.Label(self.tokens_group, text="Output: 0 (0)" , fg=self.label_fg, bg=self.bg_rightpanel, font=(self.font, 8))
        self.output_tokens_label.pack()
        
        # Left content area
        self.left_area = tk.Frame(self.root, bg=self.bg_rightpanel) #we avoided bg=bg_rightpanel background because button use is kludgy and we want to use the button_bg color for the button background and the button_border color for the border, if we set the bg for the left area to button_bg then we would have a hard time doing a border for the button since it would be the same color as the background, by setting it to bg_rightpanel we can use that as a "border" color for the button and then set the button background to button_bg to create a nice contrast, we can also do some custom colors for the tags in the markdown widget to make it look nicer, we can import these from a json file later to make it customizable but for now we can just hardcode some nice colors
        self.left_area.pack(expand=True, fill='both', side=tk.LEFT)
        
        # Add a text box where we are going to write to prompt
        self.text_box = tk.Text(self.left_area,height=5, width=400, font=(self.font, 12), fg=self.prompt_fg, bg=self.prompt_bg)
        self.text_box.pack(side=tk.BOTTOM, anchor="s", padx=8, pady=8)
        self.text_box.insert(tk.END, "Enter your prompt here...")
        self.text_box.bind("<FocusIn>", lambda event: self.text_box.delete("1.0", tk.END) if self.text_box.get("1.0", tk.END).strip() == "Enter your prompt here..." else None)
        self.text_box.bind("<Return>", self._on_submit_return)  # Handle Enter key to submit
        # We add a button to test our setup
        #Border hack-y workaround to make the button look like a frame for buttons
        self.frame = tk.Frame(self.left_area, bg=self.button_border, width=100, padx=1, pady=1) #black border frame only change for night mode, for light mode we can do bg="lightgray" and remove the inner bg from the button
        self.frame.pack(pady=10, padx=10)
        #Button to test the setup PROMPT BUTTON
        self.test_button = tk.Button(self.frame, width=100, bg=self.button_icon, text="⏎  Submit prompt", command=lambda: [self.prompt(self.text_box.get(1.0, 'end')), self.text_box.delete("1.0", tk.END)])
        self.test_button.bind("<Return>", self._on_submit_return)
        self.test_button.pack(pady=0)
        #Button to test the setup SAVE to MD BUTTON and TOGGLE INPUT BUTTON
        self.frame = tk.Frame(self.left_area, padx=0, pady=0, bg=self.bg_rightpanel) #button blends with rightpanel background, we can do some custom colors for the tags in the markdown widget to make it look nicer, we can import these from a json file later to make it customizable but for now we can just hardcode some nice colors
        self.frame.pack(pady=10, padx=10)
        self.save_button = tk.Button(self.frame, width=50, bg=self.button_icon, text="💾   Save to .md file", command=lambda: self.write_to_md(self.console_text.get(1.0, 'end')))
        self.save_button.pack(side=tk.LEFT, pady=1, padx=5)
        #self.save_button.pack(side=tk.LEFT, pady=1, padx=5)
        self.toggle_button = tk.Button(self.frame, width=50, bg=self.button_icon, text="📝  Toggle Input", command=self.toggle_textbox)
        self.toggle_button.pack(side=tk.LEFT, pady=1, padx=5)

        # Initialize file list after all widgets are created
        self.root.after(100, self.refresh_file_list)
        self.root.after(100, self.refresh_sesh_list)
        self.root.after(100, self.console_text.refresh_view)  # Ensure markdown is rendered on startup

    def snap_to_standard(self, event=None):
        """Resets window to the Zoltun-standard 710px width."""
        f_size = self.font_size_console if self.font_size_console is not None else 12
        # Adjust height based on font weight, but keep width locked
        target_h = 700 if f_size < 18 else 850
        self.root.geometry(f"710x{target_h}")
        self.root.update_idletasks()
        print(f"Snapped to 710px (Font size: {f_size})")
    
    def _on_submit_return(self, event):
        """Handle Return key press on submit button."""
        self.test_button.focus_set()  # Give button focus
        self.prompt(self.text_box.get(1.0, 'end'))
        self.text_box.delete("1.0", tk.END)
        return "break"  # Prevent default Return key behavior
    
    def prompt(self, prompt):
        print("Prompt function called with:", prompt)
        # logic to handle the prompt
        self.console_text.config(state='normal') # Enable text widget for writing
        #self.console_text.delete('1.0', END) # Clear previous content this causes problems in multiple turns since we lose the conversation history, need to find a way to keep the history but still clear the screen for new response
        self.console_text.config(state='disabled') # Disable text widget for writing
        print(f"Received prompt: {prompt}")
        # Run streaming in a separate thread to avoid blocking GUI MARKDOWN RENDERING still has some issues with streaming but this is a start, we can do some optimizations later to make it smoother
        thread = threading.Thread(target=self._stream_response, args=(prompt,self.api_key))
        thread.daemon = True  # Thread will close when main program exits
        thread.start()
    
    def _stream_response(self, prompt, api_key_passed):
        # Append user message to conversation history
        print("ModelR ", self.modelR, "MAXR ", self.maxR)
        self.conversation_history.append({"role": "user", "content": prompt})
        
        # Add user prompt to the display buffer with formatting
        prompt_display = f"PROMPT: {prompt.upper()}"
        if self.console_text.raw_text:
            self.console_text.raw_text += "\n\n" + prompt_display
        else:
            self.console_text.raw_text = prompt_display
        #####ACTUAL API CALL ####
        # N.B GLM5 is "glm-5" no decimal#######
        ####Have to modularize client call####
        client = ZaiClient(api_key=api_key_passed, # Your API Key passed from .env
                           base_url=self.endpointR
                           )
        response = client.chat.completions.create(
            model=self.modelR, #model default "glm-4.7" modelR from settings.json model
            messages=self.conversation_history,  # Use full conversation history
            stream=True,  # Enable streaming output Breaks stuff
            thinking={
                "type": "disabled", #show thinking default "disabled"
            },
            max_tokens=self.maxR, #was 4096 no quotes value now from settings.json max_tokens and saved here as maxR
            temperature=1.0 #was 1.0 no quotes value will come from settings.json temperature and saved here as ??? 
        )
        ########## END CALL ##########
        #print("ABSOLUTELY FULL RESPONSE BELOW BEFOR FORMATTING:", response)
        full_response = self.streaming_out(response)
        
        # Append assistant response to conversation history
        if full_response:
            self.conversation_history.append({"role": "assistant", "content": full_response})
        # Get complete response need to pipe this back to the console_text widget
        self.console_text.config(state='normal')
        self.console_text.config(state='disabled')
        self.auto_md(prompt, self.console_text.get(1.0, 'end'))
        #self.markdown_to_html(full_content)
        #new line might nowt work here since we are streaming, need to pipe this back to the console_text widget        

    def streaming_out(self, response_in): # Process streaming response
        full_content = "" #full content blanked out for testing purposes
        usage_info = None  # Store usage info from final chunk
        try:
            for chunk in response_in:
                # Check if chunk has choices and the first choice has a delta
                if hasattr(chunk, 'choices') and chunk.choices:
                    choice = chunk.choices[0]
                    if hasattr(choice, 'delta'):
                        delta = choice.delta
                        # Handle incremental content
                        if hasattr(delta, 'content') and delta.content:
                            full_content += delta.content
                            # Update UI in real-time
                            self.console_text.config(state='normal')
                            self.console_text.insert(tk.END, delta.content)
                            self.console_text.see(tk.END)
                            self.console_text.config(state='disabled')
                            self.root.update_idletasks()  # Force UI update                
                        # Check if completed and capture usage info
                        """if hasattr(choice, 'finish_reason') and choice.finish_reason:
                            print(f"\n\nCompletion reason: {choice.finish_reason}")
                            if hasattr(chunk, 'usage') and chunk.usage: #token block
                                usage_info = chunk.usage
                                print(f"Token usage: Input {usage_info.prompt_tokens}, Output {usage_info.completion_tokens}")
                                model_info = chunk.model #should be separate if but Im lazy and want to make dinner
                                print(f"Model used: {model_info}") """
            self.console_text.raw_text += "\n\nRESPONSE:\n\n" + full_content + "\n\n---"
            if self.console_text.markdown_enabled:
                self.console_text.refresh_view() # Format inseead of REFRESHVIEW to avoid resetting the scroll during streaming
        except Exception as e:
            print(f"Streaming error: {e}")
            # Fallback: try to get complete response
            self.console_text.config(state='normal')
            self.console_text.insert(tk.END, f"\n\nStreaming error occurred. Partial response:\n{full_content}")
            self.console_text.config(state='disabled')
        #DIAG #print(f"Full content: {full_content}")

        # Update token labels with usage info
        if usage_info:
            # In streaming_out, when updating labels:
            self.total_tokens_label.config(text=f"Total: {usage_info.total_tokens} ({self.cumulative_input + self.cumulative_output + usage_info.total_tokens})")
            self.input_tokens_label.config(text=f"Input: {usage_info.prompt_tokens} ({self.cumulative_input + usage_info.prompt_tokens})")
            self.output_tokens_label.config(text=f"Output: {usage_info.completion_tokens} ({self.cumulative_output + usage_info.completion_tokens})")
            # Then update cumulative totals
            self.cumulative_input += usage_info.prompt_tokens
            self.cumulative_output += usage_info.completion_tokens
            #model version number is in the chunk.model field, we can display this in the UI as well, we can also do some parsing to make it look nicer if needed, for now we can just display the raw model string
            #self.model_label.config(text=f"Model: {model_info}")
        return full_content  # Return the full response for conversation history

    def toggle_textbox(self):
        if self.text_box.winfo_viewable():
            self.text_box.pack_forget()
        else:
            self.text_box.pack(side=tk.BOTTOM, anchor="s", padx=8, pady=8)
    
    def refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        try:
            current_dir = os.getcwd()
            print(f"Current directory: {current_dir}")
            files = os.listdir('.')
            #DIAG #print(f"Files found: {files}")
            md_files = [f for f in files if f.endswith('.md')]
            #DIAG #print(f"MD files found: {md_files}")
            for file in md_files:
                self.file_listbox.insert(tk.END, file)
            self.root.update_idletasks()  # Force UI update
        except Exception as e:
            print(f"Error refreshing file list: {e}")

    def refresh_sesh_list(self):
        self.file_seshbox.delete(0, tk.END)
        initial_dir = os.getcwd()
        print(f"Initial directory: {initial_dir}")
        try:
            sessions_dir = os.path.join(initial_dir, "sessions")
            print(f"Sessions directory: {sessions_dir}")
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir, exist_ok=True)
            files = os.listdir(sessions_dir)
            #DIAG #print(f"Files found: {files}")
            md_files = [f for f in files if f.endswith('.md')]
            #DIAG #print(f"MD files found: {md_files}")
            for file in md_files:
                self.file_seshbox.insert(tk.END, file)
            self.root.update_idletasks()  # Force UI update
        except Exception as e:
            print(f"Error refreshing file list: {e}")
        

    
    def open_selected_file(self, event):
        selection = [ 'x' , 0]
        # 0 is listbox, 1 is seshbox
        if event.widget == self.file_listbox:
            selection[0] = self.file_listbox.curselection()
            selection[1] = 0
        elif event.widget == self.file_seshbox:
            selection[0] = self.file_seshbox.curselection()
            selection[1] = 1
        if selection[0]:
            filename = self.file_listbox.get(selection[0]) if selection[1] == 0 else self.file_seshbox.get(selection[0])
            try:
                # Try UTF-8 first, then fallback to other encodings
                try:
                    if selection[1] == 0:
                        with open(filename, 'r', encoding='utf-8') as f:
                            content = f.read()
                    else:
                        with open(f"sessions/{filename}", 'r', encoding='utf-8') as f:
                            content = f.read()
                except UnicodeDecodeError:
                    # Fallback to cp1252 (Windows common encoding)
                    with open(filename, 'r', encoding='cp1252', errors='replace') as f:
                        content = f.read()
                self.console_text.config(state='normal')
                self.console_text.delete(1.0, tk.END)
                self.console_text.insert(tk.END, f"--- Content of {filename} ---\n\n")
                self.console_text.insert(tk.END, content)
                self.console_text.config(state='disabled')
                # New refresh function implementation that uses the raw_text buffer and refresh_view for markdown rendering
                self.console_text.config(state='normal')
                self.console_text.delete(1.0, tk.END)
                # Update the buffer
                self.console_text.raw_text = content 
                # Trigger the render
                if self.console_text.markdown_enabled:
                    self.console_text.refresh_view()
                else:
                    self.console_text.insert(tk.END, content)
                    self.console_text.config(state='disabled')
            except Exception as e:
                print(f"Error opening file {filename}: {e}")
                messagebox.showerror("Error", f"Could not open file {filename}: {e}")
    
    def write_to_md(self, text):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            title="Save as Markdown"
        )
        if file_path:
            with open(file_path, "w", encoding='utf-8') as md_file:
                md_file.write(text)
            self.refresh_file_list()  # Refresh file list after saving
    def auto_md(self, prompt, text):
        # Use current_filename for multi-turn conversations, or generate from first prompt
        if self.current_filename is None:
            # New conversation - generate filename from first prompt
            import re
            # Take first 50 characters, remove invalid chars, replace spaces with underscores
            safe_prompt = re.sub(r'[<>:"/\\|?*]', '', prompt[:50]).strip()
            safe_prompt = re.sub(r'\s+', '_', safe_prompt)
            self.current_filename = f"{safe_prompt}.md" if safe_prompt else "autosave.md"
        
        # Ensure sessions directory exists and save there
        os.makedirs('sessions', exist_ok=True) # Create sessions directory if it doesn't exist
        filepath = os.path.join('sessions', self.current_filename)
        #should make it if not there
        
        # Check if file exists to decide whether to write or append
        if os.path.exists(filepath):
            # Append to existing file with separator
            with open(filepath, "a", encoding='utf-8') as md_file:
                md_file.write("\n\n---\n\n")  # Add separator between turns
                md_file.write(text)  # Append new response
        else:
            # Create new file with full content
            with open(filepath, "w", encoding='utf-8') as md_file:
                md_file.write(text)
        
        self.refresh_sesh_list()  # Refresh session list after saving
    
    def clear_console(self):
        """Clear the console display and reset conversation history for a fresh start."""
        # Clear the console display
        self.console_text.config(state='normal')
        self.console_text.delete('1.0', tk.END)
        self.console_text.config(state='disabled')
        
        # Reset the raw_text buffer
        self.console_text.raw_text = ""
        
        # Reset conversation history to just the system message
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        # Reset filename for new conversation
        self.current_filename = None
        print("Console cleared, conversation history reset, and filename reset")
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
        ########### Start theme list, next func is retrieval
    
    def load_default_theme(self):
        """Load the default theme from settings.json."""
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                max_tokens = settings.get("max_tokens")
                model = settings.get("model")
                set_me = max_tokens, model
                print("Set me ", set_me)
                print("max tokens ", max_tokens, "model ", model)
                default_theme = settings.get("default_theme", "aquatic.json")
                # Verify the theme file exists
                if os.path.exists(os.path.join("theme", default_theme)):
                    return default_theme, settings #set_me
                else:
                    print(f"Theme file {default_theme} not found, using aquatic.json")
                    return "aquatic.json", settings
        except FileNotFoundError:
            print("settings.json not found, using aquatic.json")
            # Return default settings when file not found
            default_settings = {
                "max_tokens": 120000,
                "model": "glm-4.7",
                "endpoint": "https://api.z.ai/api/paas/v4/",
                "endpoints": {
                    "regular": "https://api.z.ai/api/paas/v4/",
                    "code": "https://api.z.ai/api/coding/paas/v4",
                    "token": "https://api.z.ai/api/monitor/usage/quota/limit",
                    "model": "https://api.z.ai/api/monitor/usage/model-usage"
                }
            }
            return "aquatic.json", default_settings
        except Exception as e:
            print(f"Error loading default theme: {e}, using aquatic.json")
            # Return default settings on error
            default_settings = {
                "max_tokens": 120000,
                "model": "glm-4.7",
                "endpoint": "https://api.z.ai/api/paas/v4/",
                "endpoints": {
                    "regular": "https://api.z.ai/api/paas/v4/",
                    "code": "https://api.z.ai/api/coding/paas/v4",
                    "token": "https://api.z.ai/api/monitor/usage/quota/limit",
                    "model": "https://api.z.ai/api/monitor/usage/model-usage"
                }
            }
            return "aquatic.json", default_settings
    
    def save_default_theme(self, theme_file):
        """Save the selected theme as default in settings.json."""
        try:
            # Read existing settings
            try:
                with open("settings.json", "r") as f:
                    settings = json.load(f)
            except FileNotFoundError:
                settings = {}
            
            # Update default_theme
            settings["default_theme"] = theme_file
            
            # Write back to settings.json
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            
            print(f"Saved default theme: {theme_file}")
        except Exception as e:
            print(f"Error saving default theme: {e}")
    
    def save_default_model(self, model_name):
        """Save the selected model as default in settings.json."""
        try:
            # Read existing settings
            try:
                with open("settings.json", "r") as f:
                    settings = json.load(f)
            except FileNotFoundError:
                settings = {}
            
            # Update model
            settings["model"] = model_name
            
            # Write back to settings.json
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            
            print(f"Saved default model: {model_name}")
        except Exception as e:
            print(f"Error saving default model: {e}")
    
    def apply_model(self, event=None):
        """Apply the selected model."""
        selected_model = self.model_combo.get()
        
        if not selected_model:
            return
        
        # Save the selected model as default
        self.save_default_model(selected_model)
        
        # Update the current model
        self.modelR = selected_model
        if self.modelR == "glm-5":
            self.endpointR = self.endpoints["code"]
        else:
            self.endpointR = self.endpoints["regular"]
        # Update the model label
        #self.model_label.config(text=f"Model: {selected_model}")
        
        print(f"Applied model: {selected_model} endpointR {self.endpointR}")
    
    def _reset_fonts_to_original(self):
        """Reset all widgets to their original font sizes."""
        # Original font sizes from widget initialization
        original_sizes = {
            'console_text': 12,
            'text_box': 12,
            'file_listbox': None,  # Use tkinter default
            'file_seshbox': None,  # Use tkinter default
            'test_button': None,  # Use tkinter default
            'save_button': None,  # Use tkinter default
            'toggle_button': None,  # Use tkinter default
            'refresh_button': None,  # Use tkinter default
            'clear_console_button': None,  # Use tkinter default
            'toggle_btn': None,  # Use tkinter default
            'tokens_group_l': 10,
            'total_tokens_label': None,  # Use tkinter default
            'input_tokens_label': None,  # Use tkinter default
            'output_tokens_label': None,  # Use tkinter default
            'file_list_header': 10,
            'session_list_header': 10,
        }
        
        # Reset fonts to original sizes
        if hasattr(self, 'console_text'):
            try:
                self.console_text.config(font=(self.font, original_sizes['console_text']))
            except:
                pass
        if hasattr(self, 'text_box'):
            try:
                self.text_box.config(font=(self.font, original_sizes['text_box']))
            except:
                pass
        if hasattr(self, 'file_listbox') and original_sizes['file_listbox'] is not None:
            try:
                self.file_listbox.config(font=(self.font, original_sizes['file_listbox']))
            except:
                pass
        if hasattr(self, 'file_seshbox') and original_sizes['file_seshbox'] is not None:
            try:
                self.file_seshbox.config(font=(self.font, original_sizes['file_seshbox']))
            except:
                pass
        for widget_name in ['test_button', 'save_button', 'toggle_button', 'refresh_button', 'clear_console_button']:
            if hasattr(self, widget_name) and original_sizes[widget_name] is not None:
                widget = getattr(self, widget_name)
                try:
                    widget.config(font=(self.font, original_sizes[widget_name]))
                except:
                    pass
        if hasattr(self, 'toggle_btn') and original_sizes['toggle_btn'] is not None:
            try:
                self.toggle_btn.config(font=(self.font, original_sizes['toggle_btn']))
            except:
                pass
        if hasattr(self, 'tokens_group_l'):
            try:
                self.tokens_group_l.config(font=(self.font, original_sizes['tokens_group_l'], "bold"))
            except:
                pass
        for widget_name in ['total_tokens_label', 'input_tokens_label', 'output_tokens_label']:
            if hasattr(self, widget_name) and original_sizes[widget_name] is not None:
                widget = getattr(self, widget_name)
                try:
                    widget.config(font=(self.font, original_sizes[widget_name]))
                except:
                    pass
        if hasattr(self, 'file_list_header'):
            try:
                self.file_list_header.config(font=(self.font, original_sizes['file_list_header'], "bold"))
            except:
                pass
        if hasattr(self, 'session_list_header'):
            try:
                self.session_list_header.config(font=(self.font, original_sizes['session_list_header'], "bold"))
            except:
                pass
    
    def apply_theme(self, event=None):
        """Loads the selected JSON file and applies settings."""
        # ... after selecting the file ...
        self.root.withdraw() # Temporarily hide the window while we calculate fonts/sizes
        selected_file = self.theme_combo.get()
        
        if not selected_file:
            return
        
        # Save the selected theme as default
        self.save_default_theme(selected_file)
        try:
            # Reset fonts to original sizes before applying new theme
            self._reset_fonts_to_original()
            
            # Construct full path to the file
            file_path = os.path.join("theme", selected_file)
            
            with open(file_path, "r") as f:
                t = json.load(f)
            # Parse theme colors from JSON
            if t["simple"] == "yes":
                aC = t["arrayOfColors"]
                self.bg_rightpanel = aC[0]
                self.console_bg = self.prompt_fg = self.button_border = self.button_fg = self.listbox_fg = self.label_fg = aC[1]
                self.console_fg = self.prompt_bg = self.listbox_bg = aC[2]
                self.button_bg = aC[3]
                self.button_icon = aC[4]
                self.headings_theme = t["headings"]
                self.t_type = t["t_type"]
                self.whichTheme = t["theme"]
                self.font = t["font"]
                # Read font sizes from theme only if explicitly specified
                # If not specified, use None to indicate we should not change fonts
                self.font_size_console = t.get("font_size_console")
                self.font_size_textbox = t.get("font_size_textbox")
                self.font_size_listbox = t.get("font_size_listbox")
                self.font_size_button = t.get("font_size_button")
                self.font_size_label = t.get("font_size_label")
                self.font_size_header = t.get("font_size_header")
                # Read window size overrides from theme (optional)
                self.theme_window_width = t.get("window_width")
                self.theme_window_height = t.get("window_height")
            else:
                self.bg_rightpanel = t["bg_rightpanel"]
                self.button_bg = t["button_bg"]
                self.console_bg = t["console_bg"]
                self.console_fg = t["console_fg"]
                self.button_fg = t["button_fg"]
                self.button_icon = t["button_icon"]
                self.button_border = t["button_border"]
                self.t_type = t["t_type"]
                #self.not_type = t["not_type"]
                self.prompt_fg = t["prompt_fg"]
                self.prompt_bg = t["prompt_bg"]
                self.listbox_fg = t["listbox_fg"]
                self.listbox_bg = t["listbox_bg"]
                self.label_fg = t["label_fg"]
                self.label_bg = t["label_bg"]
                self.headings_theme = t["headings"]
                self.whichTheme = t["theme"]
                self.font = t["font"]
                # Read font sizes from theme only if explicitly specified
                # If not specified, use None to indicate we should not change fonts
                self.font_size_console = t.get("font_size_console")
                self.font_size_textbox = t.get("font_size_textbox")
                self.font_size_listbox = t.get("font_size_listbox")
                self.font_size_button = t.get("font_size_button")
                self.font_size_label = t.get("font_size_label")
                self.font_size_header = t.get("font_size_header")
                # Read window size overrides from theme (optional)
                self.theme_window_width = t.get("window_width")
                self.theme_window_height = t.get("window_height")
            # Apply opacity
            opac = t.get("opacity", 0.9)
            self.root.attributes('-alpha', opac)
            
            # Update UI elements with new colors
            # Only configure widgets that exist
            if hasattr(self, 'right_panel'):
                self.right_panel.config(bg=self.bg_rightpanel)
            if hasattr(self, 'console_text'):
                # Determine size: use theme value, or fallback to 12
                f_size = self.font_size_console if self.font_size_console is not None else 12
                self.console_text.config(
                    font=(self.font, f_size),
                    wrap=tk.WORD,  # clean wrapping for large fonts
                    bg=self.console_bg, 
                    fg=self.console_fg
                    )
                ###
                try:
                    # 1. Force a layout refresh so Tkinter sees the new font sizes
                    self.root.update_idletasks() 
                    
                    # 2. Set your "Zoltun Standard" 710px Snap
                    f_size = self.font_size_console if self.font_size_console is not None else 12
                    # Use theme override if provided, otherwise use default width
                    target_w = self.theme_window_width if self.theme_window_width is not None else 710
                    # Use theme override if provided, otherwise calculate based on font size and prompt visibility
                    if self.theme_window_height is not None:
                        target_h = self.theme_window_height
                    else:
                        # Check if prompt input is visible via toggle_button
                        prompt_visible = hasattr(self, 'toggle_button') and self.toggle_button.winfo_ismapped()
                        target_h = 700 if not prompt_visible else 850
                    
                    # 3. Apply the geometry to force the window back to 710px
                    # This overrides the OS's memory of the wider window
                    self.root.geometry(f"{target_w}x{target_h}")
                    
                    # 4. The "Release": Set a minimum but allow free resizing
                    # We remove the hard maxsize so the user can drag it wider
                    self.root.minsize(710, 500)
                    self.root.maxsize(self.root.winfo_screenwidth(), self.root.winfo_screenheight())
                    self.root.resizable(True, True) 
                    
                    print(f"Theme applied: Snapped to {target_w}x{target_h}")
                ###
                
                except Exception as e:
                    print(f"Error controlling window size: {e}")
                if hasattr(self.console_text, 'config'):
                    try:
                        import tkinter.font as tkfont
                        current_font = tkfont.Font(font=self.console_text.cget("font"))
                        font_size = current_font.actual()["size"]
                        if self.font_size_console is not None:
                            self.console_text.config(font=(self.font, self.font_size_console))
                        else:
                            self.console_text.config(font=(self.font, font_size))
                    except:
                        pass
            if hasattr(self, 'text_box'):
                self.text_box.config(fg=self.prompt_fg, bg=self.prompt_bg)
                try:
                    import tkinter.font as tkfont
                    current_font = tkfont.Font(font=self.text_box.cget("font"))
                    font_size = current_font.actual()["size"]
                    if self.font_size_textbox is not None:
                        self.text_box.config(font=(self.font, self.font_size_textbox))
                    else:
                        self.text_box.config(font=(self.font, font_size))
                except:
                    pass
            if hasattr(self, 'file_listbox'):
                self.file_listbox.config(fg=self.listbox_fg, bg=self.listbox_bg)
                try:
                    import tkinter.font as tkfont
                    current_font = tkfont.Font(font=self.file_listbox.cget("font"))
                    font_size = current_font.actual()["size"]
                    if self.font_size_listbox is not None:
                        self.file_listbox.config(font=(self.font, self.font_size_listbox))
                    else:
                        self.file_listbox.config(font=(self.font, 9))
                except:
                    pass
            if hasattr(self, 'file_seshbox'):
                self.file_seshbox.config(fg=self.listbox_fg, bg=self.listbox_bg)
                try:
                    import tkinter.font as tkfont
                    current_font = tkfont.Font(font=self.file_seshbox.cget("font"))
                    font_size = current_font.actual()["size"]
                    if self.font_size_listbox is not None:
                        self.file_seshbox.config(font=(self.font, self.font_size_listbox))
                    else:
                        self.file_seshbox.config(font=(self.font, 9))
                except:
                    pass
            
            # Update combobox style
            # background is the little arrow unclicked
            #if self.t_type == "matrix":
            if self.t_type == "matrix":
                self.combo_style.configure('TCombobox', foreground ="black", fieldbackground=self.console_bg, background=self.console_bg)
            #print("Foreground 1 ", self.theme_combo.foreground)
            if self.t_type == "inverse":
                self.combo_style.configure('TCombobox', foreground ="", fieldbackground=self.console_bg, background=self.console_fg, selectbackground = self.console_bg)
            # Update buttons
            for widget_name in ['test_button', 'save_button', 'toggle_button', 'refresh_button', 'clear_console_button']:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    widget.config(bg=self.button_bg, fg=self.button_fg)
                    try:
                        import tkinter.font as tkfont
                        current_font = tkfont.Font(font=widget.cget("font"))
                        font_size = current_font.actual()["size"]
                        if self.font_size_button is not None:
                            widget.config(font=(self.font, self.font_size_button))
                        else:
                            widget.config(font=(self.font, 9))
                    except:
                        pass
            # Update checkbutton with additional options
            #self.t_type
            print("theme ", self.whichTheme, "type ", self.t_type, "Button fg ", self.button_fg, "button_bg ", self.button_bg, "active background ", self.console_bg, "active foreground ", self.button_bg) #DIAG
            #this is for togglebox NOT dropdown and can be removed
            if hasattr(self, 'toggle_btn'):
                if self.t_type == "matrix":
                    self.toggle_btn.config(bg=self.button_bg, fg=self.button_fg, selectcolor=self.button_bg, activebackground=self.console_bg, activeforeground=self.button_bg) #different with matrix and inverse
                    try:
                        import tkinter.font as tkfont
                        current_font = tkfont.Font(font=self.toggle_btn.cget("font"))
                        font_size = current_font.actual()["size"]
                        if self.font_size_button is not None:
                            self.toggle_btn.config(font=(self.font, self.font_size_button))
                        else:
                            self.toggle_btn.config(font=(self.font, 9))
                    except:
                        pass
                    print("Matrix Flag")
                #inverse
                if self.t_type == "inverse":
                    self.toggle_btn.config(bg=self.button_bg, fg=self.button_fg, selectcolor=self.button_bg, activebackground=self.button_bg, activeforeground=self.button_bg) #different with matrix and inverse
                    try:
                        import tkinter.font as tkfont
                        current_font = tkfont.Font(font=self.toggle_btn.cget("font"))
                        font_size = current_font.actual()["size"]
                        if self.font_size_button is not None:
                            self.toggle_btn.config(font=(self.font, self.font_size_button))
                        else:
                            self.toggle_btn.config(font=(self.font, 9))
                    except:
                        pass
                    print("Inverse flag")
                    print("IN INVERSE ", "theme ", self.whichTheme, "type ", self.t_type, "Button fg ", self.button_fg, "button_bg ", self.button_bg, "active background ", self.console_bg, "active foreground ", self.button_bg)
            # Update labels
            if hasattr(self, 'tokens_group'):
                self.tokens_group.config(bg=self.bg_rightpanel)
            if hasattr(self, 'tokens_group_l'):
                self.tokens_group_l.config(fg=self.button_fg, bg=self.bg_rightpanel)
                try:
                    import tkinter.font as tkfont
                    current_font = tkfont.Font(font=self.tokens_group_l.cget("font"))
                    font_size = current_font.actual()["size"]
                    if self.font_size_header is not None:
                        self.tokens_group_l.config(font=(self.font, self.font_size_header, "bold"))
                    else:
                        self.tokens_group_l.config(font=(self.font, 9, "bold"))
                except:
                    pass
            #self.model_label.config(fg=self.label_fg, bg=self.bg_rightpanel)
            if hasattr(self, 'total_tokens_label'):
                self.total_tokens_label.config(fg=self.label_fg, bg=self.bg_rightpanel)
                try:
                    import tkinter.font as tkfont
                    current_font = tkfont.Font(font=self.total_tokens_label.cget("font"))
                    font_size = current_font.actual()["size"]
                    if self.font_size_label is not None:
                        self.total_tokens_label.config(font=(self.font, self.font_size_label))
                    else:
                        self.total_tokens_label.config(font=(self.font, 9))
                except:
                    pass
            if hasattr(self, 'input_tokens_label'):
                self.input_tokens_label.config(fg=self.label_fg, bg=self.bg_rightpanel)
                try:
                    import tkinter.font as tkfont
                    current_font = tkfont.Font(font=self.input_tokens_label.cget("font"))
                    font_size = current_font.actual()["size"]
                    if self.font_size_label is not None:
                        self.input_tokens_label.config(font=(self.font, self.font_size_label))
                    else:
                        self.input_tokens_label.config(font=(self.font, 9))
                except:
                    pass
            if hasattr(self, 'output_tokens_label'):
                self.output_tokens_label.config(fg=self.label_fg, bg=self.bg_rightpanel)
                try:
                    import tkinter.font as tkfont
                    current_font = tkfont.Font(font=self.output_tokens_label.cget("font"))
                    font_size = current_font.actual()["size"]
                    if self.font_size_label is not None:
                        self.output_tokens_label.config(font=(self.font, self.font_size_label))
                    else:
                        self.output_tokens_label.config(font=(self.font, 9))
                except:
                    pass
            if hasattr(self, 'file_list_header'):
                self.file_list_header.config(fg=self.button_fg, bg=self.bg_rightpanel)
                try:
                    import tkinter.font as tkfont
                    current_font = tkfont.Font(font=self.file_list_header.cget("font"))
                    font_size = current_font.actual()["size"]
                    if self.font_size_header is not None:
                        self.file_list_header.config(font=(self.font, self.font_size_header, "bold"))
                    else:
                        self.file_list_header.config(font=(self.font, 9, "bold"))
                except:
                    pass
            if hasattr(self, 'session_list_header'):
                self.session_list_header.config(fg=self.button_fg, bg=self.bg_rightpanel)
                try:
                    import tkinter.font as tkfont
                    current_font = tkfont.Font(font=self.session_list_header.cget("font"))
                    font_size = current_font.actual()["size"]
                    if self.font_size_header is not None:
                        self.session_list_header.config(font=(self.font, self.font_size_header, "bold"))
                    else:
                        self.session_list_header.config(font=(self.font, 9, "bold"))
                except:
                    pass
            
            # Update left area and frame
            if hasattr(self, 'left_area'):
                self.left_area.config(bg=self.bg_rightpanel)
            if hasattr(self, 'frame'):
                self.frame.config(bg=self.bg_rightpanel)
            
            # Update SmartChatWidget headings theme
            if hasattr(self, 'console_text') and self.headings_theme:
                self.console_text.update_headings_theme(self.headings_theme, self.listbox_bg, self.listbox_fg, self.console_bg, self.button_bg)
            
            # Auto-expand window if content doesn't fit, or reset to 800x600 if window is too large
# --- FINAL GEOMETRY RESET ---
            try:
                # 1. Force the UI to calculate new font sizes before we snap
                self.root.update_idletasks() 
                
                # 2. Set the Zoltun Snap
                f_size = self.font_size_console if self.font_size_console is not None else 12
                # Use theme override if provided, otherwise use default width
                target_w = self.theme_window_width if self.theme_window_width is not None else 710
                # Use theme override if provided, otherwise calculate based on font size and prompt visibility
                if self.theme_window_height is not None:
                    target_h = self.theme_window_height
                else:
                    # Check if prompt input is visible via toggle_button
                    prompt_visible = hasattr(self, 'toggle_button') and self.toggle_button.winfo_ismapped()
                    target_h = 700 if not prompt_visible else 850

                
                # 3. Apply the 710px geometry string. 
                # This overrides the manual resize and the "req_width" expansion.
                self.root.geometry(f"{target_w}x{target_h}")
                
                # 4. Release for manual resizing
                # We set a minimum to protect the sidebar but allow growth
                self.root.minsize(710, 500)
                self.root.maxsize(self.root.winfo_screenwidth(), self.root.winfo_screenheight())
                self.root.resizable(True, True) 

                # 4. Bring it back - the user only sees the final result
                self.root.deiconify()
                
                print(f"Zoltun Snap: Applied {target_w}x{target_h}")
            except Exception as e:
                print(f"Error resetting window geometry: {e}")            
            print(f"Applied theme from {selected_file}")
            
        except Exception as e:
            print(f"Error loading theme: {e}")

# Create the main root (will be used for both splash and main app)
root = tk.Tk()
root.withdraw()  # Hide immediately to prevent blank popup

# Show splash screen
splash = show_splash_screen(None)

# Schedule the creation of the main app after 3 seconds
def create_main_app():
    """Create the main application after splash screen closes."""
    if splash.winfo_exists():
        splash.destroy()
    # Create the App instance (which will configure the window)
    app = App(root)
    # Show the window
    root.deiconify()
    root.lift()
    root.focus_force()

root.after(3000, create_main_app)

# Start the mainloop
root.mainloop()