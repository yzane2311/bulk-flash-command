import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import json
import sys
import platform
import subprocess
import threading
import queue
import datetime
import re


PYTHON_EXEC = sys.executable
# !!! IMPORTANT: Ensure this path is correct for your system and points to the mtk.py executable
MTKCLIENT_PATH = "/home/ubuntu/mtkclient/mtk.py" # Example for Linux, adjust if necessary

# --- Placeholders & Constants ---
class UltimateDeviceTool:
    def __init__(self): self.labels = {}; self.theme = {}; self.log_panel = None; self.master = None; self._update_cancel_button_state = lambda enable: None; self.after = lambda ms, func: None
class LogPanelPlaceholder:
    def log(self, m, t="info", its=True): print(f"[{t.upper()}] {m}")
    def clear_log(self): print("--- Log Cleared ---")
    def show_progress(self): print("Progress Shown")
    def hide_progress(self): print("Progress Hidden")
    def winfo_exists(self): return True # Simulate window existence

LABEL_FONT = ("Arial", 10, "bold")
FONT = ("Arial", 9)
BTN_FONT = ("Arial", 9, "bold")

class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        # Remove non-standard keys before passing to the original tk.Button
        kwargs.pop("theme", None)
        kwargs.pop("icon_path", None)
        kwargs.pop("icon_size", None)
        super().__init__(master, **kwargs)

# ========== MTKTab Class ==========
class MTKTab(ttk.Frame):
    def __init__(self, parent_notebook, master_app: UltimateDeviceTool):
        super().__init__(parent_notebook)
        self.master_app = master_app
        self.labels = master_app.labels # Get labels from master app
        self.configure(padding=(10,10))

        self.da_file_var = tk.StringVar()
        self.auth_file_var = tk.StringVar()
        self.preloader_file_var = tk.StringVar()
        self.scatter_file_var = tk.StringVar()
        self.partition_checkbox_vars = {} # Dictionary to store partition checkbox variables
        self.mtk_process = None # To store the running mtkclient process
        self.output_queue = queue.Queue() # Queue for process output
        self.process_running = False # Flag to track if a process is running

        self.current_operation_log_buffer = [] # Buffer for log messages of the current operation
        self.detected_device_info = {} # To store detected device information
        self.current_action_name_for_log = "" # Name of the current operation for logging

        # --- Scrollable Frame ---
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas) # Using tk.Frame instead of ttk.Frame if there are style issues
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_width_long = 48
        btn_width_medium = 22
        btn_width_short = 10

        # --- Firmware Flashing Group ---
        group_firmware_flash = tk.LabelFrame(scrollable_frame, text=self.labels.get("group_mtk_firmware_flash", "Firmware Flashing"), font=LABEL_FONT, padx=10, pady=10, relief="groove", bd=2)
        group_firmware_flash.pack(pady=10, padx=5, fill=tk.X)
        
        scatter_frame = tk.Frame(group_firmware_flash) # Using tk.Frame
        scatter_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(scatter_frame, text=self.labels.get("label_scatter_file", "Scatter File:"), font=FONT).pack(side=tk.LEFT, padx=(0,5))
        tk.Entry(scatter_frame, textvariable=self.scatter_file_var, font=FONT, width=55, state="readonly").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ModernButton(scatter_frame, text=self.labels.get("btn_browse", "Browse..."), font=BTN_FONT, command=self._browse_scatter_file, width=btn_width_short, padx=4, pady=1).pack(side=tk.LEFT, padx=(5,0))

        partitions_ctrl_frame = tk.Frame(group_firmware_flash) # Using tk.Frame
        partitions_ctrl_frame.pack(fill=tk.X, pady=(5,2))
        tk.Label(partitions_ctrl_frame, text=self.labels.get("label_partitions_to_flash", "Partitions:"), font=FONT).pack(side=tk.LEFT, anchor=tk.W)
        ModernButton(partitions_ctrl_frame, text=self.labels.get("btn_select_all", "All"), font=BTN_FONT, command=self._select_all_partitions, width=btn_width_short-2, padx=4, pady=1).pack(side=tk.LEFT, padx=(10,2))
        ModernButton(partitions_ctrl_frame, text=self.labels.get("btn_deselect_all", "None"), font=BTN_FONT, command=self._deselect_all_partitions, width=btn_width_short-2, padx=4, pady=1).pack(side=tk.LEFT, padx=(2,0))

        partitions_outer_f = tk.Frame(group_firmware_flash, bd=1, relief="sunken") # Using tk.Frame
        partitions_outer_f.pack(fill=tk.BOTH, expand=True, pady=(0,5))
        partitions_canvas = tk.Canvas(partitions_outer_f, borderwidth=0, height=120)
        self.partitions_list_frame = tk.Frame(partitions_canvas) # Using tk.Frame to display partition list
        pscroll_y = ttk.Scrollbar(partitions_outer_f, orient="vertical", command=partitions_canvas.yview)
        pscroll_x = ttk.Scrollbar(partitions_outer_f, orient="horizontal", command=partitions_canvas.xview)
        partitions_canvas.configure(yscrollcommand=pscroll_y.set, xscrollcommand=pscroll_x.set)
        pscroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        pscroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        partitions_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        partitions_canvas.create_window((0,0), window=self.partitions_list_frame, anchor="nw")
        self.partitions_list_frame.bind("<Configure>", lambda e: partitions_canvas.configure(scrollregion=partitions_canvas.bbox("all")))
        ModernButton(group_firmware_flash, text=self.labels.get("btn_mtk_flash_scatter", "Flash Selected Partitions"), font=BTN_FONT, command=self.action_mtk_flash_scatter_firmware, width=btn_width_long).pack(pady=(8,0), anchor=tk.CENTER)

        # --- Global Options Group ---
        group_files = tk.LabelFrame(scrollable_frame, text=self.labels.get("group_mtk_files", "Global Options"), font=LABEL_FONT, padx=10, pady=10, relief="groove", bd=2)
        group_files.pack(pady=5, padx=5, fill=tk.X)
        self._create_file_selector(group_files, self.labels.get("label_da_file", "DA File:"), self.da_file_var, width=55, btn_width=btn_width_short)
        self._create_file_selector(group_files, self.labels.get("label_auth_file", "Auth File:"), self.auth_file_var, width=55, btn_width=btn_width_short)
        self._create_file_selector(group_files, self.labels.get("label_preloader_file", "Preloader File:"), self.preloader_file_var, width=55, btn_width=btn_width_short)

        # --- Operations Columns ---
        ops_main_f = tk.Frame(scrollable_frame) # Using tk.Frame
        ops_main_f.pack(fill=tk.X, pady=5, padx=5)
        ops_col1 = tk.Frame(ops_main_f) # Using tk.Frame
        ops_col1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ops_col2 = tk.Frame(ops_main_f) # Using tk.Frame
        ops_col2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
        op_btn_cfg = {"width": btn_width_medium, "pady": 2, "font": BTN_FONT, "anchor": tk.W}

        # --- Column 1 Actions ---
        action_groups_col1 = [
            (self.labels.get("group_mtk_dump", "Dump Operations"), [
                ("btn_mtk_read_full_dump", "Read Full Dump", self.action_mtk_read_full_dump),
                ("btn_mtk_read_userdata", "Read Userdata", self.action_mtk_read_userdata),
                ("btn_mtk_read_custom_dump", "Read Custom Partition", self.action_mtk_read_custom_dump),
                ("btn_mtk_auto_boot_repair_dump", "Dump Boot Repair Files", self.action_mtk_auto_boot_repair_dump),
                ("btn_mtk_write_dump", "Write Partition", self.action_mtk_write_dump),
            ]),
            (self.labels.get("group_mtk_partitions", "Partition Operations"), [
                ("btn_mtk_list_partitions", "List Partitions (GPT)", self.action_mtk_list_partitions),
                ("btn_mtk_backup_selected_partitions", "Backup Selected Partitions", self.action_mtk_backup_selected_partitions),
                ("btn_mtk_backup_security_partitions", "Backup Security Partitions", self.action_mtk_backup_security_partitions),
                ("btn_mtk_format_selected_partitions", "Format Selected Partitions", self.action_mtk_format_selected_partitions),
                ("btn_mtk_restore_selected_partitions", "Restore Selected Partitions", self.action_mtk_restore_selected_partitions),
                ("btn_mtk_reset_nv_data", "Reset NV Partitions", self.action_mtk_reset_nv_data),
            ])
        ]

        # --- Column 2 Actions ---
        action_groups_col2 = [
            (self.labels.get("group_mtk_frp_data", "FRP & Data Operations"), [
                ("btn_mtk_erase_frp", "Erase FRP", self.action_mtk_erase_frp),
                ("btn_mtk_samsung_frp", "Samsung FRP (MTK)", self.action_mtk_samsung_frp),
                ("btn_mtk_safe_format", "Safe Format Data", self.action_mtk_safe_format),
                ("btn_mtk_erase_frp_write_file", "Erase FRP (Write File)", self.action_mtk_erase_frp_write_file),
                ("btn_mtk_wipe_data", "Wipe Data", self.action_mtk_wipe_data),
            ]),
            (self.labels.get("group_mtk_bootloader", "Bootloader Operations"), [
                ("btn_mtk_unlock_bootloader", "Unlock Bootloader", self.action_mtk_unlock_bootloader),
                ("btn_mtk_lock_bootloader", "Lock Bootloader", self.action_mtk_lock_bootloader),
            ]),
            (self.labels.get("group_mtk_keys_forensics", "Keys & Forensics"), [
                ("btn_mtk_extract_keys", "Attempt Key Partition Dump", self.action_mtk_extract_keys),
                ("btn_mtk_generate_ewc", "Guide: Generate EWC (Oxygen)", self.action_mtk_generate_ewc),
                ("btn_mtk_build_forensic_project", "Guide: Full Forensic Project", self.action_mtk_build_forensic_project),
            ]),
            (self.labels.get("group_mtk_hw_utils", "Hardware Utilities"), [
                ("btn_mtk_dump_hw_keys_brom", "Dump HW Keys [BROM]", self.action_mtk_dump_hw_keys_brom),
                ("btn_mtk_dump_hw_keys_preloader", "Dump HW Keys [PRELOADER]", self.action_mtk_dump_hw_keys_preloader),
            ])
        ]

        # --- Create Buttons for Columns ---
        for col_frame, groups in [(ops_col1, action_groups_col1), (ops_col2, action_groups_col2)]:
            for group_label_key, actions in groups:
                group = tk.LabelFrame(col_frame, text=group_label_key, font=LABEL_FONT, padx=10, pady=5, relief="groove", bd=2)
                group.pack(pady=5, fill=tk.X, expand=True)
                for btn_label_key, btn_text_default, command in actions:
                    ModernButton(group, text=self.labels.get(btn_label_key, btn_text_default), command=command, **op_btn_cfg).pack(fill=tk.X)

        self._poll_output_queue() # Start polling the output queue

    # --- File Browsing & Parsing ---
    def _create_file_selector(self, parent, lbl_txt, var, f_types_key="default", width=40, btn_width=10):
        f = tk.Frame(parent) # Using tk.Frame
        f.pack(fill=tk.X, pady=1)
        tk.Label(f, text=lbl_txt, font=FONT).pack(side=tk.LEFT, padx=(0,5))
        tk.Entry(f, textvariable=var, font=FONT, width=width, state="readonly").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ModernButton(f, text=self.labels.get("btn_browse", "..."), font=BTN_FONT, command=lambda v=var, k=f_types_key: self._browse_file(v,k), width=btn_width, padx=4,pady=1).pack(side=tk.LEFT,padx=(5,0))

    def _browse_file(self, var_to_set, file_types_key="default"):
        f_map = {
            "default": [("Bin/Img Files", "*.bin *.img"), ("All Files", "*.*")],
            "scatter": [("Scatter Files", "*.txt"), ("All Files", "*.*")]
        }
        # Ensure master_app.master exists before using it as parent
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        fpath = filedialog.askopenfilename(parent=parent_window, title=self.labels.get("select_file_title", "Select File"), filetypes=f_map.get(file_types_key, f_map["default"]))
        if fpath: 
            var_to_set.set(fpath)
            self._log_gui_event(f"File Selected: {os.path.basename(fpath)}")
        return fpath

    def _browse_scatter_file(self):
        fpath = self._browse_file(self.scatter_file_var, "scatter")
        if fpath: 
            self._update_partition_list(fpath)
        else: 
            self._clear_partition_list()

    def _parse_scatter_file(self, fpath):
        parts = []
        unique_parts = set()
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
            # Improved regex to handle variations and comments
            matches = re.findall(r"^\s*partition_name:\s*(\w+)(?:.|\n)*?^\s*is_download:\s*true", content, re.IGNORECASE | re.MULTILINE)
            for name in matches:
                if name not in unique_parts:
                    parts.append(name)
                    unique_parts.add(name)
        except Exception as e: 
            self._log_gui_event(f"Error parsing Scatter file: {e}", "error")
        if not parts: 
            self._log_gui_event(f"No downloadable partitions found in {os.path.basename(fpath)}", "warning")
        else: 
            self._log_gui_event(f"Partitions from {os.path.basename(fpath)}: {len(parts)} found", "info")
        return parts

    def _update_partition_list(self, scatter_fpath):
        self._clear_partition_list()
        part_names = self._parse_scatter_file(scatter_fpath)
        if not part_names: 
            tk.Label(self.partitions_list_frame, text=self.labels.get("no_partitions_found", "No downloadable partitions found."), font=FONT).pack()
        else:
            for name in part_names:
                var = tk.BooleanVar(value=True)
                self.partition_checkbox_vars[name] = var
                tk.Checkbutton(self.partitions_list_frame, text=name, variable=var, font=FONT, anchor="w").pack(fill=tk.X)

    def _clear_partition_list(self):
        for w in self.partitions_list_frame.winfo_children(): w.destroy()
        self.partition_checkbox_vars.clear()

    def _select_all_partitions(self, select=True):
        for var in self.partition_checkbox_vars.values(): var.set(select)
        self._log_gui_event(f"Partitions: {'All selected' if select else 'None selected'}")

    def _deselect_all_partitions(self): 
        self._select_all_partitions(select=False)

    # --- Logging & Process Handling ---
    def _log_gui_event(self, message, tag="info"):
        if self.master_app.log_panel and hasattr(self.master_app.log_panel, 'log'):
            self.master_app.log_panel.log(message, tag)

    def _log_operation_summary(self, message, tag="operation_status"):
        if self.master_app.log_panel and hasattr(self.master_app.log_panel, 'log'):
            self.master_app.log_panel.log(message, tag)

    def _parse_mtk_output_for_device_info(self, line):
        patterns = {
            "chipset": r"HW Chipset:\s*(\S+)|Chipset:\s*(\S+)", "hw_ver": r"HW Version:\s*(\S+)",
            "sw_ver": r"SW Version:\s*(\S+)", "board": r"Board:\s*(\S+)",
            "manufacturer": r"Manufacturer:\s*(\S+)", "model": r"Model:\s*(\S+)",
            "brand": r"Brand:\s*(\S+)", "android": r"Android version:\s*(\S+)", "meid": r"MEID:\s*(\S+)",
            "socid": r"SOC ID:\s*([0-9a-fA-F]+)"
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                value = next((g for g in match.groups() if g is not None), None)
                if value and key not in self.detected_device_info:
                    self.detected_device_info[key] = value
                    return True
        return False

    def _enqueue_output(self, pipe, _tag_unused):
        try:
            with pipe:
                for line_bytes in iter(pipe.readline, b''):
                    line = line_bytes.decode("utf-8", errors="ignore").strip()
                    self.output_queue.put(line)
                    self._parse_mtk_output_for_device_info(line)
        except Exception as e: 
            self.output_queue.put(f"[[ERROR READING PIPE: {e}]]")
        finally: 
            self.output_queue.put(None) # Signal end of stream

    def _poll_output_queue(self):
        stream_closed_count = 0
        try:
            while True: # Drain the queue
                line = self.output_queue.get_nowait()
                if line is None: # End of stream signal received
                    stream_closed_count +=1
                    continue
                self.current_operation_log_buffer.append(line)
        except queue.Empty: 
            pass # Queue is empty, no problem

        if self.process_running and self.mtk_process:
            # Condition changed to stream_closed_count >= 1 because stderr is merged into stdout
            if stream_closed_count >= 1 or self.mtk_process.poll() is not None: 
                 rc = self.mtk_process.wait() # Wait for process to finish to get exit code
                 self._finalize_operation_log(self.current_action_name_for_log, rc)
                 self._operation_cleanup()

        # Ensure master_app.master and master_app.after exist before calling
        if hasattr(self.master_app, 'master') and self.master_app.master and \
           hasattr(self.master_app, 'after') and callable(self.master_app.after) and \
           self.winfo_exists(): # Ensure widget still exists
             try:
                 self.master_app.after(100, self._poll_output_queue)
             except tk.TclError: 
                 pass # Avoid error if window is destroyed

    def _finalize_operation_log(self, action_name, return_code):
        self._log_operation_summary(f"Operation: {action_name}", "operation_status")
        if self.detected_device_info:
            info_str = ", ".join([f"{k.replace('_',' ').title()}: {v}" for k,v in self.detected_device_info.items()])
            self._log_operation_summary(f"Device Info: {info_str}", "device_info")
        else: 
            self._log_operation_summary("Device Info: Not detected or N/A.", "device_info")

        if self.current_operation_log_buffer:
            self._log_operation_summary("--- Raw Output Start ---", "raw_output")
            for line in self.current_operation_log_buffer:
                self._log_operation_summary(line, "raw_output")
            self._log_operation_summary("--- Raw Output End ---", "raw_output")

        if return_code == 0: 
            self._log_operation_summary("Status: Success", "success")
        else:
            self._log_operation_summary(f"Status: Failed (Exit Code: {return_code})", "error")
            error_keywords = ["error", "fail", "traceback", "except", "critical", "could not", "can't open", "not found", "no such file", "nomodulefound"]
            critical_errors_logged = 0
            for line in self.current_operation_log_buffer:
                if any(keyword in line.lower() for keyword in error_keywords):
                    self._log_operation_summary(f"  Potential Error Detail: {line}", "error")
                    critical_errors_logged += 1
                    if critical_errors_logged >= 5: break # Limit number of logged error details

    def _operation_cleanup(self):
        self.process_running = False
        self.mtk_process = None
        self.current_operation_log_buffer = []
        self.detected_device_info = {}
        if self.master_app.log_panel: self.master_app.log_panel.hide_progress()
        if hasattr(self.master_app, '_update_cancel_button_state'): self.master_app._update_cancel_button_state(enable=False)
        # Clear any remaining items in the queue
        while not self.output_queue.empty():
            try: self.output_queue.get_nowait()
            except queue.Empty: break

    def _run_mtk_command(self, command_args_list, action_name, is_forensic_key_dump=False, forensic_partitions=None):
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        if self.process_running:
            messagebox.showwarning(self.labels.get("mtk_op_in_progress_title", "Operation in Progress"), 
                                   self.labels.get("mtk_op_in_progress_msg", "Another MTK operation is already running."), 
                                   parent=parent_window)
            return False

        confirm_key = "mtk_confirm_action_msg_flash" if "flash" in action_name.lower() else "mtk_confirm_action_msg"
        confirm_msg_template = self.labels.get(confirm_key, "Are you sure you want to perform: {action_name}?")
        confirm_msg = confirm_msg_template.format(action_name=action_name)
        
        if "dump hw keys" in action_name.lower() or "dumpbrom" in action_name.lower() or "dumppreloader" in action_name.lower():
            confirm_msg += "\n\n" + self.labels.get("mtk_warning_hw_dump", "WARNING: This is an advanced operation. It might read sensitive data or fail depending on device security. Proceed with caution.")
        elif "format" in action_name.lower() or "erase" in action_name.lower() or "wipe" in action_name.lower():
             confirm_msg += "\n\n" + self.labels.get("mtk_warning_erase", "WARNING: This will erase data and cannot be undone!")

        if not messagebox.askokcancel(self.labels.get("mtk_confirm_action_title", "Confirm Action"), confirm_msg, icon=messagebox.WARNING, parent=parent_window):
            self._log_gui_event(f"Action '{action_name}' cancelled by user.", "info")
            return False

        if self.master_app.log_panel: self.master_app.log_panel.clear_log()
        self.current_action_name_for_log = action_name
        self.current_operation_log_buffer = []
        self.detected_device_info = {}
        self._log_operation_summary(f"Starting: {action_name}", "operation_status")
        self._log_operation_summary("Waiting for MTK Port (Connect device in BROM/Preloader mode)...", "info")

        base_cmd = [PYTHON_EXEC, MTKCLIENT_PATH]

        if is_forensic_key_dump and forensic_partitions:
            output_dir = filedialog.askdirectory(title=self.labels.get("select_key_dump_folder_title", "Select Folder to Save Key Partitions"), parent=parent_window)
            if not output_dir: 
                self._log_gui_event("Key partition dump cancelled: No output folder.", "info")
                return False
            self._log_gui_event(f"Dumping key partitions to: {output_dir}", "info")
            success_all = True
            # Note: These operations are synchronous (block UI)
            for part_name in forensic_partitions:
                self._log_gui_event(f"  Dumping: {part_name}", "info")
                part_cmd_args_specific = ["r", part_name, os.path.join(output_dir, f"{part_name}.bin")]
                current_full_cmd = list(base_cmd) + part_cmd_args_specific
                if self.da_file_var.get(): current_full_cmd.extend(["--loader", self.da_file_var.get()])
                if self.auth_file_var.get(): current_full_cmd.extend(["--auth", self.auth_file_var.get()])
                if self.preloader_file_var.get(): current_full_cmd.extend(["--preloader", self.preloader_file_var.get()])
                try:
                    flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                    process = subprocess.run(current_full_cmd, capture_output=True, text=True, check=False, creationflags=flags, encoding='utf-8', errors='ignore')
                    if process.stdout: self._log_gui_event(f"    [{part_name} STDOUT] {process.stdout.strip()}", "info")
                    if process.stderr: self._log_gui_event(f"    [{part_name} STDERR] {process.stderr.strip()}", "warning")
                    if process.returncode == 0: self._log_gui_event(f"  Successfully dumped {part_name}.", "success")
                    else: 
                        self._log_gui_event(f"  Failed to dump {part_name} (Code: {process.returncode}).", "error")
                        success_all = False
                except Exception as e: 
                    self._log_gui_event(f"  Exception dumping {part_name}: {e}", "error")
                    success_all = False
            self._log_gui_event("Key partition dump sequence finished.", "success" if success_all else "warning")
            return success_all

        full_cmd = list(base_cmd) + command_args_list
        if self.da_file_var.get(): full_cmd.extend(["--loader", self.da_file_var.get()])
        if self.auth_file_var.get(): full_cmd.extend(["--auth", self.auth_file_var.get()])
        if self.preloader_file_var.get() and command_args_list[0] not in ['dumpbrom', 'dumppreloader']: # Preloader not typically used with dumpbrom/dumppreloader
             full_cmd.extend(["--preloader", self.preloader_file_var.get()])

        self._log_gui_event(f"Executing command: {' '.join(full_cmd)}", "debug")

        try:
            flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            self.mtk_process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=False, creationflags=flags)
            self.process_running = True
            threading.Thread(target=self._enqueue_output, args=(self.mtk_process.stdout, "merged_output"), daemon=True).start()
            if self.master_app.log_panel: self.master_app.log_panel.show_progress()
            if hasattr(self.master_app, '_update_cancel_button_state'): self.master_app._update_cancel_button_state(enable=True)
            return True
        except FileNotFoundError:
            err_msg = f"Error: Python executable '{PYTHON_EXEC}' or mtkclient script '{MTKCLIENT_PATH}' not found. Ensure paths are correct."
            self._finalize_operation_log(action_name, -1) # Use custom error code
            if self.master_app.log_panel: self.master_app.log_panel.log(err_msg, "error")
            messagebox.showerror("File Not Found", err_msg, parent=parent_window)
        except Exception as e:
            err_msg = f"Failed to start MTK operation: {e}"
            self._finalize_operation_log(action_name, -2) # Use custom error code
            if self.master_app.log_panel: self.master_app.log_panel.log(err_msg, "error")
            messagebox.showerror("Operation Error", err_msg, parent=parent_window)
        self._operation_cleanup()
        return False

    # --- MTK Action Methods ---
    def action_mtk_flash_scatter_firmware(self):
        action_name = self.labels.get("btn_mtk_flash_scatter", "Flash Firmware (Scatter)")
        scatter_path = self.scatter_file_var.get()
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self

        if not scatter_path:
            self._log_gui_event("No scatter file selected.", "error")
            messagebox.showerror("Error", "No scatter file selected.", parent=parent_window)
            return
        if not os.path.exists(scatter_path):
            self._log_gui_event(f"Scatter file not found: {scatter_path}", "error")
            messagebox.showerror("Error", f"Scatter file not found: {scatter_path}", parent=parent_window)
            return

        selected_partitions = [name for name, var in self.partition_checkbox_vars.items() if var.get()]
        if not selected_partitions:
            self._log_gui_event("No partitions selected to flash.", "warning")
            messagebox.showwarning("Warning", "No partitions selected to flash.", parent=parent_window)
            return

        # Confirm before starting the potentially long, UI-blocking flash operation
        confirm_msg = self.labels.get("mtk_confirm_action_msg_flash_selected", "Are you sure you want to flash the selected {count} partition(s)?\nThis operation will block the UI until completed.").format(count=len(selected_partitions))
        confirm_msg += "\n\n" + self.labels.get("mtk_warning_erase", "WARNING: This will write data to the device and may erase existing data!")
        if not messagebox.askokcancel(self.labels.get("mtk_confirm_action_title", "Confirm Action"), confirm_msg, icon=messagebox.WARNING, parent=parent_window):
            self._log_gui_event(f"Action '{action_name}' cancelled by user.", "info")
            return

        if self.master_app.log_panel: self.master_app.log_panel.clear_log()
        self.current_action_name_for_log = action_name # Set operation name for logging
        self._log_operation_summary(f"Starting: {action_name} for partitions: {', '.join(selected_partitions)}", "operation_status")
        self._log_operation_summary("Note: This operation will block the UI until all selected partitions are flashed.", "info")
        if self.master_app.log_panel: self.master_app.log_panel.show_progress()


        scatter_dir = os.path.dirname(scatter_path)
        base_cmd_prefix = [PYTHON_EXEC, MTKCLIENT_PATH]
        common_opts = []
        if self.da_file_var.get(): common_opts.extend(["--loader", self.da_file_var.get()])
        if self.auth_file_var.get(): common_opts.extend(["--auth", self.auth_file_var.get()])
        # Do not add --preloader here generally for 'w' command, mtkclient will handle if needed

        success_all = True
        any_errors = False

        # Order flashing preloader first if selected
        if "preloader" in selected_partitions:
            partitions_to_flash_ordered = ["preloader"] + [p for p in selected_partitions if p != "preloader"]
        else:
            partitions_to_flash_ordered = selected_partitions

        for part_name in partitions_to_flash_ordered:
            self._log_gui_event(f"  Attempting to flash partition: {part_name}", "info")
            
            # Find partition image file (with common extensions)
            image_file_path = None
            possible_extensions = [".img", ".bin", ""] # Empty extension for files without extension
            for ext in possible_extensions:
                temp_path = os.path.join(scatter_dir, f"{part_name}{ext}")
                if os.path.exists(temp_path):
                    image_file_path = temp_path
                    break
            
            if not image_file_path:
                self._log_gui_event(f"    Image file for partition '{part_name}' not found in Scatter directory. Skipped.", "warning")
                success_all = False # Consider it a partial failure
                any_errors = True
                continue

            cmd_args_specific = ["w", part_name, image_file_path]
            current_full_cmd = base_cmd_prefix + cmd_args_specific + common_opts
            self._log_gui_event(f"    Executing: {' '.join(current_full_cmd)}", "debug")

            try:
                flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                # Synchronous operation (blocks UI)
                process = subprocess.run(current_full_cmd, capture_output=True, text=True, check=False, creationflags=flags, encoding='utf-8', errors='ignore')
                
                # Log process output directly
                if process.stdout:
                    for line in process.stdout.strip().split('\n'):
                        self._log_operation_summary(f"    [{part_name} STDOUT] {line}", "raw_output")
                if process.stderr:
                    for line in process.stderr.strip().split('\n'):
                         self._log_operation_summary(f"    [{part_name} STDERR] {line}", "raw_output") # Could be actual errors

                if process.returncode == 0:
                    self._log_operation_summary(f"  Successfully flashed {part_name}.", "success")
                else:
                    self._log_operation_summary(f"  Failed to flash {part_name} (Code: {process.returncode}).", "error")
                    success_all = False
                    any_errors = True
            except FileNotFoundError:
                self._log_operation_summary(f"  Error: '{PYTHON_EXEC}' or '{MTKCLIENT_PATH}' not found.", "error")
                success_all = False; any_errors = True; break # Stop operation if essential files not found
            except Exception as e:
                self._log_operation_summary(f"  Exception while flashing {part_name}: {e}", "error")
                success_all = False
                any_errors = True
        
        final_status_msg = "Flashing sequence completed."
        final_status_tag = "success"
        if not success_all:
            final_status_msg += " (with some errors)"
            final_status_tag = "warning"
        if any_errors and not success_all: # If there was a complete failure
             final_status_tag = "error"


        self._log_operation_summary(final_status_msg, final_status_tag)
        if self.master_app.log_panel: self.master_app.log_panel.hide_progress()
        # No _operation_cleanup here as it's not an asynchronous _run_mtk_command operation
        # self.process_running should be reset if set elsewhere for this operation
        # But since we're not using _run_mtk_command, no need to worry about self.process_running

    def action_mtk_read_full_dump(self):
        action_name = self.labels.get("btn_mtk_read_full_dump", "Read Full Dump")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        output_file = filedialog.asksaveasfilename(title="Save Full Dump As...", defaultextension=".bin", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")], parent=parent_window)
        if not output_file: 
            self._log_gui_event("Read Full Dump cancelled.", "info")
            return
        cmd_args = ["rf", output_file]
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_read_userdata(self):
        action_name = self.labels.get("btn_mtk_read_userdata", "Read Userdata")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        output_file = filedialog.asksaveasfilename(title="Save Userdata As...", defaultextension=".bin", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")], parent=parent_window)
        if not output_file: 
            self._log_gui_event("Read Userdata cancelled.", "info")
            return
        cmd_args = ["r", "userdata", output_file]
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_read_custom_dump(self):
        action_name = self.labels.get("btn_mtk_read_custom_dump", "Read Custom Partition")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        partition_name = simpledialog.askstring("Input", "Enter partition name to read:", parent=parent_window)
        if not partition_name: 
            self._log_gui_event("Read Custom Dump cancelled.", "info")
            return
        output_file = filedialog.asksaveasfilename(title=f"Save {partition_name} As...", defaultextension=".bin", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")], parent=parent_window)
        if not output_file: 
            self._log_gui_event("Read Custom Dump cancelled.", "info")
            return
        cmd_args = ["r", partition_name, output_file]
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_auto_boot_repair_dump(self):
        action_name = self.labels.get("btn_mtk_auto_boot_repair_dump", "Dump Boot Repair Files")
        boot_partitions = ["preloader", "lk", "lk2", "boot", "recovery", "tee1", "tee2", "scp1", "scp2", "sspm_1", "sspm_2", "md1img", "md3img", "spmfw", "mcupmfw", "gz1", "gz2"]
        self._log_gui_event(f"Attempting to dump common boot-related partitions: {', '.join(boot_partitions)}", "info")
        # Note: This operation is synchronous (blocks UI) due to is_forensic_key_dump
        self._run_mtk_command([], action_name, is_forensic_key_dump=True, forensic_partitions=boot_partitions)

    def action_mtk_write_dump(self):
        action_name = self.labels.get("btn_mtk_write_dump", "Write Partition")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        partition_name = simpledialog.askstring("Input", "Enter partition name to write:", parent=parent_window)
        if not partition_name: 
            self._log_gui_event("Write Partition cancelled.", "info")
            return
        input_file = filedialog.askopenfilename(title=f"Select file for {partition_name}", filetypes=[("Binary files", "*.bin *.img"), ("All files", "*.*")], parent=parent_window)
        if not input_file: 
            self._log_gui_event("Write Partition cancelled.", "info")
            return
        cmd_args = ["w", partition_name, input_file]
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_list_partitions(self):
        action_name = self.labels.get("btn_mtk_list_partitions", "List Partitions (GPT)")
        cmd_args = ["printgpt"]
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_backup_selected_partitions(self):
        action_name = self.labels.get("btn_mtk_backup_selected_partitions", "Backup Selected Partitions")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        selected_partitions = [name for name, var in self.partition_checkbox_vars.items() if var.get()]
        if not selected_partitions:
            self._log_gui_event("No partitions selected for backup.", "warning")
            messagebox.showwarning("Warning", "No partitions selected for backup.", parent=parent_window)
            return
        self._log_gui_event(f"Attempting to backup selected partitions: {', '.join(selected_partitions)}", "info")
        # Note: This operation is synchronous (blocks UI) due to is_forensic_key_dump
        self._run_mtk_command([], action_name, is_forensic_key_dump=True, forensic_partitions=selected_partitions)

    def action_mtk_backup_security_partitions(self):
        action_name = self.labels.get("btn_mtk_backup_security_partitions", "Backup Security Partitions")
        security_partitions = ["proinfo", "nvram", "nvdata", "protect1", "protect2", "seccfg", "otp", "persist", "frp", "efuse"]
        self._log_gui_event(f"Attempting to backup common security partitions: {', '.join(security_partitions)}", "info")
        # Note: This operation is synchronous (blocks UI) due to is_forensic_key_dump
        self._run_mtk_command([], action_name, is_forensic_key_dump=True, forensic_partitions=security_partitions)

    def _perform_sync_partition_operations(self, action_name_key, action_verb_log, command_prefix_list, partitions_list, extra_confirm_msg_key=None):
        """ Helper function to perform synchronous operations on multiple partitions (e.g., format, restore, erase) """
        action_name = self.labels.get(action_name_key, action_verb_log) # Default to action_verb_log if key not found
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self

        if not partitions_list:
            self._log_gui_event(f"No partitions to perform '{action_name}'.", "warning")
            messagebox.showwarning("Warning", f"No partitions to perform '{action_name}'.", parent=parent_window)
            return

        confirm_msg = self.labels.get("mtk_confirm_action_msg_generic_multi", "Are you sure you want to {action} the following {count} partition(s):\n{partitions_str}?").format(
            action=action_verb_log.lower(), 
            count=len(partitions_list), 
            partitions_str=", ".join(partitions_list)
        )
        if extra_confirm_msg_key:
             confirm_msg += "\n\n" + self.labels.get(extra_confirm_msg_key, "") # Append extra warning if key exists
        
        if not messagebox.askokcancel(self.labels.get("mtk_confirm_action_title", "Confirm Action"), confirm_msg, icon=messagebox.WARNING, parent=parent_window):
            self._log_gui_event(f"Action '{action_name}' cancelled by user.", "info")
            return

        if self.master_app.log_panel: self.master_app.log_panel.clear_log()
        self._log_operation_summary(f"Starting: {action_name} on {', '.join(partitions_list)}", "operation_status")
        self._log_operation_summary("Note: This operation will block the UI until completed.", "info")
        if self.master_app.log_panel: self.master_app.log_panel.show_progress()

        base_cmd_prefix_exec = [PYTHON_EXEC, MTKCLIENT_PATH]
        common_opts = []
        if self.da_file_var.get(): common_opts.extend(["--loader", self.da_file_var.get()])
        if self.auth_file_var.get(): common_opts.extend(["--auth", self.auth_file_var.get()])
        if self.preloader_file_var.get(): common_opts.extend(["--preloader", self.preloader_file_var.get()])
        
        success_all = True
        any_errors = False

        for part_name in partitions_list:
            self._log_gui_event(f"  {action_verb_log} partition: {part_name}", "info")
            
            # Build command arguments specific to the partition
            current_cmd_args = list(command_prefix_list) # Copy the list
            if "{partition_name}" in current_cmd_args: # Replace placeholder if exists
                current_cmd_args = [arg.replace("{partition_name}", part_name) for arg in current_cmd_args]
            else: # Otherwise, assume partition name is the next argument
                current_cmd_args.append(part_name)

            # If operation is write (restore), we need the file path
            if action_verb_log == "Restore": # Or any other indicator for write operation
                input_dir = getattr(self, "_current_input_dir_for_restore", None) # Must be set before calling function
                if not input_dir:
                    self._log_operation_summary(f"  Error: Input directory for restore not set. Skipped.", "error")
                    success_all = False; any_errors = True; continue
                
                backup_file = os.path.join(input_dir, f"{part_name}.bin")
                if not os.path.exists(backup_file):
                    backup_file = os.path.join(input_dir, f"{part_name}.img") # Try .img
                    if not os.path.exists(backup_file):
                        self._log_operation_summary(f"  Skipping {part_name}: Backup file (.bin or .img) not found in {input_dir}.", "warning")
                        any_errors = True; continue # Not necessarily a complete failure
                
                # Add file path to command arguments (usually after partition name)
                # Assumes command_prefix_list is something like ['w']
                current_cmd_args.append(backup_file)
                self._log_gui_event(f"    Restoring from: {os.path.basename(backup_file)}", "info")


            full_cmd = base_cmd_prefix_exec + current_cmd_args + common_opts
            self._log_gui_event(f"    Executing: {' '.join(full_cmd)}", "debug")

            try:
                flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                process = subprocess.run(full_cmd, capture_output=True, text=True, check=False, creationflags=flags, encoding='utf-8', errors='ignore')
                if process.stdout:
                    for line in process.stdout.strip().split('\n'): self._log_operation_summary(f"    [{part_name} STDOUT] {line}", "raw_output")
                if process.stderr:
                    for line in process.stderr.strip().split('\n'): self._log_operation_summary(f"    [{part_name} STDERR] {line}", "raw_output")
                
                if process.returncode == 0:
                    self._log_operation_summary(f"  Successfully {action_verb_log.lower()}ed {part_name}.", "success")
                else:
                    self._log_operation_summary(f"  Failed to {action_verb_log.lower()} {part_name} (Code: {process.returncode}).", "error")
                    success_all = False; any_errors = True
            except FileNotFoundError:
                self._log_operation_summary(f"  Error: '{PYTHON_EXEC}' or '{MTKCLIENT_PATH}' not found.", "error")
                success_all = False; any_errors = True; break 
            except Exception as e:
                self._log_operation_summary(f"  Exception while {action_verb_log.lower()}ing {part_name}: {e}", "error")
                success_all = False; any_errors = True
        
        final_status_msg = f"{action_verb_log} sequence completed."
        final_status_tag = "success"
        if not success_all: final_status_msg += " (with some errors)"; final_status_tag = "warning"
        if any_errors and not success_all : final_status_tag = "error"

        self._log_operation_summary(final_status_msg, final_status_tag)
        if self.master_app.log_panel: self.master_app.log_panel.hide_progress()


    def action_mtk_format_selected_partitions(self):
        selected_partitions = [name for name, var in self.partition_checkbox_vars.items() if var.get()]
        self._perform_sync_partition_operations(
            action_name_key="btn_mtk_format_selected_partitions",
            action_verb_log="Format",
            command_prefix_list=["e"], # mtkclient command for format is 'e'
            partitions_list=selected_partitions,
            extra_confirm_msg_key="mtk_warning_erase"
        )

    def action_mtk_restore_selected_partitions(self):
        selected_partitions = [name for name, var in self.partition_checkbox_vars.items() if var.get()]
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        if not selected_partitions:
             self._log_gui_event("No partitions selected for restore.", "warning")
             messagebox.showwarning("Warning", "No partitions selected for restore.", parent=parent_window)
             return

        input_dir = filedialog.askdirectory(title="Select Folder Containing Partition Backups", parent=parent_window)
        if not input_dir:
            self._log_gui_event("Restore cancelled: No input folder selected.", "info")
            return
        
        self._current_input_dir_for_restore = input_dir # Store for use in helper function

        self._perform_sync_partition_operations(
            action_name_key="btn_mtk_restore_selected_partitions",
            action_verb_log="Restore",
            command_prefix_list=["w"], # mtkclient command for write is 'w'
            partitions_list=selected_partitions,
            extra_confirm_msg_key="mtk_warning_write" # You can add a new label key for write warning
        )
        delattr(self, "_current_input_dir_for_restore") # Cleanup


    def action_mtk_reset_nv_data(self):
        nv_partitions = ["nvram", "nvdata"]
        self._perform_sync_partition_operations(
            action_name_key="btn_mtk_reset_nv_data",
            action_verb_log="Reset (Erase)",
            command_prefix_list=["e"], # Erase is 'e'
            partitions_list=nv_partitions,
            extra_confirm_msg_key="mtk_warning_erase"
        )

    def action_mtk_erase_frp(self):
        action_name = self.labels.get("btn_mtk_erase_frp", "Erase FRP")
        # This is a single operation, can use _run_mtk_command
        cmd_args = ["e", "frp"] 
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_samsung_frp(self):
        action_name = self.labels.get("btn_mtk_samsung_frp", "Samsung FRP (MTK)")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        self._log_gui_event(f"Action '{action_name}' requires specific implementation or external tool - Placeholder.", "warning")
        messagebox.showinfo("Not Implemented", f"Action '{action_name}' requires device-specific methods not yet implemented here.", parent=parent_window)

    def action_mtk_safe_format(self):
        action_name = self.labels.get("btn_mtk_safe_format", "Safe Format Data")
        # Usually involves formatting userdata and metadata/md_udc
        # Since mtkclient might not support "safe format" as a single command, we'll erase userdata
        # User can erase metadata separately if needed
        self._log_gui_event("Note: Safe Format currently only erases 'userdata'. Metadata erase might be needed manually.", "info")
        cmd_args = ["e", "userdata"]
        self._run_mtk_command(cmd_args, action_name)


    def action_mtk_erase_frp_write_file(self):
        action_name = self.labels.get("btn_mtk_erase_frp_write_file", "Erase FRP (Write File)")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        input_file = filedialog.askopenfilename(title="Select FRP Reset File", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")], parent=parent_window)
        if not input_file: 
            self._log_gui_event("Erase FRP (File) cancelled.", "info")
            return
        cmd_args = ["w", "frp", input_file]
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_wipe_data(self):
        partitions_to_wipe = ["userdata", "metadata"] # May need to add cache as well
        self._perform_sync_partition_operations(
            action_name_key="btn_mtk_wipe_data",
            action_verb_log="Wipe",
            command_prefix_list=["e"],
            partitions_list=partitions_to_wipe,
            extra_confirm_msg_key="mtk_warning_erase_all_data" # New label key for wipe all data warning
        )

    def action_mtk_unlock_bootloader(self):
        action_name = self.labels.get("btn_mtk_unlock_bootloader", "Unlock Bootloader")
        cmd_args = ["da", "seccfg", "unlock"] # This is a common command, might vary
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_lock_bootloader(self):
        action_name = self.labels.get("btn_mtk_lock_bootloader", "Lock Bootloader")
        cmd_args = ["da", "seccfg", "lock"] # This is a common command, might vary
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_extract_keys(self):
        # Old name, redirects to Backup Security Partitions now
        self.action_mtk_backup_security_partitions()

    def action_mtk_generate_ewc(self):
        action_name = self.labels.get("btn_mtk_generate_ewc", "Guide: Generate EWC (Oxygen)")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        self._log_gui_event(f"Action '{action_name}' provides guidance only.", "info")
        messagebox.showinfo("Guidance", """Generating EWC token for Oxygen Forensic Detective typically involves:
1. Dumping specific partitions (e.g., userdata, metadata).
2. Using Oxygen's tools or specific scripts to process these dumps.
This tool can help with step 1 (use 'Read Userdata' or 'Read Full Dump'). Step 2 requires Oxygen software.""", parent=parent_window)

    def action_mtk_build_forensic_project(self):
        action_name = self.labels.get("btn_mtk_build_forensic_project", "Guide: Full Forensic Project")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        self._log_gui_event(f"Action '{action_name}' provides guidance only.", "info")
        messagebox.showinfo("Guidance", """Building a full forensic project usually involves:
1. Dumping all relevant partitions (Use 'Read Full Dump' or 'Backup Selected Partitions').
2. Dumping security keys/info if possible (Use 'Backup Security Partitions' or 'Dump HW Keys').
3. Importing these dumps into forensic software (e.g., Cellebrite UFED, Magnet AXIOM, Oxygen).""", parent=parent_window)

    def action_mtk_dump_hw_keys_brom(self):
        action_name = self.labels.get("btn_mtk_dump_hw_keys_brom", "Dump HW Keys [BROM]")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        output_file = filedialog.asksaveasfilename(title="Save BROM Dump As...", defaultextension=".bin", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")], parent=parent_window)
        if not output_file: 
            self._log_gui_event("Dump HW Keys [BROM] cancelled.", "info")
            return
        cmd_args = ["dumpbrom", "--filename", output_file]
        cmd_args.append("--socid") # Attempt to read SOC ID as well
        self._run_mtk_command(cmd_args, action_name)

    def action_mtk_dump_hw_keys_preloader(self):
        action_name = self.labels.get("btn_mtk_dump_hw_keys_preloader", "Dump HW Keys [PRELOADER]")
        parent_window = self.master_app.master if self.master_app and hasattr(self.master_app, 'master') else self
        output_file = filedialog.asksaveasfilename(title="Save Preloader Dump As...", defaultextension=".bin", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")], parent=parent_window)
        if not output_file: 
            self._log_gui_event("Dump HW Keys [PRELOADER] cancelled.", "info")
            return
        cmd_args = ["dumppreloader", "--filename", output_file]
        cmd_args.append("--socid") # Attempt to read SOC ID as well
        self._run_mtk_command(cmd_args, action_name)

# Example Usage (if run standalone for testing)
if __name__ == '__main__':
    root = tk.Tk()
    root.title("MTK Tab Test")
    root.geometry("850x700") # Slightly increased window size

    # Create dummy master app and log panel
    class DummyMasterApp(UltimateDeviceTool):
        def __init__(self, master_window): # Changed parameter name to avoid confusion
            super().__init__()
            self.master = master_window # Set the main window
            # Add more labels needed for testing
            self.labels = {
                "group_mtk_firmware_flash": "Firmware Flashing",
                "label_scatter_file": "Scatter File:",
                "btn_browse": "Browse...",
                "label_partitions_to_flash": "Partitions to Flash:",
                "btn_select_all": "All",
                "btn_deselect_all": "None",
                "btn_mtk_flash_scatter": "Flash Selected Partitions",
                "group_mtk_files": "Global Options",
                "label_da_file": "DA File:",
                "label_auth_file": "Auth File:",
                "label_preloader_file": "Preloader File:",
                "group_mtk_dump": "Dump Operations",
                "btn_mtk_read_full_dump": "Read Full Dump",
                "btn_mtk_read_userdata": "Read Userdata",
                "btn_mtk_read_custom_dump": "Read Custom Partition",
                "btn_mtk_auto_boot_repair_dump": "Dump Boot Repair Files",
                "btn_mtk_write_dump": "Write Partition",
                "group_mtk_partitions": "Partition Operations",
                "btn_mtk_list_partitions": "List Partitions (GPT)",
                "btn_mtk_backup_selected_partitions": "Backup Selected Partitions",
                "btn_mtk_backup_security_partitions": "Backup Security Partitions",
                "btn_mtk_format_selected_partitions": "Format Selected Partitions",
                "btn_mtk_restore_selected_partitions": "Restore Selected Partitions",
                "btn_mtk_reset_nv_data": "Reset NV Partitions",
                "group_mtk_frp_data": "FRP & Data Operations",
                "btn_mtk_erase_frp": "Erase FRP",
                "btn_mtk_samsung_frp": "Samsung FRP (MTK)",
                "btn_mtk_safe_format": "Safe Format Data",
                "btn_mtk_erase_frp_write_file": "Erase FRP (Write File)",
                "btn_mtk_wipe_data": "Wipe Data",
                "group_mtk_bootloader": "Bootloader Operations",
                "btn_mtk_unlock_bootloader": "Unlock Bootloader",
                "btn_mtk_lock_bootloader": "Lock Bootloader",
                "group_mtk_keys_forensics": "Keys & Forensics",
                "btn_mtk_extract_keys": "Attempt Key Partition Dump",
                "btn_mtk_generate_ewc": "Guide: Generate EWC (Oxygen)",
                "btn_mtk_build_forensic_project": "Guide: Full Forensic Project",
                "group_mtk_hw_utils": "Hardware Utilities",
                "btn_mtk_dump_hw_keys_brom": "Dump HW Keys [BROM]",
                "btn_mtk_dump_hw_keys_preloader": "Dump HW Keys [PRELOADER]",
                "select_file_title": "Select File",
                "no_partitions_found": "No downloadable partitions found.",
                "mtk_op_in_progress_title": "Operation in Progress",
                "mtk_op_in_progress_msg": "Another MTK operation is already running.",
                "mtk_confirm_action_title": "Confirm Action",
                "mtk_confirm_action_msg": "Are you sure you want to perform: {action_name}?",
                "mtk_confirm_action_msg_flash": "Are you sure you want to flash: {action_name}? This will write to the device!",
                "mtk_confirm_action_msg_flash_selected": "Are you sure you want to flash the selected {count} partition(s)?\nThis operation will block the UI until completed.",
                "mtk_warning_hw_dump": "WARNING: This is an advanced operation. It might read sensitive data or fail depending on device security. Proceed with caution.",
                "mtk_warning_erase": "WARNING: This will erase data and cannot be undone!",
                "mtk_warning_erase_all_data": "WARNING: This will erase all user data and metadata and cannot be undone!",
                "mtk_warning_write": "WARNING: This will overwrite existing data on the selected partition(s)!",
                "select_key_dump_folder_title": "Select Folder to Save Key Partitions",
                "mtk_confirm_action_msg_generic_multi": "Are you sure you want to {action} the following {count} partition(s):\n{partitions_str}?",
            }
            self.log_panel = LogPanelPlaceholder() # Using the placeholder log panel
            self.after = master_window.after # Using the main window's after function

        def _update_cancel_button_state(self, enable):
            print(f"Cancel button state: {enable}")

    app = DummyMasterApp(root)
    notebook = ttk.Notebook(root)
    mtk_tab = MTKTab(notebook, app) # Pass app as master_app
    notebook.add(mtk_tab, text='MTK')
    notebook.pack(expand=True, fill='both')

    # Add a dummy log panel area
    log_text_area = tk.Text(root, height=10, wrap=tk.WORD, font=FONT)
    log_text_area.pack(fill='x', side='bottom', padx=5, pady=5)
    
    # Redefine LogPanelPlaceholder to use the text area
    class RealLogPanel:
        def __init__(self, text_area):
            self.text_area = text_area
            self.text_area.tag_config("error", foreground="red")
            self.text_area.tag_config("success", foreground="green")
            self.text_area.tag_config("warning", foreground="orange") # Corrected from "darkorange"
            self.text_area.tag_config("info", foreground="blue")
            self.text_area.tag_config("debug", foreground="purple")
            self.text_area.tag_config("operation_status", foreground="black", font=LABEL_FONT)
            self.text_area.tag_config("device_info", foreground="darkblue")
            self.text_area.tag_config("raw_output", foreground="gray40", font=("Courier", 8))


        def log(self, message, tag="info", its=True): # its currently unused
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.text_area.insert(tk.END, f"[{timestamp}] [{tag.upper()}] {message}\n", tag)
            self.text_area.see(tk.END) # Scroll to bottom

        def clear_log(self):
            self.text_area.delete(1.0, tk.END)
            self.log("Log cleared.", "info")
        
        def show_progress(self):
            self.log("Progress: [##########]", "info") # Simulate progress bar

        def hide_progress(self):
            self.log("Progress hidden.", "info")
        
        def winfo_exists(self): # Check if the text_area widget still exists
            return self.text_area.winfo_exists()


    app.log_panel = RealLogPanel(log_text_area) # Use the real log panel now
    app.log_panel.log("MTK Tab Test Application Started.", "info")


    root.mainloop()
