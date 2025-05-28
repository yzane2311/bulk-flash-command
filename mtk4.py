#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess
import threading
import sqlite3
from datetime import datetime
import queue # For passing results from thread to main
import traceback # For detailed error logging
import webbrowser # For opening URL
import csv
import re # For parsing App Manager output
import shutil # For shutil.which
import tempfile # For temporary files in MTK operations
from pathlib import Path # For path operations

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Pillow library not found. Please install it: pip install Pillow. Image features will be limited.")

# Static debug log path and function, defined early for global use
_DEBUG_LOG_PATH = "application_debug_log.txt"

def log_to_file_debug_globally(message, level="INFO"):
    try:
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as f_log:
            f_log.write(f"[{datetime.now()}] [{level}] {message}\n")
    except Exception as e:
        print(f"[CRITICAL_ERROR] Global static log failed: {e} for message: {message}", file=sys.stderr)

log_to_file_debug_globally("Script execution started. Global logger active.")

# Fixed credentials for login
FIXED_USERNAME = "admin"
FIXED_PASSWORD = "admin"

# ========== LABELS ==========
LABELS = {
    "en": {
        "title": "Ultimat-Unlock Tool",
        "edition": "Samsung, Honor & Xiaomi Edition",
        "tab_samsung": "Samsung (ADB)",
        "tab_honor": "Honor (Fastboot)",
        "tab_xiaomi": "Xiaomi (ADB + Fastboot)",
        "tab_file_advanced": "Files & Advanced",
        "tab_app_manager": "App Manager",
        "tab_mtk": "MTK Tools", # New MTK Tab Label
        "log": "Operation Log",
        "group_samsung": "Samsung ADB Repair & Utilities",
        "group_file": "File & App Management",
        "group_honor": "Honor Fastboot Tools",
        "group_xiaomi_adb": "Xiaomi ADB Mode",
        "group_xiaomi_fastboot": "Xiaomi Fastboot Mode",
        "group_advanced_cmd": "Advanced Command Execution",
        "group_mtk_files": "MTK Custom Files",
        "group_mtk_dump": "MTK Dump Operations",
        "group_mtk_partitions": "MTK Partitions Manager",
        "group_mtk_frp_data": "MTK FRP & Data",
        "group_mtk_bootloader": "MTK Bootloader",
        "group_mtk_keys_forensics": "MTK Key Extraction & Forensics",
        "group_mtk_flash": "MTK Flash Operations", # New group for flashing
        "label_da_file": "DA File:",
        "label_auth_file": "Auth File:",
        "label_preloader_file": "Preloader File:",
        "btn_browse": "Browse",
        "btn_mtk_read_full_dump": "Read Full Dump (Userarea)",
        "btn_mtk_read_userdata": "Read Userdata",
        "btn_mtk_read_custom_dump": "Read Custom Dump (Select Partitions)",
        "btn_mtk_auto_boot_repair_dump": "Auto Boot Repair Dump",
        "btn_mtk_write_dump": "Write Full/Custom Dump",
        "btn_mtk_list_partitions": "List Partitions",
        "btn_mtk_backup_selected_partitions": "Backup Selected/All Partitions",
        "btn_mtk_backup_security_partitions": "Backup Security Partitions",
        "btn_mtk_format_selected_partitions": "Format Selected Partitions",
        "btn_mtk_restore_selected_partitions": "Restore Selected Partitions",
        "btn_mtk_reset_nv_data": "Reset NV Data (nvram, nvdata, nvcfg)",
        "btn_mtk_erase_frp": "Erase FRP",
        "btn_mtk_samsung_frp": "Samsung MTK FRP",
        "btn_mtk_safe_format": "Safe Format (Keep Data)",
        "btn_mtk_erase_frp_write_file": "Erase FRP (Write File)",
        "btn_mtk_wipe_data": "Wipe Data (userdata)",
        "btn_mtk_unlock_bootloader": "Unlock Bootloader (seccfg)",
        "btn_mtk_lock_bootloader": "Lock Bootloader (seccfg)",
        "btn_mtk_extract_keys": "Extract Keys (BROM/Preloader)",
        "btn_mtk_generate_ewc": "Generate EWC File (Oxygen Forensic)",
        "btn_mtk_build_forensic_project": "Build Full Forensic Project",
        "btn_mtk_flash_scatter": "Flash with Scatter File", # New button label
        "mtk_placeholder_msg": "MTK Action: {action}. DA: {da}, Auth: {auth}, PL: {pl}. Using mtkclient.",
        "mtk_file_not_selected": "{file_type} file not selected.",
        "mtk_select_dump_file": "Select Dump File to Write",
        "mtk_select_cfg_file": "Select CFG File for Dump/Partitions (Optional)",
        "mtk_select_frp_file": "Select FRP File to Write",
        "mtk_select_scatter_file": "Select Scatter File (.txt)",
        "mtk_select_firmware_dir": "Select Firmware Directory (containing partition images)",
        "mtk_confirm_action_title": "Confirm MTK Operation",
        "mtk_confirm_action_msg": "This MTK operation ({action_name}) can be risky and may alter device state or data. Ensure correct files are selected. Proceed with caution.",
        "mtk_partitions_prompt_title": "Select Partitions",
        "mtk_partitions_prompt_msg": "Enter partition names, comma-separated (e.g., boot,recovery,system):",
        "mtk_output_dir_prompt_title": "Select Output Directory",
        "mtk_no_partitions_selected": "No partitions selected or entered.",
        "mtk_client_not_found_title": "MTKClient Not Found",
        "mtk_client_not_found_msg": "mtkclient executable not found. Please ensure it is installed and in your system's PATH. MTK operations will not be available.",
        "ewc_save_title": "Save EWC File As",
        "btn_connection": "Check Connection",
        "btn_info": "Device Info",
        "btn_reboot_dl": "Reboot Download",
        "btn_reboot_rec": "Reboot Recovery",
        "btn_reboot_bl": "Reboot Bootloader",
        "btn_remove_frp": "Remove FRP (ADB)",
        "btn_usb_debug": "Enable USB Debug",
        "btn_repair_network": "Repair Network (root)",
        "btn_fix_perms": "Fix System Permissions",
        "btn_reset_wifi": "Reset WiFi",
        "btn_factory_reset": "Factory Reset (ADB)",
        "btn_mount_rw": "Mount System RW (root)",
        "btn_wipe_cache": "Wipe Cache (root)",
        "btn_clear_dalvik": "Clear Dalvik (root)",
        "btn_screenlock_reset": "Reset Screen Lock (ADB)",
        "btn_arabize_device": "Arabize Device (ADB)",
        "btn_open_browser_adb": "Open Browser (ADB)",
        "pull_file_title": "Pull File from Device",
        "pull_file_device_path_msg": "Enter device source path (e.g., /sdcard/file.txt):",
        "push_file_title": "Push File to Device",
        "push_file_device_path_msg": "Enter device destination path (e.g., /sdcard/newfile.txt):",
        "install_apk_title": "Select APK to Install",
        "uninstall_title": "Uninstall App",
        "uninstall_msg": "Enter package name (e.g., com.example.app):",
        "honor_frp_code_title": "Enter Honor FRP Key",
        "honor_frp_code_msg": "Please enter the Honor FRP unlock key:",
        "advanced_cmd_label": "Enter ADB or Fastboot command:",
        "btn_run_advanced_cmd": "Run Command",
        "adb_status_connected": "ADB: Connected",
        "adb_status_not_connected": "ADB: Not Connected",
        "adb_status_device_id_prefix": "Device ID: ",
        "search_log_label": "Search Log:",
        "find_button": "Find",
        "all_button": "All",
        "export_button": "Export to TXT",
        "btn_export_csv": "Export to CSV",
        "btn_cancel_operation": "Cancel Operation",
        "cancel_operation_warning_title": "Cancel Operation Warning",
        "cancel_operation_warning_message": "Stopping an operation abruptly might leave the device in an unstable state or cause issues. Are you sure you want to attempt to cancel?",
        "quit_dialog_title": "Quit",
        "quit_dialog_message": "Do you want to quit Ultimat-Unlock Tool?",
        "dependency_check_title": "Dependency Check",
        "adb_not_found_message": "ADB (Android Debug Bridge) not found or not working. Some features will be unavailable. Please install/configure ADB and add it to your system PATH.",
        "fastboot_not_found_message": "Fastboot not found or not working. Some features will be unavailable. Please install/configure Fastboot and add it to your system PATH.",
        "fatal_error_title": "Fatal Error",
        "fatal_error_message_prefix": "A critical error occurred:",
        "btn_get_detailed_info": "Read Device Info (ADB)",
        "btn_pull_file": "Pull File from Device",
        "btn_push_file": "Push File to Device",
        "btn_install_apk": "Install APK",
        "btn_uninstall_app": "Uninstall App",
        "btn_backup_user_data_adb": "Backup User Data (ADB)",
        "btn_restore_user_data_adb": "Restore User Data (ADB)",
        "backup_user_data_title": "Select Backup File Location",
        "backup_user_data_msg": "Choose where to save the user data backup (.ab file):",
        "restore_user_data_title": "Select Backup File to Restore",
        "restore_user_data_msg": "Choose the user data backup file (.ab) to restore:",
        "btn_honor_info": "Read Serial & Software Info",
        "honor_frp_key_label": "Honor FRP Key:",
        "btn_honor_frp": "Remove FRP (Honor Code)",
        "btn_honor_reboot_bl": "Reboot Bootloader (Honor)",
        "btn_honor_reboot_edl": "Reboot EDL (Honor)",
        "btn_honor_wipe_data_cache": "Wipe Data/Cache (Honor)",
        "btn_xiaomi_adb_info": "Read Device Info (ADB)",
        "btn_xiaomi_enable_diag_root": "Enable Diag (ROOT)",
        "btn_xiaomi_reset_frp_adb": "Reset FRP (ADB)",
        "btn_xiaomi_bypass_mi_account": "Bypass Mi Account (ADB)",
        "btn_xiaomi_reboot_normal_adb": "Reboot Normal (ADB)",
        "btn_xiaomi_reboot_fastboot_adb": "Reboot Fastboot (ADB)",
        "btn_xiaomi_reboot_recovery_adb": "Reboot Recovery (ADB)",
        "btn_xiaomi_reboot_edl_adb": "Reboot EDL (ADB)",
        "btn_xiaomi_fastboot_info": "Read Info (Fastboot)",
        "btn_xiaomi_fastboot_read_security": "Read Security (Fastboot)",
        "btn_xiaomi_fastboot_unlock": "Unlock Bootloader (Fastboot)",
        "btn_xiaomi_fastboot_lock": "Lock Bootloader (Fastboot)",
        "btn_xiaomi_fastboot_reboot_sys": "Reboot System (Fastboot)",
        "btn_xiaomi_fastboot_reboot_fast": "Reboot Fastboot (Fastboot)",
        "btn_xiaomi_fastboot_reboot_edl": "Reboot EDL (Fastboot)",
        "btn_xiaomi_fastboot_wipe_cache": "Wipe Cache (Fastboot)",
        "btn_xiaomi_fastboot_wipe_data": "Wipe Data (Fastboot)",
        "lang": "Language",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "professional_dark": "Professional Dark",
        "arabic": "Arabic",
        "english": "English",
        "login_title": "Login - Ultimat-Unlock Tool",
        "username_label": "Username:",
        "password_label": "Password:",
        "login_button": "Login",
        "login_failed_title": "Login Failed",
        "login_failed_message": "Invalid username or password.",
        "arabize_confirm_title": "Confirm Arabization",
        "arabize_confirm_message": "This will attempt to change the device language to Arabic (ar-AE).\nThis may require specific permissions and might not work on all devices.\nProceed?",
        "arabize_note": "Note: Arabization might require WRITE_SECURE_SETTINGS permission or root on some devices. Effectiveness varies.",
        "open_browser_title": "Open URL in Device Browser",
        "open_browser_prompt": "Enter the full URL to open (e.g., https://ultimat-unlock.com/):",
        "frp_reset_warning_title": "FRP Reset Attempt",
                "frp_reset_warning_message": "This will attempt a series of common ADB commands to reset FRP. TThis command will reset FRP packages."
        "screen_lock_reset_warning_title": "Screen Lock Reset Attempt",
        "screen_lock_reset_warning_message": "This attempts to remove screen lock files. It usually requires ROOT access and is unlikely to work on modern Android versions due to encryption. Data loss[...]
        "context_cut": "Cut",
        "context_copy": "Copy",
        "context_paste": "Paste",
        "context_select_all": "Select All",
        "log_connect_server_success": "Connect to server...successful",
        "log_operation_started": "Operation Started: ",
        "log_device_info_header": "Device Information:",
        "log_frp_reset_ok": "FRP Reset.... OK",
        "log_frp_reset_fail": "FRP Reset.... FAILED",
        "log_read_info_complete": "Read Info.... COMPLETE",
        "btn_telegram_channel": "Telegram Channel",
        "btn_contact_support": "Contact Support",
        "btn_group_support": "Group Support",
        "device_status_panel_title": "ADB Connection Status",
        "status_model": "Model:",
        "status_android": "Android:",
        "status_connection": "Connection:",
        "status_root": "Root:",
        "status_unknown": "Unknown",
        "btn_refresh_adb_top": "Refresh ADB",
        "login_window_title": "Ultimat-Unlock V2.2.2",
        "email_or_username_label": "Email or Username:",
        "remember_me_label": "Remember Me",
        "website_label": "Website",
        "support_label": "Support",
        "signup_label": "sign up",
        "login_button_text": "LOGIN",
        "login_main_title": "Ultimat-Unlock tool",
        "btn_pull_contacts_vcf": "Pull Contacts (VCF)",
        "pull_contacts_title": "Save Contacts As",
        "pull_contacts_confirm_msg": "Attempt to pull contacts and save as VCF? This method might not get all details and requires ADB.",
        "pull_contacts_no_output": "No contacts data retrieved or error parsing output.",
        "pull_contacts_file_error": "Error writing VCF file.",
        "app_manager_filter_all": "All Apps",
        "app_manager_filter_system": "System Apps",
        "app_manager_filter_third_party": "Third-party Apps",
        "btn_refresh_app_list": "Refresh List",
        "btn_copy_package_name": "Copy Package Name",
        "btn_uninstall_selected_app": "Uninstall Selected App",
        "app_manager_search_label": "Search Package:",
        "uninstall_app_confirm_title": "Confirm Uninstall",
        "uninstall_app_confirm_message": "Are you sure you want to uninstall the selected application: {package_name}?",
        "no_app_selected_title": "No Selection",
        "no_app_selected_message": "Please select an application from the list first.",
        "btn_remove_mdm": "Remove MDM (ADB)",
        "btn_bypass_knox": "Bypass Knox (ADB)",
        "mdm_remove_warning_title": "MDM Removal Attempt",
        "mdm_remove_warning_message": "This will attempt to disable common MDM-related packages via ADB. This operation is not guaranteed to work on all devices/setups and might have unintended conseq[...]
        "knox_bypass_warning_title": "Knox Bypass Attempt",
        "knox_bypass_warning_message": "This will attempt to disable common Knox-related packages via ADB. This operation is intended for specific scenarios like school tablets after use and is not gu[...]
        "log_mdm_remove_start": "Starting MDM Removal sequence (ADB)...",
        "log_mdm_remove_ok": "MDM Removal sequence attempted. Check device functionality.",
        "log_mdm_remove_fail": "MDM Removal sequence encountered issues.",
        "log_knox_bypass_start": "Starting Knox Bypass sequence (ADB)...",
        "log_knox_bypass_ok": "Knox Bypass sequence attempted. Check device functionality.",
        "log_knox_bypass_fail": "Knox Bypass sequence encountered issues."
    },
    "ar": {
        "title": "أداة Ultimat-Unlock",
        "edition": "إصدار سامسونج، هونور، شاومي",
        "tab_samsung": "سامسونج (ADB)",
        "tab_honor": "هونور (Fastboot)",
        "tab_xiaomi": "شاومي (ADB + Fastboot)",
        "tab_file_advanced": "ملفات وأدوات متقدمة",
        "tab_app_manager": "مدير التطبيقات",
        "tab_mtk": "أدوات MTK", # New MTK Tab Label AR
        "log": "سجل العمليات",
        "group_samsung": "إصلاح سامسونج وأدوات ADB",
        "group_file": "إدارة الملفات والتطبيقات",
        "group_honor": "أدوات هونور Fastboot",
        "group_xiaomi_adb": "شاومي وضع ADB",
        "group_xiaomi_fastboot": "شاومي وضع Fastboot",
        "group_advanced_cmd": "تنفيذ أوامر متقدمة",
        "group_mtk_files": "ملفات MTK المخصصة",
        "group_mtk_dump": "عمليات سحب MTK Dump",
        "group_mtk_partitions": "مدير أقسام MTK",
        "group_mtk_frp_data": "MTK FRP والبيانات",
        "group_mtk_bootloader": "MTK Bootloader",
        "group_mtk_keys_forensics": "استخراج مفاتيح MTK والتحليل الجنائي",
        "group_mtk_flash": "عمليات تفليش MTK", # New group for flashing AR
        "label_da_file": "ملف DA:",
        "label_auth_file": "ملف Auth:",
        "label_preloader_file": "ملف Preloader:",
        "btn_browse": "استعراض",
        "btn_mtk_read_full_dump": "قراءة Full Dump (Userarea)",
        "btn_mtk_read_userdata": "قراءة Userdata",
        "btn_mtk_read_custom_dump": "قراءة Dump مخصص (اختر الأقسام)",
        "btn_mtk_auto_boot_repair_dump": "سحب Dump تلقائي لإصلاح الإقلاع",
        "btn_mtk_write_dump": "كتابة Full/Custom Dump",
        "btn_mtk_list_partitions": "عرض الأقسام",
        "btn_mtk_backup_selected_partitions": "نسخ احتياطي للأقسام المحددة/الكل",
        "btn_mtk_backup_security_partitions": "نسخ احتياطي لأقسام الأمان",
        "btn_mtk_format_selected_partitions": "تهيئة الأقسام المحددة",
        "btn_mtk_restore_selected_partitions": "استعادة الأقسام المحددة",
        "btn_mtk_reset_nv_data": "إعادة ضبط بيانات NV",
        "btn_mtk_erase_frp": "مسح FRP",
        "btn_mtk_samsung_frp": "Samsung MTK FRP",
        "btn_mtk_safe_format": "تهيئة آمنة (مع الحفاظ على البيانات)",
        "btn_mtk_erase_frp_write_file": "مسح FRP (كتابة ملف)",
        "btn_mtk_wipe_data": "مسح البيانات (userdata)",
        "btn_mtk_unlock_bootloader": "فتح البوتلودر (seccfg)",
        "btn_mtk_lock_bootloader": "قفل البوتلودر (seccfg)",
        "btn_mtk_extract_keys": "استخراج المفاتيح (BROM/Preloader)",
        "btn_mtk_generate_ewc": "إنشاء ملف EWC (Oxygen Forensic)",
        "btn_mtk_build_forensic_project": "إنشاء مشروع تحليل جنائي كامل",
        "btn_mtk_flash_scatter": "تفليش باستخدام ملف Scatter", # New button label AR
        "mtk_placeholder_msg": "إجراء MTK: {action}. DA: {da}, Auth: {auth}, PL: {pl}. جاري استخدام mtkclient.",
        "mtk_file_not_selected": "لم يتم تحديد ملف {file_type}.",
        "mtk_select_dump_file": "اختر ملف Dump للكتابة",
        "mtk_select_cfg_file": "اختر ملف CFG للـ Dump/الأقسام (اختياري)",
        "mtk_select_frp_file": "اختر ملف FRP للكتابة",
        "mtk_select_scatter_file": "اختر ملف Scatter (.txt)",
        "mtk_select_firmware_dir": "اختر مجلد الفيرموير (يحتوي على صور الأقسام)",
        "mtk_confirm_action_title": "تأكيد عملية MTK",
        "mtk_confirm_action_msg": "عملية MTK هذه ({action_name}) قد تكون خطيرة وقد تغير حالة الجهاز أو بياناته. تأكد من اختيار الملفات [...]
        "mtk_partitions_prompt_title": "اختر الأقسام",
        "mtk_partitions_prompt_msg": "أدخل أسماء الأقسام مفصولة بفاصلة (مثال: boot,recovery,system):",
        "mtk_output_dir_prompt_title": "اختر مجلد الإخراج",
        "mtk_no_partitions_selected": "لم يتم اختيار أو إدخال أي أقسام.",
        "mtk_client_not_found_title": "لم يتم العثور على MTKClient",
        "mtk_client_not_found_msg": "لم يتم العثور على برنامج mtkclient. يرجى التأكد من تثبيته وإضافته إلى مسار النظام. عمليات MTK لن [...]
        "ewc_save_title": "حفظ ملف EWC باسم",
        "btn_connection": "فحص الاتصال",
        "btn_info": "معلومات الجهاز",
        "btn_reboot_dl": "إعادة تشغيل لوضع الداونلود",
        "btn_reboot_rec": "إعادة تشغيل للريكفري",
        "btn_reboot_bl": "إعادة تشغيل للبوتلودر",
        "btn_remove_frp": "إزالة FRP (ADB)",
        "btn_usb_debug": "تفعيل تصحيح USB",
        "btn_repair_network": "إصلاح الشبكة (روت)",
        "btn_fix_perms": "إصلاح صلاحيات النظام",
        "btn_reset_wifi": "إعادة ضبط WiFi",
        "btn_factory_reset": "إعادة ضبط المصنع (ADB)",
        "btn_mount_rw": "جعل النظام قابل للكتابة (روت)",
        "btn_wipe_cache": "مسح الكاش (روت)",
        "btn_clear_dalvik": "مسح دالفك (روت)",
        "btn_screenlock_reset": "إزالة قفل الشاشة (ADB)",
        "btn_arabize_device": "تعريب الهاتف (ADB)",
        "btn_open_browser_adb": "فتح المتصفح (ADB)",
        "pull_file_title": "سحب ملف من الجهاز",
        "pull_file_device_path_msg": "أدخل مسار الملف المصدر بالجهاز (مثال: /sdcard/file.txt):",
        "push_file_title": "رفع ملف إلى الجهاز",
        "push_file_device_path_msg": "أدخل مسار الوجهة بالجهاز (مثال: /sdcard/newfile.txt):",
        "install_apk_title": "اختر ملف APK للتثبيت",
        "uninstall_title": "حذف تطبيق",
        "uninstall_msg": "أدخل اسم الحزمة (مثال: com.example.app):",
        "honor_frp_code_title": "إدخال رمز FRP لهونور",
        "honor_frp_code_msg": "الرجاء إدخال رمز فك قفل FRP الخاص بهونور:",
        "advanced_cmd_label": "أدخل أمر ADB أو Fastboot:",
        "btn_run_advanced_cmd": "تنفيذ الأمر",
        "adb_status_connected": "ADB: متصل",
        "adb_status_not_connected": "ADB: غير متصل",
        "adb_status_device_id_prefix": "معرف الجهاز: ",
        "search_log_label": "بحث في السجل:",
        "find_button": "بحث",
        "all_button": "الكل",
        "export_button": "تصدير إلى TXT",
        "btn_export_csv": "تصدير إلى CSV",
        "btn_cancel_operation": "إلغاء العملية",
        "cancel_operation_warning_title": "تحذير إلغاء العملية",
        "cancel_operation_warning_message": "إيقاف العملية بشكل مفاجئ قد يترك الجهاز في حالة غير مستقرة أو يسبب مشاكل. هل أنت متأكد[...]
        "quit_dialog_title": "خروج",
        "quit_dialog_message": "هل تريد الخروج من أداة Ultimat-Unlock؟",
        "dependency_check_title": "فحص الاعتماديات",
        "adb_not_found_message": "ADB (Android Debug Bridge) غير موجود أو لا يعمل. بعض الميزات لن تكون متاحة. الرجاء تثبيت/تكوين ADB وإضافته[...]
        "fastboot_not_found_message": "Fastboot غير موجود أو لا يعمل. بعض الميزات لن تكون متاحة. الرجاء تثبيت/تكوين Fastboot وإضافته إلى [...]
        "fatal_error_title": "خطأ فادح",
        "fatal_error_message_prefix": "حدث خطأ حرج:",
        "btn_get_detailed_info": "قراءة معلومات الجهاز (ADB)",
        "btn_pull_file": "سحب ملف من الجهاز",
        "btn_push_file": "رفع ملف إلى الجهاز",
        "btn_install_apk": "تثبيت APK",
        "btn_uninstall_app": "حذف تطبيق",
        "btn_backup_user_data_adb": "نسخ احتياطي لبيانات المستخدم (ADB)",
        "btn_restore_user_data_adb": "استعادة بيانات المستخدم (ADB)",
        "backup_user_data_title": "اختر موقع ملف النسخ الاحتياطي",
        "backup_user_data_msg": "اختر مكان حفظ النسخ الاحتياطي لبيانات المستخدم (ملف .ab):",
        "restore_user_data_title": "اختر ملف النسخ الاحتياطي للاستعادة",
        "restore_user_data_msg": "اختر ملف النسخ الاحتياطي لبيانات المستخدم (.ab) للاستعادة:",
        "btn_honor_info": "قراءة معلومات وسيريال هونور",
        "honor_frp_key_label": "رمز FRP لهونور:",
        "btn_honor_frp": "إزالة FRP (رمز هونور)",
        "btn_honor_reboot_bl": "إعادة تشغيل للبوتلودر (هونور)",
        "btn_honor_reboot_edl": "إعادة تشغيل لوضع EDL (هونور)",
        "btn_honor_wipe_data_cache": "مسح الداتا والكاش (هونور)",
        "btn_xiaomi_adb_info": "قراءة معلومات الجهاز (ADB)",
        "btn_xiaomi_enable_diag_root": "تفعيل Diag (روت)",
        "btn_xiaomi_reset_frp_adb": "إعادة تعيين FRP (ADB)",
        "btn_xiaomi_bypass_mi_account": "تجاوز حساب Mi (ADB)",
        "btn_xiaomi_reboot_normal_adb": "إعادة تشغيل عادي (ADB)",
        "btn_xiaomi_reboot_fastboot_adb": "إعادة تشغيل فاستبوت (ADB)",
        "btn_xiaomi_reboot_recovery_adb": "إعادة تشغيل ريكفري (ADB)",
        "btn_xiaomi_reboot_edl_adb": "إعادة تشغيل EDL (ADB)",
        "btn_xiaomi_fastboot_info": "قراءة المعلومات (Fastboot)",
        "btn_xiaomi_fastboot_read_security": "قراءة الأمان (Fastboot)",
        "btn_xiaomi_fastboot_unlock": "فتح البوتلودر (Fastboot)",
        "btn_xiaomi_fastboot_lock": "قفل البوتلودر (Fastboot)",
        "btn_xiaomi_fastboot_reboot_sys": "إعادة تشغيل للنظام (Fastboot)",
        "btn_xiaomi_fastboot_reboot_fast": "إعادة تشغيل فاستبوت (Fastboot)",
        "btn_xiaomi_fastboot_reboot_edl": "إعادة تشغيل EDL (Fastboot)",
        "btn_xiaomi_fastboot_wipe_cache": "مسح الكاش (Fastboot)",
        "btn_xiaomi_fastboot_wipe_data": "مسح الداتا (Fastboot)",
        "lang": "اللغة",
        "theme": "الثيم",
        "light": "فاتح",
        "dark": "داكن",
        "professional_dark": "داكن احترافي",
        "arabic": "العربية",
        "english": "الإنجليزية",
        "login_title": "تسجيل الدخول - أداة Ultimat-Unlock",
        "username_label": "اسم المستخدم:",
        "password_label": "كلمة المرور:",
        "login_button": "تسجيل الدخول",
        "login_failed_title": "فشل تسجيل الدخول",
        "login_failed_message": "اسم المستخدم أو كلمة المرور غير صحيحة.",
        "arabize_confirm_title": "تأكيد التعريب",
        "arabize_confirm_message": "سيحاول هذا الإجراء تغيير لغة الجهاز إلى العربية (ar-AE).\nقد يتطلب هذا أذونات معينة وقد لا يعم[...]
        "arabize_note": "ملاحظة: قد يتطلب التعريب إذن WRITE_SECURE_SETTINGS أو صلاحيات الروت على بعض الأجهزة. تختلف الفعالية.",
        "open_browser_title": "فتح رابط في متصفح الجهاز",
        "open_browser_prompt": "أدخل الرابط الكامل للفتح (مثال: https://ultimat-unlock.com/):",
        "frp_reset_warning_title": "محاولة إزالة FRP",
        "frp_reset_warning_message": "سيقوم هذا الإجراء بمحاولة تنفيذ سلسلة من أوامر ADB الشائعة لإزالة قفل FRP. هذه الأوامر ليست [...]
        "screen_lock_reset_warning_title": "محاولة إزالة قفل الشاشة",
        "screen_lock_reset_warning_message": "يحاول هذا الإجراء إزالة ملفات قفل الشاشة. يتطلب عادةً صلاحيات الروت ومن غير المرجح أ[...]
        "context_cut": "قص",
        "context_copy": "نسخ",
        "context_paste": "لصق",
        "context_select_all": "تحديد الكل",
        "log_connect_server_success": "الاتصال بالخادم... ناجح",
        "log_operation_started": "بدء العملية: ",
        "log_device_info_header": "معلومات الجهاز:",
        "log_frp_reset_ok": "إعادة تعيين FRP.... تم بنجاح",
        "log_frp_reset_fail": "إعادة تعيين FRP.... فشل",
        "log_read_info_complete": "قراءة المعلومات.... اكتمل",
        "btn_telegram_channel": "قناة تيليجرام",
        "btn_contact_support": "تواصل مع الدعم",
        "btn_group_support": "دعم المجموعة",
        "device_status_panel_title": "حالة اتصال ADB",
        "status_model": "الطراز:",
        "status_android": "أندرويد:",
        "status_connection": "الاتصال:",
        "status_root": "الروت:",
        "status_unknown": "غير معروف",
        "btn_refresh_adb_top": "تحديث ADB",
        "login_window_title": "Ultimat-Unlock V2.2.2",
        "email_or_username_label": "البريد الإلكتروني أو اسم المستخدم:",
        "remember_me_label": "تذكرني",
        "website_label": "الموقع",
        "support_label": "الدعم",
        "signup_label": "إنشاء حساب",
        "login_button_text": "تسجيل الدخول",
        "login_main_title": "أداة Ultimat-Unlock",
        "btn_pull_contacts_vcf": "سحب جهات الاتصال (VCF)",
        "pull_contacts_title": "حفظ جهات الاتصال باسم",
        "pull_contacts_confirm_msg": "محاولة سحب جهات الاتصال وحفظها كملف VCF؟ قد لا تحصل هذه الطريقة على كل التفاصيل وتتطلب ADB.",
        "pull_contacts_no_output": "لم يتم استرداد بيانات جهات الاتصال أو حدث خطأ في تحليل الإخراج.",
        "pull_contacts_file_error": "خطأ في كتابة ملف VCF.",
        "app_manager_filter_all": "كل التطبيقات",
        "app_manager_filter_system": "تطبيقات النظام",
        "app_manager_filter_third_party": "تطبيقات الطرف الثالث",
        "btn_refresh_app_list": "تحديث القائمة",
        "btn_copy_package_name": "نسخ اسم الحزمة",
        "btn_uninstall_selected_app": "إلغاء تثبيت المحدد",
        "app_manager_search_label": "بحث عن حزمة:",
        "uninstall_app_confirm_title": "تأكيد إلغاء التثبيت",
        "uninstall_app_confirm_message": "هل أنت متأكد أنك تريد إلغاء تثبيت التطبيق المحدد: {package_name}؟",
        "no_app_selected_title": "لم يتم التحديد",
        "no_app_selected_message": "الرجاء تحديد تطبيق من القائمة أولاً.",
        "btn_remove_mdm": "إزالة MDM (ADB)",
        "btn_bypass_knox": "تجاوز Knox (ADB)",
        "mdm_remove_warning_title": "محاولة إزالة MDM",
        "mdm_remove_warning_message": "سيحاول هذا الإجراء تعطيل حزم MDM الشائعة عبر ADB. هذا الإجراء غير مضمون للعمل على جميع الأجه[...]
        "knox_bypass_warning_title": "محاولة تجاوز Knox",
        "knox_bypass_warning_message": "سيحاول هذا الإجراء تعطيل حزم Knox الشائعة عبر ADB. هذا الإجراء مخصص لسيناريوهات محددة مثل أ[...]
        "log_mdm_remove_start": "بدء تسلسل إزالة MDM (ADB)...",
        "log_mdm_remove_ok": "تمت محاولة تسلسل إزالة MDM. تحقق من وظائف الجهاز.",
        "log_mdm_remove_fail": "واجه تسلسل إزالة MDM مشاكل.",
        "log_knox_bypass_start": "بدء تسلسل تجاوز Knox (ADB)...",
        "log_knox_bypass_ok": "تمت محاولة تسلسل تجاوز Knox. تحقق من وظائف الجهاز.",
        "log_knox_bypass_fail": "واجه تسلسل تجاوز Knox مشاكل."
    }
}
log_to_file_debug_globally("LABELS defined.")

# ========== THEMES ==========
DARK_BLUE_ACCENT = "#003366"
DARK_BLUE_ACCENT2 = "#002244"
CANCEL_BTN_RED_BG = "#C62828" # Darker Red
CANCEL_BTN_RED_FG = "#FFFFFF"
CANCEL_BTN_RED_ACTIVE_BG = "#B71C1C" # Even Darker Red

THEMES = {
    "light": {
        "BG": "#ECEFF1", "FG": "#263238", "ACCENT": DARK_BLUE_ACCENT, "ACCENT2": DARK_BLUE_ACCENT2, "PROGRESS_BAR_BG": "#2ECC71",
        "BTN_BG": DARK_BLUE_ACCENT, "BTN_BG2": DARK_BLUE_ACCENT2, "BTN_FG": "#FFFFFF", "BTN_BORDER": DARK_BLUE_ACCENT2,
        "GROUP_BG": "#FFFFFF", "LOG_BG": "#CFD8DC", "DEVICE_STATUS_BG": "#B0BEC5", "DEVICE_STATUS_FG": "#263238",
        "LOG_FG_SUCCESS": "#4CAF50", "LOG_FG_INFO": "#2196F3", "LOG_FG_ERROR": "#F44336",
        "LOG_FG_FAIL": "#D32F2F", "LOG_FG_CMD": "#00796B", "LOG_FG_WARNING": "#FF9800",
        "STATUS_BAR_BG": "#B0BEC5", "STATUS_BAR_FG": "#263238",
        "NOTEBOOK_TAB_BG": "#B0BEC5", "NOTEBOOK_TAB_FG": "#37474F",
        "NOTEBOOK_TAB_SELECTED_BG": DARK_BLUE_ACCENT, "NOTEBOOK_TAB_SELECTED_FG": "#FFFFFF",
        "NOTEBOOK_TAB_ACTIVE_BG": DARK_BLUE_ACCENT2,
        "CANCEL_BTN_BG_ACTIVE": CANCEL_BTN_RED_BG, "CANCEL_BTN_FG_ACTIVE": CANCEL_BTN_RED_FG,
        "CANCEL_BTN_HOVER_BG_ACTIVE": CANCEL_BTN_RED_ACTIVE_BG
    },
    "dark": {
        "BG": "#263238", "FG": "#ECEFF1", "ACCENT": DARK_BLUE_ACCENT, "ACCENT2": DARK_BLUE_ACCENT2, "PROGRESS_BAR_BG": "#2ECC71",
        "BTN_BG": DARK_BLUE_ACCENT, "BTN_BG2": DARK_BLUE_ACCENT2, "BTN_FG": "#FFFFFF", "BTN_BORDER": DARK_BLUE_ACCENT,
        "GROUP_BG": "#37474F", "LOG_BG": "#455A64", "DEVICE_STATUS_BG": "#37474F", "DEVICE_STATUS_FG": "#ECEFF1",
        "LOG_FG_SUCCESS": "#81C784", "LOG_FG_INFO": "#64B5F6", "LOG_FG_ERROR": "#E57373",
        "LOG_FG_FAIL": "#EF5350", "LOG_FG_CMD": "#4DB6AC", "LOG_FG_WARNING": "#FFB74D",
        "STATUS_BAR_BG": "#212121", "STATUS_BAR_FG": DARK_BLUE_ACCENT,
        "NOTEBOOK_TAB_BG": "#37474F", "NOTEBOOK_TAB_FG": "#B0BEC5",
        "NOTEBOOK_TAB_SELECTED_BG": DARK_BLUE_ACCENT, "NOTEBOOK_TAB_SELECTED_FG": "#FFFFFF",
        "NOTEBOOK_TAB_ACTIVE_BG": DARK_BLUE_ACCENT2,
        "CANCEL_BTN_BG_ACTIVE": CANCEL_BTN_RED_BG, "CANCEL_BTN_FG_ACTIVE": CANCEL_BTN_RED_FG,
        "CANCEL_BTN_HOVER_BG_ACTIVE": CANCEL_BTN_RED_ACTIVE_BG
    },
    "professional_dark": {
        "BG": "#21252B", "FG": "#D1D9E0", "ACCENT": DARK_BLUE_ACCENT, "ACCENT2": DARK_BLUE_ACCENT2, "PROGRESS_BAR_BG": "#2ECC71",
        "BTN_BG": DARK_BLUE_ACCENT, "BTN_BG2": DARK_BLUE_ACCENT2, "BTN_FG": "#FFFFFF", "BTN_BORDER": DARK_BLUE_ACCENT,
        "GROUP_BG": "#2C313A", "LOG_BG": "#2C313A", "DEVICE_STATUS_BG": "#2C313A", "DEVICE_STATUS_FG": "#D1D9E0",
        "LOG_FG_SUCCESS": "#2ECC71", "LOG_FG_INFO": "#3498DB", "LOG_FG_ERROR": "#E74C3C",
        "LOG_FG_FAIL": "#C0392B", "LOG_FG_CMD": "#1ABC9C", "LOG_FG_WARNING": "#F39C12",
        "STATUS_BAR_BG": "#1A1D21", "STATUS_BAR_FG": DARK_BLUE_ACCENT,
        "NOTEBOOK_TAB_BG": "#2C313A", "NOTEBOOK_TAB_FG": "#AAB8C5",
        "NOTEBOOK_TAB_SELECTED_BG": DARK_BLUE_ACCENT, "NOTEBOOK_TAB_SELECTED_FG": "#FFFFFF",
        "NOTEBOOK_TAB_ACTIVE_BG": DARK_BLUE_ACCENT2,
        "TITLE_FG": "#FFFFFF", "EDITION_FG": "#AAB8C5",
        "CANCEL_BTN_BG_ACTIVE": CANCEL_BTN_RED_BG, "CANCEL_BTN_FG_ACTIVE": CANCEL_BTN_RED_FG,
        "CANCEL_BTN_HOVER_BG_ACTIVE": CANCEL_BTN_RED_ACTIVE_BG
    }
}
log_to_file_debug_globally("THEMES defined.")

FONT = ("Segoe UI", 10)
TITLE_FONT = ("Segoe UI Semibold", 18)
APP_LOGO_TITLE_FONT = ("Segoe UI Semibold", 16)
SUBTITLE_FONT = ("Segoe UI", 8)
DEVICE_STATUS_FONT_LABEL = ("Segoe UI", 9, "bold")
DEVICE_STATUS_FONT_VALUE = ("Segoe UI", 9)
LABEL_FONT = ("Segoe UI", 9, "bold")
BTN_FONT = ("Segoe UI", 10, "bold") # Increased button font size slightly for "inflated" look
LOG_FONT = ("Consolas", 11)
log_to_file_debug_globally("FONTS defined.")

app_images = {}

def load_image(image_path, size=None):
    if not PIL_AVAILABLE:
        log_to_file_debug_globally(f"Pillow not available, cannot load {image_path}.", "WARNING")
        return None
    try:
        # Try to find assets directory relative to script location
        # This is more robust, especially if the script is run from a different CWD
        base_dir = Path(sys.argv[0]).resolve().parent
        full_path = base_dir / "assets" / image_path
        if not full_path.exists(): # Fallback to script's current directory if not in assets
            full_path = base_dir / image_path

        if not full_path.exists():
            log_to_file_debug_globally(f"Image file not found: {full_path}", "WARNING")
            return None

        img = Image.open(full_path)
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except FileNotFoundError: # Should be caught by exists() check, but as a safeguard
        log_to_file_debug_globally(f"Image file not found (direct FileNotFoundError): {image_path}", "WARNING")
    except Exception as e:
        log_to_file_debug_globally(f"Error loading image {image_path}: {e}", "ERROR")
        # Print detailed traceback for image loading errors as they can be subtle
        log_to_file_debug_globally(traceback.format_exc(), "ERROR_TRACE")
    return None

DEVICE_INFO_PROPERTIES = [
    ("Model", "ro.product.model"),
    ("Device", "ro.product.device"),
    ("Brand Name", "ro.product.brand"),
    ("Chipset", "ro.board.platform"),
    ("Hw Version", "ro.hardware"),
    ("Android Version", "ro.build.version.release"),
    ("Usb.config", "sys.usb.config"),
    ("Model ID", "ro.build.display.id"),
    ("PDA", "ro.build.id"),
    ("Platform", "ro.product.cpu.abi"),
    ("language", "ro.product.locale"),
    ("Security Patch", "ro.build.version.security_patch"),
    ("Root State", "ro.secure"),
    ("Encryption State", "ro.crypto.state"),
    ("Bootloader State", "ro.bootloader"),
    ("description", "ro.build.description")
]

def get_labels(lang):
    return LABELS.get(lang, LABELS["en"])

def get_theme(theme_name):
    return THEMES.get(theme_name, THEMES["light"])

class ModernButton(tk.Button):
    def __init__(self, master, text, command, theme, width=28, height=1, icon_path=None, icon_size=(16,16), state=tk.NORMAL, relief="raised", borderwidth=2, padx=8, pady=4, **kwargs): # Increased widt[...]
        self.icon_image = None
        if icon_path and PIL_AVAILABLE:
            try:
                self.icon_image = load_image(icon_path, size=icon_size)
                if self.icon_image:
                    app_images[f"btn_{text}_{icon_path}"] = self.icon_image
            except Exception as e:
                log_to_file_debug_globally(f"Failed to load button icon {icon_path}: {e}", "WARNING")
                self.icon_image = None

        bg_color = kwargs.pop('bg', theme["BTN_BG"])
        fg_color = kwargs.pop('fg', theme["BTN_FG"])
        active_bg_color = kwargs.pop('activebackground', theme["BTN_BG2"])
        active_fg_color = kwargs.pop('activeforeground', theme["BTN_FG"])

        # Special handling for Cancel button colors when active
        if text == get_labels(theme.get("lang_for_cancel", "en")).get("btn_cancel_operation", "Cancel Operation") and state == tk.NORMAL:
            bg_color = theme.get("CANCEL_BTN_BG_ACTIVE", CANCEL_BTN_RED_BG)
            fg_color = theme.get("CANCEL_BTN_FG_ACTIVE", CANCEL_BTN_RED_FG)
            active_bg_color = theme.get("CANCEL_BTN_HOVER_BG_ACTIVE", CANCEL_BTN_RED_ACTIVE_BG)


        super().__init__(
            master, text=text, command=command, font=kwargs.pop('font', BTN_FONT),
            bg=bg_color, fg=fg_color,
            activebackground=active_bg_color, activeforeground=active_fg_color,
            bd=borderwidth, relief=relief, cursor="hand2", height=height, width=width,
            padx=padx,
            pady=pady,
            image=self.icon_image, compound=tk.LEFT if self.icon_image else tk.NONE,
            state=state, **kwargs)

        self.theme = theme
        self.default_bg = bg_color
        self.hover_bg = active_bg_color

        # For non-flat buttons, highlightthickness might not be needed or desired as much
        self.config(highlightbackground=theme.get("BTN_BORDER", theme["ACCENT"]), highlightthickness=0 if relief != "flat" else 1)


        if state == tk.NORMAL:
            self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg) if self.cget('state') == tk.NORMAL else None)
            self.bind("<Leave>", lambda e: self.config(bg=self.default_bg) if self.cget('state') == tk.NORMAL else None)
        elif state == tk.DISABLED:
            self.config(bg=kwargs.get('disabledbackground', theme.get("GROUP_BG", "#ECEFF1" if theme["BG"] == "#ECEFF1" else "#2C313A")),
                        fg=kwargs.get('disabledforeground', theme.get("NOTEBOOK_TAB_FG", "#AAB8C5")))


class DBLogger:
    def __init__(self, dbfile=None, tk_root=None):
        log_to_file_debug_globally("DBLogger __init__ started.")
        if dbfile is None:
            try:
                # Use Path for robust path creation
                base_dir = Path(sys.argv[0]).resolve().parent
                dbfile_path = base_dir / "operation_log.db"
                dbfile_path.parent.mkdir(parents=True, exist_ok=True)
                dbfile_path.touch(exist_ok=True) # Creates if not exists, updates timestamp
                dbfile = str(dbfile_path)
                log_to_file_debug_globally(f"DBLogger: DB file path set to: {dbfile}")
            except Exception as e_db_path1:
                log_to_file_debug_globally(f"DBLogger: Failed to create DB at primary path {dbfile}: {e_db_path1}", "WARNING")
                try:
                    user_dir = Path.home()
                    dbfile_fallback_path = user_dir / ".UltimatUnlockTool" / "operation_log.db"
                    dbfile_fallback_path.parent.mkdir(parents=True, exist_ok=True)
                    dbfile_fallback_path.touch(exist_ok=True)
                    dbfile = str(dbfile_fallback_path)
                    log_to_file_debug_globally(f"DBLogger: DB file path set to fallback: {dbfile}")
                except Exception as e_db_path2:
                    log_to_file_debug_globally(f"DBLogger: Failed to create DB at fallback path {dbfile_fallback_path}: {e_db_path2}", "ERROR")
                    dbfile = ":memory:"
                    log_to_file_debug_globally("DBLogger: Using in-memory database as last resort.")

        self.dbfile = dbfile
        self.tk_root = tk_root
        self.conn = None
        self.cursor = None

        try:
            self.conn = sqlite3.connect(self.dbfile, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 timestamp TEXT,
                                 tag TEXT,
                                 message TEXT)''')
            self.conn.commit()
            log_to_file_debug_globally("DBLogger: Database initialized/checked.")
        except Exception as e_db_init:
            log_to_file_debug_globally(f"DBLogger: Database initialization error: {e_db_init}", "ERROR")
            if self.conn:
                self.conn.close()
            self.conn = None
            self.cursor = None
        log_to_file_debug_globally("DBLogger __init__ finished.")

    def add(self, message, tag="info"):
        if not self.conn or not self.cursor:
            log_to_file_debug_globally(f"DBLogger: Cannot add log, database not initialized. Message: {message}", "WARNING")
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO logs (timestamp, tag, message) VALUES (?, ?, ?)",
                               (timestamp, tag, message))
            self.conn.commit()
        except Exception as e_add:
            log_to_file_debug_globally(f"DBLogger: Error adding log: {e_add}. Message: {message}", "ERROR")

    def search(self, term):
        if not self.conn or not self.cursor:
            log_to_file_debug_globally(f"DBLogger: Cannot search, database not initialized. Term: {term}", "WARNING")
            return []

        try:
            self.cursor.execute("SELECT timestamp, tag, message FROM logs WHERE message LIKE ? ORDER BY id DESC LIMIT 1000",
                               (f"%{term}%",))
            return self.cursor.fetchall()
        except Exception as e_search:
            log_to_file_debug_globally(f"DBLogger: Error searching logs: {e_search}. Term: {term}", "ERROR")
            return []

    def all(self, limit=1000):
        if not self.conn or not self.cursor:
            log_to_file_debug_globally("DBLogger: Cannot fetch all, database not initialized.", "WARNING")
            return []

        try:
            self.cursor.execute("SELECT timestamp, tag, message FROM logs ORDER BY id DESC LIMIT ?", (limit,))
            return self.cursor.fetchall()
        except Exception as e_all:
            log_to_file_debug_globally(f"DBLogger: Error fetching all logs: {e_all}", "ERROR")
            return []

    def close(self):
        if self.conn:
            try:
                self.conn.close()
                log_to_file_debug_globally("DBLogger: Database connection closed.")
            except Exception as e_close:
                log_to_file_debug_globally(f"DBLogger: Error closing database: {e_close}", "ERROR")

class TextContextMenu:
    def __init__(self, widget, tk_root, labels):
        self.widget = widget
        self.tk_root = tk_root
        self.labels = labels
        self.menu = tk.Menu(widget, tearoff=0)

        self.menu.add_command(label=self.labels.get("context_cut", "Cut"), command=self.cut)
        self.menu.add_command(label=self.labels.get("context_copy", "Copy"), command=self.copy)
        self.menu.add_command(label=self.labels.get("context_paste", "Paste"), command=self.paste)
        self.menu.add_separator()
        self.menu.add_command(label=self.labels.get("context_select_all", "Select All"), command=self.select_all)

        widget.bind("<Button-3>", self.show_menu)

    def show_menu(self, event):
        has_selection = False
        try:
            if self.widget.selection_get():
                has_selection = True
        except tk.TclError:
            has_selection = False

        is_editable = isinstance(self.widget, (tk.Entry, tk.Text)) and self.widget.cget('state') == tk.NORMAL
        self.menu.entryconfig(self.labels.get("context_cut", "Cut"), state=tk.NORMAL if has_selection and is_editable else tk.DISABLED)
        self.menu.entryconfig(self.labels.get("context_copy", "Copy"), state=tk.NORMAL if has_selection else tk.DISABLED)

        can_paste = False
        try:
            if self.tk_root.clipboard_get() and is_editable :
                can_paste = True
        except tk.TclError:
            can_paste = False
        self.menu.entryconfig(self.labels.get("context_paste", "Paste"), state=tk.NORMAL if can_paste else tk.DISABLED)

        has_text = False
        if isinstance(self.widget, tk.Text):
            if self.widget.get("1.0", tk.END).strip():
                has_text = True
        elif isinstance(self.widget, tk.Entry):
            if self.widget.get().strip():
                has_text = True

        self.menu.entryconfig(self.labels.get("context_select_all", "Select All"), state=tk.NORMAL if has_text else tk.DISABLED)

        self.menu.tk_popup(event.x_root, event.y_root)

    def cut(self):
        try:
            if self.widget.selection_get() and self.widget.cget('state') == tk.NORMAL:
                self.widget.event_generate("<<Cut>>")
        except tk.TclError:
            pass

    def copy(self):
        try:
            if self.widget.selection_get():
                self.widget.event_generate("<<Copy>>")
        except tk.TclError:
            pass

    def paste(self):
        try:
            if self.widget.cget('state') == tk.NORMAL:
                 self.widget.event_generate("<<Paste>>")
        except tk.TclError:
            pass

    def select_all(self):
        if isinstance(self.widget, tk.Text):
            self.widget.tag_add(tk.SEL, "1.0", tk.END)
            self.widget.mark_set(tk.INSERT, "1.0")
            self.widget.see(tk.INSERT)
        elif isinstance(self.widget, tk.Entry):
            self.widget.select_range(0, tk.END)
            self.widget.icursor(tk.END)
        return "break"


class ProgressBarManager(tk.Frame):
    def __init__(self, master, theme):
        super().__init__(master, bg=theme["BG"])
        self.var = tk.IntVar(value=0)
        progress_bar_color = theme.get("PROGRESS_BAR_BG", "#2ECC71")

        lightcolor = progress_bar_color
        darkcolor = theme.get("ACCENT2", DARK_BLUE_ACCENT2)
        troughcolor = theme.get("GROUP_BG", theme.get("BG", "#ECEFF1"))
        bordercolor = progress_bar_color

        thickness = 12

        self.pb = ttk.Progressbar(
            self,
            orient="horizontal",
            mode="indeterminate",
            variable=self.var,
            style="Green.Horizontal.TProgressbar"
        )
        self.running = False

        style = ttk.Style()
        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor=troughcolor,
            bordercolor=bordercolor,
            background=progress_bar_color,
            lightcolor=lightcolor,
            darkcolor=darkcolor,
            thickness=thickness
        )
        self.pb.pack(fill=tk.X, padx=10, pady=(2,5))

    def start(self):
        if not self.winfo_exists(): return
        if not self.running:
            self.pb.config(mode="indeterminate")
            self.pb.start(10)
            self.running = True

    def stop(self):
        if not self.winfo_exists(): return
        if self.running:
            self.pb.stop()
            self.running = False
        self.pb.config(mode="determinate")
        self.var.set(0)
        self.pb.update_idletasks()

    def set_value(self, percent):
        if not self.winfo_exists(): return
        if self.running:
            self.pb.stop()
            self.running = False
        self.pb.config(mode="determinate")
        self.var.set(max(0, min(100, int(percent))))
        self.pb.update_idletasks()


class LogPanel(tk.Frame):
    def __init__(self, master, theme, labels, db_logger=None, tk_root=None, app_controller=None):
        super().__init__(master, bg=theme["BG"])
        self.labels = labels
        self.theme = theme
        self.tk_root = tk_root
        self.app_controller = app_controller
        self.theme["lang_for_cancel"] = app_controller.lang if app_controller else "en" # Pass lang for cancel button text

        log_title_frame = tk.Frame(self, bg=theme["BG"])
        log_title_frame.pack(fill=tk.X, padx=6, pady=(8,2))
        tk.Label(log_title_frame, text=labels["log"], font=LABEL_FONT, bg=theme["BG"], fg=theme.get("FG", "#263238")).pack(side=tk.LEFT)

        self.text = tk.Text(self, height=20, font=LOG_FONT, state=tk.DISABLED,
                            bg=theme["LOG_BG"], fg=theme["LOG_FG_INFO"],
                            bd=1, relief="sunken", wrap=tk.WORD,
                            selectbackground=theme["ACCENT"], selectforeground=theme["BTN_FG"],
                            insertbackground=theme["FG"])
        self.text.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0,6))
        TextContextMenu(self.text, self.tk_root, self.labels)

        for tag_name, color_key in [("info", "LOG_FG_INFO"), ("success", "LOG_FG_SUCCESS"),
                                    ("error", "LOG_FG_ERROR"), ("fail", "LOG_FG_FAIL"),
                                    ("cmd", "LOG_FG_CMD"), ("warning", "LOG_FG_WARNING"),
                                    ("device_info_label", "FG"),
                                    ("device_info_value", "ACCENT")]:

            font_config = LOG_FONT
            if tag_name in ["success", "error", "fail"]:
                font_config = (LOG_FONT[0], LOG_FONT[1], "bold")
            if tag_name == "fail":
                font_config = (LOG_FONT[0], LOG_FONT[1], "bold")
            if tag_name == "device_info_label":
                 font_config = (LOG_FONT[0], LOG_FONT[1], "bold")

            self.text.tag_configure(tag_name, foreground=theme[color_key], font=font_config)

        self.db_logger = db_logger
        self.progress_bar = ProgressBarManager(self, theme)
        self.progress_bar.pack(fill=tk.X, padx=6)

        controls_frame = tk.Frame(self, bg=theme["BG"])
        controls_frame.pack(fill=tk.X, padx=6, pady=(6,10))

        self.cancel_button = ModernButton(controls_frame, labels.get("btn_cancel_operation", "Cancel Operation"),
                                           command=self.app_controller.action_cancel_operation if self.app_controller else None,
                                           theme=theme, width=20, height=1, icon_path=None, state=tk.DISABLED,
                                           bg=theme.get("GROUP_BG"), fg=theme.get("NOTEBOOK_TAB_FG")) # Default disabled colors
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 4))
        if self.app_controller:
            self.app_controller.set_cancel_button_reference(self.cancel_button)

    def clear_log(self):
        if not self.winfo_exists(): return
        def __clear():
            if not self.text.winfo_exists(): return
            self.text.config(state=tk.NORMAL)
            self.text.delete("1.0", tk.END)
            self.text.config(state=tk.DISABLED)

        if self.tk_root and hasattr(self.tk_root, 'after') and self.tk_root.winfo_exists():
            if threading.current_thread() is not threading.main_thread():
                self.tk_root.after(0, __clear)
            else:
                __clear()
        else:
            __clear()


    def log(self, message, tag="info", indent=0, include_timestamp=False):
        if not self.winfo_exists(): return

        def __log_to_widget():
            if not self.text.winfo_exists(): return
            self.text.config(state=tk.NORMAL)

            timestamp_prefix = f"[{datetime.now().strftime('%H:%M:%S')}] " if include_timestamp else ""

            prefix_map = {"cmd": "[CMD]", "success": "[OK]", "error": "[ERR]", "fail": "[FAIL]", "warning": "[WARN]", "info": "[INFO]"}
            log_prefix_tag = prefix_map.get(tag, "[LOG]")

            actual_log_prefix = ""
            if not tag.startswith("device_info_") and tag != "connect_server_success_tag":
                 actual_log_prefix = f"{log_prefix_tag} "

            indent_space = "  " * indent

            if message == self.labels.get("log_connect_server_success", "Connect to server...successful") and tag == "info":
                 full_log_message = f"{indent_space}{message}\n"
            else:
                 full_log_message = f"{timestamp_prefix}{indent_space}{actual_log_prefix}{message}\n"

            idx = self.text.index(tk.END + "-1c linestart")
            self.text.insert(tk.END, full_log_message)
            self.text.tag_add(tag, idx, f"{idx} + {len(full_log_message)-1}c")

            self.text.see(tk.END)
            self.text.config(state=tk.DISABLED)

            if self.db_logger: self.db_logger.add(message, tag)

        if self.tk_root and hasattr(self.tk_root, 'after') and self.tk_root.winfo_exists():
            if threading.current_thread() is not threading.main_thread():
                self.tk_root.after(0, __log_to_widget)
            else:
                __log_to_widget()
        else:
             __log_to_widget()

    def log_device_info_block(self, device_info_dict):
        if not self.winfo_exists() or not self.text.winfo_exists(): return

        self.text.config(state=tk.NORMAL)

        connect_msg = f"{self.labels.get('log_connect_server_success', 'Connect to server...successful')}\n"
        idx_connect = self.text.index(tk.END + "-1c linestart")
        self.text.insert(tk.END, connect_msg)
        self.text.tag_add("info", idx_connect, f"{idx_connect} + {len(connect_msg)-1}c")

        max_label_len = 0
        if device_info_dict:
            present_labels = [label for label, prop_key in DEVICE_INFO_PROPERTIES if label in device_info_dict]
            if present_labels:
                max_label_len = max(len(label) for label in present_labels) + 1

        for label_text, prop_key in DEVICE_INFO_PROPERTIES:
            value_text_original = device_info_dict.get(label_text, "N/A")
            value_text_display = value_text_original
            value_tag = "device_info_value"

            if label_text == "Root State":
                if value_text_original == "1": value_text_display = "No Root!"
                elif value_text_original == "0": value_text_display = "Rooted!"
                else: value_text_display = "Unknown"

                if "No Root!" in value_text_display: value_tag = "fail"
                elif "Rooted!" in value_text_display: value_tag = "success"

            formatted_label = f"{label_text}:".ljust(max_label_len if max_label_len > 0 else len(label_text) + 2)
            line_content = f"  {formatted_label} {value_text_display}\n"

            line_start_idx = self.text.index(tk.END + "-1c linestart")
            self.text.insert(tk.END, line_content)

            label_part_start = self.text.index(f"{line_start_idx} + 2c")
            label_part_end = self.text.index(f"{label_part_start} + {len(formatted_label)}c")
            self.text.tag_add("device_info_label", label_part_start, label_part_end)

            value_part_start = self.text.index(f"{label_part_end} + 1c")
            value_part_end = self.text.index(f"{value_part_start} + {len(value_text_display)}c")
            self.text.tag_add(value_tag, value_part_start, value_part_end)

        if self.text.winfo_exists():
            self.text.see(tk.END)
            self.text.config(state=tk.DISABLED)


class StatusBar(tk.Label):
    def __init__(self, master, theme, labels):
        super().__init__(master, anchor="w", font=("Segoe UI", 10),
                         bg=theme.get("STATUS_BAR_BG", theme["BG"]),
                         fg=theme.get("STATUS_BAR_FG", theme["ACCENT"]),
                         padx=10, pady=4)
        self.theme = theme
        self.labels = labels
        self._check_adb_after_id = None
        self.set_status(self.labels["adb_status_not_connected"], theme.get("LOG_FG_ERROR", "#F44336"))
        self._check_adb()

    def set_status(self, text, color):
        if self.winfo_exists(): self.config(text=text, fg=color)

    def _check_adb(self):
        def check_thread_func():
            stat = self.labels["adb_status_not_connected"]
            color = self.theme.get("LOG_FG_ERROR", "#F44336")
            device_id = None
            try:
                flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                out_state = subprocess.check_output(['adb', 'get-state'], stderr=subprocess.STDOUT, text=True, timeout=2, creationflags=flags)
                if "device" in out_state:
                    out_devices = subprocess.check_output(['adb', 'devices'], stderr=subprocess.STDOUT, text=True, timeout=2, creationflags=flags)
                    lines = out_devices.strip().split('\n')
                    if len(lines) > 1 and "List of devices attached" in lines[0]:
                        parts = lines[1].split('\t')
                        if len(parts) > 0 and parts[0].strip():
                            device_id = parts[0].strip()
                            stat = f"{self.labels['adb_status_connected']} ({self.labels.get('adb_status_device_id_prefix','ID: ')}{device_id})"
                    else: # Fallback if parsing devices fails but state is 'device'
                         stat = self.labels["adb_status_connected"]
                    color = self.theme.get("LOG_FG_SUCCESS", "#4CAF50")
            except Exception: pass

            if self.winfo_exists() and self.master.winfo_exists():
                 final_stat = stat
                 self.master.after(0, lambda s=final_stat, c=color, did=device_id: (
                     self.set_status(s, c),
                     self.master.master._update_top_adb_status_bar(s, c, did) if hasattr(self.master.master, '_update_top_adb_status_bar') else None
                 ))


            if self.winfo_exists():
                 self._check_adb_after_id = self.after(3000, self._check_adb) # Check more frequently

        threading.Thread(target=check_thread_func, daemon=True).start()

    def cancel_adb_check(self):
        if self._check_adb_after_id:
            self.after_cancel(self._check_adb_after_id)
            self._check_adb_after_id = None

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.parent = parent
        self.app_controller = app_controller
        self.labels = app_controller.labels

        self.title_text = self.labels.get("login_window_title", "Ultimat-Unlock V2.2.2")
        self.title(self.title_text)
        self.geometry("380x580")
        self.resizable(False, False)

        self.login_bg_color = "#3A3A3A"
        self.login_fg_color = "#FFFFFF"
        self.login_accent_color = "#00D100"
        self.login_entry_bg_color = "#4A4A4A"

        self.configure(bg=self.login_bg_color)
        self.protocol("WM_DELETE_WINDOW", self._on_closing_login)

        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        if parent_width < 50 or parent_height < 50: # If parent is withdrawn or minimized
             parent_width = self.parent.winfo_screenwidth()
             parent_height = self.parent.winfo_screenheight()
             parent_x = (parent_width // 2) - (self.parent.winfo_reqwidth() // 2) # Centered on screen
             parent_y = (parent_height // 2) - (self.parent.winfo_reqheight() // 2)


        x = parent_x + (parent_width // 2) - (380 // 2)
        y = parent_y + (parent_height // 2) - (580 // 2)
        self.geometry(f"+{max(0,x)}+{max(0,y)}") # Ensure not off-screen

        main_frame = tk.Frame(self, bg=self.login_bg_color, padx=30, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(main_frame, text=self.labels.get("login_main_title", "Ultimat-Unlock tool"),
                 font=("Segoe UI", 18, "bold"),
                 bg=self.login_bg_color, fg=self.login_fg_color, justify=tk.CENTER).pack(pady=(10,25))


        email_label_text = self.labels.get("email_or_username_label", "Email or Username:")
        tk.Label(main_frame, text=email_label_text, font=FONT, bg=self.login_bg_color, fg=self.login_fg_color).pack(anchor=tk.W)

        email_entry_frame = tk.Frame(main_frame, bg=self.login_bg_color)
        email_entry_frame.pack(fill=tk.X, pady=(2,0))
        app_images['user_icon_login'] = load_image("user_icon.png", size=(20,20))
        if app_images.get('user_icon_login'):
            tk.Label(email_entry_frame, image=app_images['user_icon_login'], bg=self.login_bg_color).pack(side=tk.LEFT, padx=(0,5), pady=(0,2))

        self.username_entry = tk.Entry(email_entry_frame, font=FONT,
                                       bg=self.login_entry_bg_color, fg=self.login_fg_color, insertbackground=self.login_fg_color,
                                       relief=tk.FLAT, bd=0)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, pady=(0,2))
        email_underline = tk.Frame(main_frame, height=2, bg=self.login_accent_color)
        email_underline.pack(fill=tk.X, pady=(0,10))
        TextContextMenu(self.username_entry, self, self.labels)

        password_label_text = self.labels.get("password_label", "Password:")
        tk.Label(main_frame, text=password_label_text, font=FONT, bg=self.login_bg_color, fg=self.login_fg_color).pack(anchor=tk.W, pady=(10,0))

        password_entry_frame = tk.Frame(main_frame, bg=self.login_bg_color)
        password_entry_frame.pack(fill=tk.X, pady=(2,0))
        app_images['lock_icon_login'] = load_image("lock_icon.png", size=(20,20))
        if app_images.get('lock_icon_login'):
            tk.Label(password_entry_frame, image=app_images['lock_icon_login'], bg=self.login_bg_color).pack(side=tk.LEFT, padx=(0,5), pady=(0,2))

        self.password_entry = tk.Entry(password_entry_frame, font=FONT, show="*",
                                       bg=self.login_entry_bg_color, fg=self.login_fg_color, insertbackground=self.login_fg_color,
                                       relief=tk.FLAT, bd=0)
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, pady=(0,2))
        self.password_entry.bind("<Return>", self._attempt_login)

        self.show_password_var = tk.BooleanVar(value=False)
        app_images['eye_slash_icon'] = load_image("eye_slash_icon.png", size=(20,20))
        app_images['eye_icon'] = load_image("eye_icon.png", size=(20,20))

        self.show_hide_btn = tk.Button(password_entry_frame, image=app_images.get('eye_slash_icon'),
                                        command=self._toggle_password_visibility,
                                        bg=self.login_entry_bg_color, relief=tk.FLAT, bd=0, activebackground=self.login_entry_bg_color, cursor="hand2")
        if app_images.get('eye_slash_icon'):
            self.show_hide_btn.pack(side=tk.RIGHT, padx=(5,0), pady=(0,2))
        password_underline = tk.Frame(main_frame, height=2, bg=self.login_accent_color)
        password_underline.pack(fill=tk.X, pady=(0,15))
        TextContextMenu(self.password_entry, self, self.labels)

        remember_me_frame = tk.Frame(main_frame, bg=self.login_bg_color)
        remember_me_frame.pack(fill=tk.X, pady=(0,15))
        self.remember_me_var = tk.BooleanVar()
        remember_me_check = tk.Checkbutton(remember_me_frame, text=self.labels.get("remember_me_label", "Remember Me"),
                                           variable=self.remember_me_var, font=FONT,
                                           bg=self.login_bg_color, fg=self.login_fg_color, selectcolor=self.login_entry_bg_color,
                                           activebackground=self.login_bg_color, activeforeground=self.login_fg_color,
                                           relief=tk.FLAT, highlightthickness=0, bd=0, anchor=tk.W, cursor="hand2")
        remember_me_check.pack(side=tk.LEFT)

        login_button_frame = tk.Frame(main_frame, bg=self.login_bg_color)
        login_button_frame.pack(fill=tk.X, pady=(5,20))
        login_btn_text = self.labels.get("login_button_text", "LOGIN")
        app_images['right_arrows_icon'] = load_image("right_arrows_icon.png", size=(24,24))

        self.login_button = tk.Button(
            login_button_frame,
            text=login_btn_text,
            font=(BTN_FONT[0], BTN_FONT[1]+1, "bold"),
            bg=self.login_accent_color, fg="#202020",
            activebackground="#00B000", activeforeground="#101010",
            relief=tk.FLAT, bd=0, cursor="hand2", command=self._attempt_login,
            padx=20, pady=10,
            image=app_images.get('right_arrows_icon'),
            compound=tk.LEFT if app_images.get('right_arrows_icon') else tk.NONE
        )
        if app_images.get('right_arrows_icon'):
             self.login_button.config(text="  " + login_btn_text)
        self.login_button.pack(fill=tk.X)

        bottom_links_frame = tk.Frame(main_frame, bg=self.login_bg_color)
        bottom_links_frame.pack(fill=tk.X, pady=(20,0))

        link_font = ("Segoe UI", 9)
        link_fg_color = "#BBBBBB"
        link_hover_color = "#FFFFFF"

        def create_link_label(parent, text_key, url, icon_name_key=None):
            label_text = self.labels.get(text_key, text_key.replace("_label","").capitalize())
            img = None
            if icon_name_key:
                icon_filename = f"{icon_name_key.replace('_login','')}.png" # Assumes icon filenames like 'website_icon.png'
                app_images[icon_name_key] = load_image(icon_filename, size=(16,16))
                img = app_images.get(icon_name_key)

            link_label = tk.Label(parent, text=label_text, font=link_font,
                                  bg=self.login_bg_color, fg=link_fg_color, cursor="hand2",
                                  image=img, compound=tk.LEFT if img else tk.NONE, padx= (3 if img else 0))
            link_label.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
            link_label.bind("<Enter>", lambda e: e.widget.config(fg=link_hover_color))
            link_label.bind("<Leave>", lambda e: e.widget.config(fg=link_fg_color))
            return link_label

        create_link_label(bottom_links_frame, "website_label", "http://ultimat-unlock.com", "website_icon_login").pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(bottom_links_frame, text="|", font=link_font, bg=self.login_bg_color, fg=link_fg_color).pack(side=tk.LEFT, padx=(0,8))
        create_link_label(bottom_links_frame, "support_label", "https://t.me/UltimatUnlock", "support_icon_login").pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(bottom_links_frame, text="|", font=link_font, bg=self.login_bg_color, fg=link_fg_color).pack(side=tk.LEFT, padx=(0,8))
        create_link_label(bottom_links_frame, "signup_label", "https://ultimat-unlock.com/register", "signup_icon_login").pack(side=tk.LEFT, padx=(0, 8))


        self.grab_set() # Make this window modal
        self.focus_set() # Set focus to this window
        self.username_entry.focus() # Set focus to username entry

    def _toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show="*")
            self.show_hide_btn.config(image=app_images.get('eye_slash_icon'))
            self.show_password_var.set(False)
        else:
            self.password_entry.config(show="")
            self.show_hide_btn.config(image=app_images.get('eye_icon'))
            self.show_password_var.set(True)

    def _attempt_login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == FIXED_USERNAME and password == FIXED_PASSWORD:
            log_to_file_debug_globally("Login successful.")
            self.destroy()
            self.app_controller.show_main_app()
        else:
            log_to_file_debug_globally("Login failed.")
            messagebox.showerror(self.labels.get("login_failed_title", "Login Failed"),
                                 self.labels.get("login_failed_message", "Invalid username or password."),
                                 parent=self) # Ensure messagebox is child of login window
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()

    def _on_closing_login(self):
        log_to_file_debug_globally("Login window closed by user. Exiting application.")
        self.parent.destroy() # This will terminate the main Tk instance

class AppController:
    def __init__(self):
        log_to_file_debug_globally("AppController __init__ started.")
        self.root = tk.Tk()

        # Attempt to load application icon
        app_icon_loaded = False
        app_icon_path_png = "logo.png"
        app_icon_path_ico = "logo.ico" # Common fallback

        app_images['app_icon'] = load_image(app_icon_path_png)
        if app_images.get('app_icon'):
            self.root.iconphoto(True, app_images['app_icon'])
            app_icon_loaded = True
        else:
            log_to_file_debug_globally(f"Failed to load {app_icon_path_png}. Attempting .ico.", "WARNING")
            try:
                # Construct path relative to script for .ico
                base_dir = Path(sys.argv[0]).resolve().parent
                ico_path = base_dir / "assets" / app_icon_path_ico
                if not ico_path.exists():
                    ico_path = base_dir / app_icon_path_ico # Fallback to script dir

                if ico_path.exists():
                    self.root.iconbitmap(str(ico_path))
                    app_icon_loaded = True
                    log_to_file_debug_globally(f"Window icon set from {ico_path}.", "INFO")
                else:
                    log_to_file_debug_globally(f"{ico_path} not found.", "WARNING")
            except Exception as e_ico:
                 log_to_file_debug_globally(f"Failed to set window icon from {app_icon_path_ico}: {e_ico}", "WARNING")
        
        if not app_icon_loaded:
            log_to_file_debug_globally("Application icon could not be loaded.", "WARNING")


        self.root.withdraw() # Hide main window until login is successful

        self.lang = "en"
        self.theme_mode = "light" # Default theme
        self.labels = get_labels(self.lang)
        self.theme = get_theme(self.theme_mode)

        self.main_app_window = None # Will hold the UltimateDeviceTool instance
        self.cancel_button_ref = None
        self.mtk_client_path = None # Will be set by UltimateDeviceTool

        # Preload some commonly used icons for buttons
        app_images['telegram_icon'] = load_image("telegram_icon.png", size=(18,18))
        app_images['telegram_icon_small'] = load_image("telegram_icon.png", size=(14,14))
        app_images['refresh_icon_small'] = load_image("refresh_icon.png", size=(14,14))
        app_images['browse_icon_small'] = load_image("browse_icon.png", size=(14,14)) # For MTK browse buttons


        self.login_window = LoginWindow(self.root, self) # Create and show login window
        log_to_file_debug_globally("LoginWindow instantiated.")

    def start(self):
        log_to_file_debug_globally("AppController start, entering root.mainloop().")
        self.root.mainloop()

    def show_main_app(self):
        log_to_file_debug_globally("show_main_app called.")
        self.root.deiconify() # Show the main root window
        first_time_showing_main_app = False
        if self.main_app_window is None:
            self.main_app_window = UltimateDeviceTool(master_tk_instance=self.root, app_controller=self)
            first_time_showing_main_app = True
            log_to_file_debug_globally("UltimateDeviceTool instantiated as main_app_window.")
        else: # If main window was somehow created then hidden (e.g. error then recovery)
            log_to_file_debug_globally("Main app window already exists, ensuring it is deiconified.", "INFO")
            if isinstance(self.main_app_window, UltimateDeviceTool) and self.main_app_window.winfo_exists():
                 self.main_app_window.master.deiconify() # Ensure master (root) is visible
            else: # Should not happen if main_app_window exists, but as a fallback
                 log_to_file_debug_globally("Main app window was None or destroyed, re-instantiating.", "WARNING")
                 self.main_app_window = UltimateDeviceTool(master_tk_instance=self.root, app_controller=self)
                 first_time_showing_main_app = True

        if first_time_showing_main_app:
            try:
                # Only open browser if explicitly intended and not on every show_main_app
                # This was previously unconditional.
                # webbrowser.open("https://ultimat-unlock.com/")
                # log_to_file_debug_globally("Website https://ultimat-unlock.com/ opened automatically.", "INFO")
                pass # Decided to remove auto-opening website on first launch for now.
            except Exception as e_web_auto:
                log_to_file_debug_globally(f"Failed to auto-open website: {e_web_auto}", "WARNING")


    def set_cancel_button_reference(self, button_widget):
        self.cancel_button_ref = button_widget

    def action_cancel_operation(self):
        if self.main_app_window:
            self.main_app_window.action_cancel_operation()
        else:
            log_to_file_debug_globally("Cancel action called but main_app_window not available.", "WARNING")


class UltimateDeviceTool(tk.Frame):
    def __init__(self, master_tk_instance, app_controller):
        log_to_file_debug_globally("UltimateDeviceTool __init__ started.")
        super().__init__(master_tk_instance)

        self.master = master_tk_instance
        self.app_controller = app_controller

        self.lang = self.app_controller.lang
        self.theme_mode = self.app_controller.theme_mode
        self.labels = get_labels(self.lang)
        self.theme = get_theme(self.theme_mode)
        self.theme["lang_for_cancel"] = self.lang # For ModernButton to access current lang

        app_images['title_logo'] = load_image("logo.png", size=(38, 38))

        self.db_logger = DBLogger(tk_root=self.master)
        log_to_file_debug_globally("Instance variables (lang, theme, db_logger) initialized.")

        self.master.title(self.labels["title"])
        self.master.geometry("1450x820")
        self.master.wm_minsize(1200, 750)
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)
        log_to_file_debug_globally("Window properties (title, geometry, minsize, protocol) set on master.")

        self.pack(fill=tk.BOTH, expand=True) # Pack the main frame into the root window

        self._setup_mtkclient_path() # Try to set up mtkclient path
        self.app_controller.mtk_client_path = self._check_mtkclient() # Check and store path

        self._apply_styles()
        self._build_ui()
        self.command_queue = queue.Queue()
        self.current_popen_process = None
        # Ensure after_id_process_command_queue is cancelled on close
        self.after_id_process_command_queue = self.after(100, self._process_command_queue)
        self.last_known_device_id = None
        log_to_file_debug_globally("UltimateDeviceTool __init__ finished successfully.")

    def _setup_mtkclient_path(self):
        """Adds ~/.local/bin to PATH if not already present, for mtkclient."""
        home_dir = str(Path.home())
        local_bin = os.path.join(home_dir, ".local", "bin")
        current_path = os.environ.get("PATH", "")
        if os.path.exists(local_bin) and local_bin not in current_path:
            os.environ["PATH"] = f"{local_bin}{os.pathsep}{current_path}"
            log_to_file_debug_globally(f"Added {local_bin} to PATH for mtkclient.")
            # For subprocess calls made from this process, this PATH change should be effective.

    def _check_mtkclient(self):
        """Checks if mtkclient is installed and returns its path."""
        mtk_exe = shutil.which("mtk")
        if mtk_exe:
            log_to_file_debug_globally(f"mtkclient found at: {mtk_exe}")
            return mtk_exe
        else:
            # Try common user local bin again, as shutil.which might not pick it up immediately
            # after PATH modification if the script was just started.
            home_dir = str(Path.home())
            local_bin_mtk = os.path.join(home_dir, ".local", "bin", "mtk") # Assuming 'mtk' is the executable name
            if os.name == 'nt': # On Windows, executables often have .exe
                local_bin_mtk_exe = os.path.join(home_dir, ".local", "bin", "mtk.exe")
                if os.path.exists(local_bin_mtk_exe) and os.access(local_bin_mtk_exe, os.X_OK):
                    log_to_file_debug_globally(f"mtkclient found at fallback: {local_bin_mtk_exe}")
                    return local_bin_mtk_exe
            # Check without .exe for Linux/macOS or if .exe wasn't found on Windows
            if os.path.exists(local_bin_mtk) and os.access(local_bin_mtk, os.X_OK):
                log_to_file_debug_globally(f"mtkclient found at fallback: {local_bin_mtk}")
                return local_bin_mtk

            log_to_file_debug_globally("mtkclient not found in PATH or common user bin.", "WARNING")
            return None

    def get_mtk_executable_path(self):
        """Public method to get the checked mtkclient path."""
        if self.app_controller.mtk_client_path:
            return self.app_controller.mtk_client_path
        else:
            # Re-check if it was not found initially, maybe user installed it.
            self._setup_mtkclient_path() # Ensure PATH is set up
            self.app_controller.mtk_client_path = self._check_mtkclient() # Re-check
            if not self.app_controller.mtk_client_path and self.winfo_exists():
                 messagebox.showwarning(
                    self.labels.get("mtk_client_not_found_title", "MTKClient Not Found"),
                    self.labels.get("mtk_client_not_found_msg", "mtkclient executable not found. Please ensure it is installed and in your system's PATH. MTK operations will not be available."),
                    parent=self.master
                )
            return self.app_controller.mtk_client_path

    def _apply_styles(self):
        log_to_file_debug_globally("Applying styles...")
        self.style = ttk.Style(self.master)
        try:
            # 'clam', 'alt', 'default', 'classic' are common. 'vista' on Windows.
            # Try a few common ones for better cross-platform appearance.
            available_themes = self.style.theme_names()
            if 'clam' in available_themes: self.style.theme_use('clam')
            elif 'vista' in available_themes and os.name == 'nt': self.style.theme_use('vista')
            elif 'aqua' in available_themes and sys.platform == 'darwin': self.style.theme_use('aqua')
            else: self.style.theme_use(self.style.theme_names()[0]) # Use the first available default
            log_to_file_debug_globally(f"Using Tk theme: {self.style.theme_use()}", "INFO")

        except tk.TclError:
            log_to_file_debug_globally("TclError setting theme. Default theme will be used.", "WARNING")

        self.style.configure("TNotebook", background=self.theme["BG"], borderwidth=0, tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab",
                             background=self.theme.get("NOTEBOOK_TAB_BG", self.theme["GROUP_BG"]),
                             foreground=self.theme.get("NOTEBOOK_TAB_FG", self.theme["FG"]),
                             padding=[12, 6], font=("Segoe UI", 10, "bold"), borderwidth=1, # Increased padding, font, border for "inflated" tabs
                             relief="raised") # Raised relief for tabs
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.theme.get("NOTEBOOK_TAB_SELECTED_BG", self.theme["ACCENT"])),
                                   ("active", self.theme.get("NOTEBOOK_TAB_ACTIVE_BG", self.theme["ACCENT2"]))],
                       foreground=[("selected", self.theme.get("NOTEBOOK_TAB_SELECTED_FG", self.theme["BTN_FG"]))],
                       relief=[("selected", "sunken")]) # Sunken relief for selected tab

        self.style.configure("TPanedwindow", background=self.theme["BG"])
        self.style.configure("TFrame", background=self.theme["BG"]) # Ensure all ttk.Frames get themed
        log_to_file_debug_globally("Styles applied.")

    def _build_ui(self):
        log_to_file_debug_globally("Building UI...")
        self.config(bg=self.theme["BG"]) # Configure the main UltimateDeviceTool frame

        menubar = tk.Menu(self.master, bg=self.theme["BG"], fg=self.theme["FG"], relief=tk.FLAT, bd=0, activebackground=self.theme["ACCENT"], activeforeground=self.theme["BTN_FG"])
        theme_menu = tk.Menu(menubar, tearoff=0, bg=self.theme["GROUP_BG"], fg=self.theme["FG"], relief=tk.FLAT, activebackground=self.theme["ACCENT"], activeforeground=self.theme["BTN_FG"])
        theme_menu.add_command(label=self.labels["light"], command=lambda: self.set_theme("light"))
        theme_menu.add_command(label=self.labels["dark"], command=lambda: self.set_theme("dark"))
        theme_menu.add_command(label=self.labels["professional_dark"], command=lambda: self.set_theme("professional_dark"))
        menubar.add_cascade(label=self.labels["theme"], menu=theme_menu)

        lang_menu = tk.Menu(menubar, tearoff=0, bg=self.theme["GROUP_BG"], fg=self.theme["FG"], relief=tk.FLAT, activebackground=self.theme["ACCENT"], activeforeground=self.theme["BTN_FG"])
        lang_menu.add_command(label=LABELS["en"]["english"], command=lambda: self.set_language("en"))
        lang_menu.add_command(label=LABELS["ar"]["arabic"], command=lambda: self.set_language("ar"))
        menubar.add_cascade(label=self.labels["lang"], menu=lang_menu)
        self.master.config(menu=menubar)

        self.status_bar = StatusBar(self, self.theme, self.labels) # self is the UltimateDeviceTool frame

        bottom_buttons_frame = tk.Frame(self, bg=self.theme["BG"]) # self is the UltimateDeviceTool frame

        green_button_bg = "#00B050"
        green_button_fg = "#FFFFFF"
        green_button_active_bg = "#008C40"

        ModernButton(bottom_buttons_frame, text=self.labels.get("btn_telegram_channel", "Telegram Channel"),
                     command=lambda: webbrowser.open("https://t.me/UltimatUnlock1"),
                     theme=self.theme, width=20, icon_path="telegram_icon.png", icon_size=(16,16),
                     font=("Segoe UI", 9, "bold"),
                     bg=green_button_bg, fg=green_button_fg, activebackground=green_button_active_bg, activeforeground=green_button_fg,
                     relief="raised", borderwidth=2, padx=6, pady=3
                     ).pack(side=tk.LEFT, padx=(10,5), pady=2)

        ModernButton(bottom_buttons_frame, text=self.labels.get("btn_contact_support", "Contact Support"),
                     command=lambda: webbrowser.open("https://t.me/UltimatUnlock"),
                     theme=self.theme, width=20, icon_path="telegram_icon.png", icon_size=(16,16),
                     font=("Segoe UI", 9, "bold"),
                     bg=green_button_bg, fg=green_button_fg, activebackground=green_button_active_bg, activeforeground=green_button_fg,
                     relief="raised", borderwidth=2, padx=6, pady=3
                     ).pack(side=tk.LEFT, padx=5, pady=2)

        ModernButton(bottom_buttons_frame, text=self.labels.get("btn_group_support", "Group Support"),
                     command=lambda: webbrowser.open("https://t.me/SYRIANUNLOCKER1"),
                     theme=self.theme, width=20, icon_path="telegram_icon.png", icon_size=(16,16),
                     font=("Segoe UI", 9, "bold"),
                     bg=green_button_bg, fg=green_button_fg, activebackground=green_button_active_bg, activeforeground=green_button_fg,
                     relief="raised", borderwidth=2, padx=6, pady=3
                     ).pack(side=tk.LEFT, padx=5, pady=2)


        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,2), padx=0)


        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL, style="TPanedwindow") # self is UltimateDeviceTool
        body.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Use ttk.Frame for children of ttk.PanedWindow if possible, or ensure tk.Frame bg matches
        left_area_container = tk.Frame(body, bg=self.theme["BG"]) # Using tk.Frame, ensure BG is set
        right_area_container = tk.Frame(body, bg=self.theme["BG"])

        body.add(left_area_container, weight=3)
        body.add(right_area_container, weight=1)

        def set_sash_position_after_delay():
            try:
                self.master.update_idletasks() # Ensure window dimensions are current
                total_width = body.winfo_width()
                if total_width > 1: # Ensure width is valid
                    sash_pos = int(total_width * 0.72)
                    min_right_width = 300 # Minimum width for the log panel
                    # Ensure right pane is not too small
                    if total_width - sash_pos < min_right_width:
                        sash_pos = total_width - min_right_width
                    
                    if sash_pos > 50: # Ensure sash position is reasonable
                        body.sashpos(0, sash_pos)
                        log_to_file_debug_globally(f"PanedWindow sash set to {sash_pos} (total: {total_width})")
                    else:
                        log_to_file_debug_globally(f"Calculated sash position {sash_pos} too small or total_width too small, not setting.", "WARNING")
                else:
                    log_to_file_debug_globally("PanedWindow total_width is not > 1 for sash setting. Retrying.", "WARNING")
                    # Retry if width wasn't ready
                    self.master.after(200, set_sash_position_after_delay)
            except tk.TclError as e:
                log_to_file_debug_globally(f"TclError setting sash position: {e}. May occur if window not fully ready.", "WARNING")
            except Exception as e_sash_generic:
                log_to_file_debug_globally(f"Generic error setting sash position: {e_sash_generic}", "ERROR")

        self.master.after(150, set_sash_position_after_delay) # Delay to allow window to draw


        header_frame = tk.Frame(left_area_container, bg=self.theme["BG"])
        header_frame.pack(fill=tk.X, pady=(10, 5), padx=(15,0))

        if app_images.get('title_logo'):
            logo_label = tk.Label(header_frame, image=app_images['title_logo'], bg=self.theme["BG"])
            # logo_label.image = app_images['title_logo'] # Not needed, image= handles it
            logo_label.pack(side=tk.LEFT, padx=(0,10), pady=0)

        title_text_frame = tk.Frame(header_frame, bg=self.theme["BG"])
        title_text_frame.pack(side=tk.LEFT, anchor=tk.W, pady=0)
        tk.Label(title_text_frame, text=self.labels["title"], font=APP_LOGO_TITLE_FONT, bg=self.theme["BG"], fg=self.theme.get("TITLE_FG", self.theme["ACCENT"]) ).pack(anchor=tk.NW)
        tk.Label(title_text_frame, text=self.labels["edition"], font=SUBTITLE_FONT, bg=self.theme["BG"], fg=self.theme.get("EDITION_FG", self.theme["FG"]) ).pack(anchor=tk.NW)

        self.adb_status_bar_top = tk.Frame(left_area_container, bg=self.theme.get("DEVICE_STATUS_BG", self.theme["GROUP_BG"]), relief="groove", bd=1)
        self.adb_status_bar_top.pack(fill=tk.X, padx=15, pady=(5,10))

        self.adb_status_label_top_var = tk.StringVar(value=self.labels.get("adb_status_not_connected", "ADB: Not Connected"))
        self.adb_status_label_top_widget = tk.Label(self.adb_status_bar_top, textvariable=self.adb_status_label_top_var,
                                              font=DEVICE_STATUS_FONT_LABEL,
                                              bg=self.theme.get("DEVICE_STATUS_BG", self.theme["GROUP_BG"]),
                                              fg=self.theme.get("LOG_FG_ERROR", "#F44336"),
                                              padx=10, pady=5)
        self.adb_status_label_top_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.refresh_adb_top_button = ModernButton(self.adb_status_bar_top, text="", # Text set by icon
                                     command=self.action_refresh_adb_connection,
                                     theme=self.theme, width=3, height=1, # Small button
                                     icon_path="refresh_icon.png", icon_size=(14,14),
                                     relief="raised", borderwidth=1, padx=3, pady=1)
        self.refresh_adb_top_button.pack(side=tk.RIGHT, padx=(0,5), pady=2)


        self._update_top_adb_status_bar(self.labels.get("adb_status_not_connected"), self.theme.get("LOG_FG_ERROR"), None) # Initial update


        self.notebook = ttk.Notebook(left_area_container, style="TNotebook")
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=15, pady=(0,15))

        try:
            self.log_panel = LogPanel(right_area_container, self.theme, self.labels, db_logger=self.db_logger, tk_root=self.master, app_controller=self.app_controller)
            self.log_panel.pack(fill=tk.BOTH, expand=True, padx=(5,15), pady=(15,15)) # Adjusted padding
            log_to_file_debug_globally("Log panel created.")
        except Exception as e_log_panel:
            log_to_file_debug_globally(f"Error creating LogPanel: {e_log_panel}", "CRITICAL")
            log_to_file_debug_globally(traceback.format_exc(), "CRITICAL_TRACE")


        tabs_to_add = [
            (SamsungTab, "tab_samsung"),
            (HonorTab, "tab_honor"),
            (XiaomiTab, "tab_xiaomi"),
            (MTKTab, "tab_mtk"),      # Add MTKTab here
            (FileAdvancedTab, "tab_file_advanced"),
            (AppManagerTab, "tab_app_manager")
        ]

        for TabClass, label_key in tabs_to_add:
            try:
                tab_instance = TabClass(self.notebook, self)
                self.notebook.add(tab_instance, text=self.labels[label_key], padding=10)
                log_to_file_debug_globally(f"{TabClass.__name__} added to notebook.")
            except Exception as e_tab_creation:
                log_to_file_debug_globally(f"Error creating or adding {TabClass.__name__}: {e_tab_creation}", "ERROR")
                log_to_file_debug_globally(traceback.format_exc(), "ERROR_TRACE")
                messagebox.showerror("UI Build Error", f"Failed to build {self.labels[label_key]} tab: {e_tab_creation}", parent=self.master)

        log_to_file_debug_globally("UI Building finished.")

    def _update_top_adb_status_bar(self, status_text_from_bottom_bar, color_from_bottom_bar, device_id):
        if not self.winfo_exists() or not hasattr(self, 'adb_status_label_top_var') or not self.adb_status_label_top_widget.winfo_exists():
            return

        current_text = self.adb_status_label_top_var.get()
        new_text = self.labels.get("adb_status_not_connected") # Default
        new_color = self.theme.get("LOG_FG_ERROR") # Default

        if device_id: # If we have a device ID, it's connected
            new_text = f"{self.labels.get('adb_status_connected')} ({self.labels.get('adb_status_device_id_prefix', 'ID: ')}{device_id})"
            new_color = self.theme.get("LOG_FG_SUCCESS")
            self.last_known_device_id = device_id
        elif self.labels.get("adb_status_connected") in status_text_from_bottom_bar and not device_id and self.last_known_device_id:
            # If bottom bar says connected, but no new ID, use last known ID if available
            new_text = f"{self.labels.get('adb_status_connected')} ({self.labels.get('adb_status_device_id_prefix', 'ID: ')}{self.last_known_device_id})"
            new_color = self.theme.get("LOG_FG_SUCCESS")
        elif self.labels.get("adb_status_connected") in status_text_from_bottom_bar: # Connected but no ID available
            new_text = self.labels.get("adb_status_connected")
            new_color = self.theme.get("LOG_FG_SUCCESS")
            self.last_known_device_id = None # Clear last known ID if not provided
        else: # Not connected
            self.last_known_device_id = None


        if current_text != new_text or self.adb_status_label_top_widget.cget("fg") != new_color :
            self.adb_status_label_top_var.set(new_text)
            if self.adb_status_label_top_widget.winfo_exists():
                 self.adb_status_label_top_widget.config(fg=new_color)

        # The periodic update is now handled by the StatusBar's _check_adb calling this method.


    def action_refresh_adb_connection(self):
        if self.log_panel:
            self.log_panel.log("Attempting to refresh ADB connection (kill & start server)...", "info", include_timestamp=True)

        self.execute_command_async(
            ["adb", "kill-server"],
            operation_name="ADB Kill Server",
            callback_on_finish=self._adb_refresh_part2,
            is_part_of_sequence=True
        )

    def _adb_refresh_part2(self, result_kill):
        if result_kill.get("return_code") == 0 or "NotFoundError" in str(result_kill.get("error", "")): # Allow if server wasn't running
            if self.log_panel: self.log_panel.log("ADB server killed (or was not running). Starting server...", "info", indent=1, include_timestamp=False)
            self.execute_command_async(
                ["adb", "start-server"],
                operation_name="ADB Start Server",
                callback_on_finish=self._adb_refresh_finished,
                is_part_of_sequence=True
            )
        else:
            if self.log_panel: self.log_panel.log(f"Failed to kill ADB server: {result_kill.get('stderr','') or result_kill.get('error','')}", "error", indent=1, include_timestamp=False)
            self._adb_refresh_finished(result_kill) # Pass the error result

    def _adb_refresh_finished(self, result_start):
        if result_start.get("return_code") == 0:
            if self.log_panel: self.log_panel.log("ADB server started. Connection will be re-checked automatically.", "success", include_timestamp=True)
            # Trigger an immediate check by the main status bar, which will then call _update_top_adb_status_bar
            if hasattr(self, 'status_bar') and self.status_bar.winfo_exists():
                if self.status_bar._check_adb_after_id: self.status_bar.after_cancel(self.status_bar._check_adb_after_id)
                self.status_bar._check_adb()
        else:
            if self.log_panel: self.log_panel.log(f"Failed to start ADB server: {result_start.get('stderr','') or result_start.get('error','')}", "error", include_timestamp=True)

        if self.log_panel and self.log_panel.progress_bar.running: self.log_panel.progress_bar.stop()
        self._update_cancel_button_state(enable=False)



    def _build_device_status_widgets(self, parent_frame): # This method seems unused, _update_top_adb_status_bar is used instead
        self._update_top_adb_status_bar(self.labels.get("adb_status_not_connected"), self.theme.get("LOG_FG_ERROR"), None)


    def action_refresh_device_status(self, initial_load=False):
        if not initial_load and self.log_panel:
            self.log_panel.log("Refreshing ADB connection status...", "info", include_timestamp=False)

        # This call will get the latest status from the bottom bar and update the top one
        if hasattr(self, 'status_bar') and self.status_bar.winfo_exists():
            status_text = self.status_bar.cget("text")
            status_color = self.status_bar.cget("fg")
            # Try to extract device_id if present in status_text
            device_id_from_bottom = None
            prefix_len = len(self.labels.get('adb_status_device_id_prefix','ID: '))
            id_start_index = status_text.find(self.labels.get('adb_status_device_id_prefix','ID: '))
            if id_start_index != -1:
                id_val_start = id_start_index + prefix_len
                id_end_index = status_text.find(")", id_val_start)
                if id_end_index != -1:
                    device_id_from_bottom = status_text[id_val_start:id_end_index]

            self._update_top_adb_status_bar(status_text, status_color, device_id_from_bottom)



    def _update_cancel_button_state(self, enable=False):
        if self.app_controller and self.app_controller.cancel_button_ref:
            button = self.app_controller.cancel_button_ref
            if button.winfo_exists():
                 button.config(state=tk.NORMAL if enable else tk.DISABLED)
                 if enable:
                     button.config(bg=self.theme.get("CANCEL_BTN_BG_ACTIVE", CANCEL_BTN_RED_BG),
                                   fg=self.theme.get("CANCEL_BTN_FG_ACTIVE", CANCEL_BTN_RED_FG),
                                   activebackground=self.theme.get("CANCEL_BTN_HOVER_BG_ACTIVE", CANCEL_BTN_RED_ACTIVE_BG))
                 else: # Disabled state
                     button.config(bg=self.theme.get("GROUP_BG", "#ECEFF1" if self.theme["BG"] == "#ECEFF1" else "#2C313A"),
                                   fg=self.theme.get("NOTEBOOK_TAB_FG", "#AAB8C5"),
                                   activebackground=self.theme.get("GROUP_BG")) # Ensure hover matches disabled bg


    def execute_command_async(self, command_list, operation_name="Operation", callback_on_finish=None, is_part_of_sequence=False, is_info_gathering=False):
        log_panel_available = hasattr(self, 'log_panel') and self.log_panel is not None and self.log_panel.winfo_exists()

        if log_panel_available and not is_part_of_sequence and not is_info_gathering:
            self.log_panel.clear_log()
            self.log_panel.log(self.labels.get("log_operation_started", "Operation Started: ") + operation_name, "info", include_timestamp=True)
            self.log_panel.progress_bar.start()
            self._update_cancel_button_state(enable=True)

        command_str_for_debug = " ".join(map(str,command_list)) if isinstance(command_list, list) else str(command_list)
        if not is_info_gathering:
            log_to_file_debug_globally(f"Executing ASYNC ({operation_name}): {command_str_for_debug}", "DEBUG_CMD")

        def _command_thread():
            process = None
            try:
                startupinfo = None
                creation_flags = 0
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    creation_flags = subprocess.CREATE_NO_WINDOW


                process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           text=True, encoding='utf-8', errors='replace',
                                           startupinfo=startupinfo,
                                           creationflags=creation_flags)
                self.current_popen_process = process
                stdout, stderr = process.communicate(timeout=300) # Increased timeout for mtk operations
                return_code = process.returncode
                result_data = {"stdout": stdout, "stderr": stderr, "return_code": return_code,
                               "operation_name": operation_name, "command": command_list,
                               "callback": callback_on_finish, "is_part_of_sequence": is_part_of_sequence,
                               "is_info_gathering": is_info_gathering}
                self.command_queue.put(result_data)
            except subprocess.TimeoutExpired:
                if process: process.kill()
                log_to_file_debug_globally(f"Timeout for {operation_name}: {command_str_for_debug}", "ERROR")
                self.command_queue.put({"error": "TimeoutExpired", "operation_name": operation_name, "command": command_list, "callback": callback_on_finish, "is_part_of_sequence": is_part_of_sequence, "is_info_gathering": is_info_gathering})
            except FileNotFoundError:
                log_to_file_debug_globally(f"FileNotFound for {operation_name}: {command_list[0]}", "ERROR")
                self.command_queue.put({"error": "FileNotFound", "command_name": command_list[0], "operation_name": operation_name, "command": command_list, "callback": callback_on_finish, "is_part_of_sequence": is_part_of_sequence, "is_info_gathering": is_info_gathering})
            except Exception as e:
                if process and process.returncode is not None and process.returncode < 0 : # Negative return codes might indicate termination
                     self.command_queue.put({"error": "Cancelled", "operation_name": operation_name, "command": command_list, "callback": callback_on_finish, "is_part_of_sequence": is_part_of_sequence, "is_info_gathering": is_info_gathering})
                else:
                     log_to_file_debug_globally(f"Exception for {operation_name} ({command_str_for_debug}): {e}", "ERROR")
                     log_to_file_debug_globally(traceback.format_exc(), "ERROR_TRACE")
                     self.command_queue.put({"error": str(e), "operation_name": operation_name, "command": command_list, "callback": callback_on_finish, "is_part_of_sequence": is_part_of_sequence, "is_info_gathering": is_info_gathering})
            finally:
                self.current_popen_process = None

        threading.Thread(target=_command_thread, daemon=True).start()

    def _process_command_queue(self):
        try:
            while not self.command_queue.empty():
                result = self.command_queue.get_nowait()
                self._handle_command_result(result)
        except queue.Empty: # Expected if queue is empty
            pass
        except Exception as e:
            log_to_file_debug_globally(f"Error in _process_command_queue: {e}", "ERROR")
            log_to_file_debug_globally(traceback.format_exc(), "ERROR_TRACE")
        finally:
            if self.winfo_exists(): # Ensure widget still exists before scheduling next call
                self.after_id_process_command_queue = self.after(100, self._process_command_queue)


    def _handle_command_result(self, result):
        log_panel_available = hasattr(self, 'log_panel') and self.log_panel is not None and self.log_panel.winfo_exists()
        # Use a local log_method to avoid repeated checks; default to global logger if panel not ready
        if log_panel_available:
            log_method = self.log_panel.log
        else:
            def fallback_logger(msg, tag="info", **kwargs): # Match signature of LogPanel.log
                log_to_file_debug_globally(f"[{tag.upper()}] {msg}", "LOG_PANEL_UNAVAILABLE")
            log_method = fallback_logger


        operation_name = result.get("operation_name", "Unknown Operation")
        is_part_of_sequence = result.get("is_part_of_sequence", False)
        is_info_gathering = result.get("is_info_gathering", False)

        if is_info_gathering and "error" not in result and result.get("return_code") == 0:
            # For info gathering, typically no direct logging to UI unless it's the final display step
            pass
        elif is_part_of_sequence:
            # Logging for steps within a sequence (more concise)
            if "error" in result:
                log_method(f"Step Error ({operation_name}): {result['error']}", "error", indent=1, include_timestamp=False)
            elif result.get("return_code", -1) != 0:
                stderr = result.get("stderr", "").strip()
                stdout = result.get("stdout", "").strip()
                details = stderr if stderr else stdout
                first_line_details = details.splitlines()[0] if details else 'Unknown reason'
                log_method(f"Step Failed ({operation_name}): {first_line_details}", "error", indent=1, include_timestamp=False)
            else: # Successful step in a sequence
                stdout = result.get("stdout", "").strip()
                # For mtkclient, stdout can be verbose. Log only if not too long or contains key info.
                if stdout and not any(kw in stdout.lower() for kw in ["success", "already", "performed", "daemon started successfully", "waiting for brom...", "payload sent successfully"]):
                     summary_stdout = stdout.strip().splitlines()[0]
                     if len(summary_stdout) > 100: summary_stdout = summary_stdout[:100] + "..."
                     log_method(f"Step OK: {summary_stdout}", "info", indent=1, include_timestamp=False)
                elif not stdout: # If stdout is empty, still log a generic OK for the step
                     log_method(f"Step OK ({operation_name})", "info", indent=1, include_timestamp=False)
        else: # Logging for standalone operations (more detailed)
            if "error" in result:
                error_type = result["error"]
                error_message_summary = ""
                if error_type == "TimeoutExpired": error_message_summary = "Operation timed out"
                elif error_type == "FileNotFound": error_message_summary = f"Command '{result.get('command_name', 'N/A')}' not found. Ensure ADB/Fastboot/mtkclient is in PATH."
                elif error_type == "Cancelled": error_message_summary = "Operation cancelled by user"
                else: error_message_summary = f"Error - {error_type}"
                log_method(f"{operation_name}: {error_message_summary}", "error", include_timestamp=True)
            else:
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                return_code = result.get("return_code", -1)

                if not operation_name.startswith("Get Property"): # Avoid spamming for getprop
                    if return_code == 0:
                        log_method(f"{operation_name}: Completed successfully.", "success", include_timestamp=True)
                        if stdout.strip() and not any(kw in stdout.lower() for kw in ["success", "already", "performed", "daemon started successfully", "waiting for brom...", "payload sent successfully"]):
                            log_method("Output (stdout):", "info", indent=1, include_timestamp=False)
                            for line_idx, line_content in enumerate(stdout.strip().splitlines()):
                                if line_idx < 15: # Limit lines
                                    log_method(line_content, "info", indent=2, include_timestamp=False)
                                elif line_idx == 15:
                                    log_method("... (further output truncated in summary)", "info", indent=2)
                                    break
                        if stderr.strip(): # Log stderr even on success for mtkclient, as it might contain warnings
                            log_method("Output (stderr):", "warning", indent=1, include_timestamp=False)
                            for line_idx, line_content in enumerate(stderr.strip().splitlines()):
                                if line_idx < 10:
                                    log_method(line_content, "warning", indent=2, include_timestamp=False)
                                elif line_idx == 10:
                                    log_method("... (further stderr truncated)", "warning", indent=2)
                                    break
                    else:
                        log_method(f"{operation_name}: Failed (Code: {return_code}).", "fail", include_timestamp=True)
                        details = stderr.strip() if stderr.strip() else stdout.strip()
                        if details:
                            log_method("Error Details:", "error", indent=1, include_timestamp=False)
                            for line_idx, line_content in enumerate(details.strip().splitlines()):
                                if line_idx < 20: # Limit error detail lines
                                    log_method(line_content, "error", indent=2, include_timestamp=False)
                                elif line_idx == 20:
                                    log_method("... (further error details truncated)", "error", indent=2)
                                    break
                        else:
                            log_method("No specific error message from command.", "error", indent=1, include_timestamp=False)

        # Stop progress bar and disable cancel button ONLY if it's NOT part of a sequence AND NOT info gathering
        if log_panel_available and not is_part_of_sequence and not is_info_gathering:
            if self.log_panel.progress_bar.running: self.log_panel.progress_bar.stop()
            self._update_cancel_button_state(enable=False)

        callback = result.get("callback")
        if callback and callable(callback):
            try:
                callback(result)
            except Exception as e_callback:
                log_to_file_debug_globally(f"Error in command callback for {operation_name}: {e_callback}", "ERROR")
                log_to_file_debug_globally(traceback.format_exc(), "ERROR_TRACE")


    def action_cancel_operation(self):
        if not messagebox.askokcancel(
            self.labels.get("cancel_operation_warning_title", "Cancel Operation Warning"),
            self.labels.get("cancel_operation_warning_message", "Stopping an operation abruptly might affect the device. Are you sure?"),
            icon=messagebox.WARNING,
            parent=self.master):
            if self.log_panel: self.log_panel.log("Operation cancellation aborted by user.", "info", include_timestamp=False)
            return

        if self.current_popen_process and self.current_popen_process.poll() is None:
            try:
                self.current_popen_process.terminate() # Terminate the process
                # Note: The _command_thread will handle the "Cancelled" error state
                log_msg = "Attempting to cancel current operation..."
                if hasattr(self, 'log_panel') and self.log_panel and self.log_panel.winfo_exists():
                    self.log_panel.log(log_msg, "warning", include_timestamp=False)
                else:
                    log_to_file_debug_globally(log_msg, "WARNING")
            except Exception as e:
                log_msg = f"Error during cancellation attempt: {e}"
                if hasattr(self, 'log_panel') and self.log_panel and self.log_panel.winfo_exists():
                    self.log_panel.log(log_msg, "error", include_timestamp=True)
                else:
                    log_to_file_debug_globally(log_msg, "ERROR")
        else:
            log_msg = "No operation currently running to cancel, or process already finished."
            if hasattr(self, 'log_panel') and self.log_panel and self.log_panel.winfo_exists():
                self.log_panel.log(log_msg, "info", include_timestamp=False)
            else:
                log_to_file_debug_globally(log_msg, "INFO")
            # Ensure cancel button is disabled if no active process
            self._update_cancel_button_state(enable=False)


    def fetch_and_log_device_info(self, operation_label_key_on_success, callback_after_info_and_op=None, next_operation_command=None, next_operation_name=""):
        log_panel_available = hasattr(self, 'log_panel') and self.log_panel is not None and self.log_panel.winfo_exists()

        current_main_op_name = next_operation_name if next_operation_command else self.labels.get("btn_get_detailed_info", "Read Device Info (ADB)")

        if log_panel_available:
            self.log_panel.clear_log()
            self.log_panel.log(self.labels.get("log_operation_started", "Operation Started: ") + current_main_op_name, "info", include_timestamp=True)
            self.log_panel.progress_bar.start()
            self._update_cancel_button_state(enable=True)

        collected_props_display_keys = {}

        def _after_all_props_fetched_for_operation(final_props_dict_internal_keys):
            nonlocal collected_props_display_keys
            temp_display_dict = {}
            for display_label, internal_key in DEVICE_INFO_PROPERTIES:
                temp_display_dict[display_label] = final_props_dict_internal_keys.get(internal_key, "N/A")
            collected_props_display_keys = temp_display_dict


            if log_panel_available:
                self.log_panel.log_device_info_block(collected_props_display_keys)

            if next_operation_command:
                if log_panel_available:
                     self.log_panel.log(self.labels.get("log_operation_started", "Operation Started: ") + next_operation_name, "info", indent=1, include_timestamp=True)

                self.execute_command_async(
                    next_operation_command,
                    operation_name=next_operation_name,
                    callback_on_finish=_after_next_operation_completed,
                    is_part_of_sequence=False # The main operation is not part of a sequence
                )
            else: # No next_operation_command, so this was just info gathering
                if log_panel_available:
                    self.log_panel.log(self.labels.get(operation_label_key_on_success, "Operation successful."), "success", include_timestamp=True)
                    if self.log_panel.progress_bar.running: self.log_panel.progress_bar.stop()
                    self._update_cancel_button_state(enable=False)
                if callback_after_info_and_op:
                    callback_after_info_and_op({"return_code": 0, "device_info": collected_props_display_keys})

        def _after_next_operation_completed(result):
            # This callback is for the 'next_operation_command' if it was provided
            # The progress bar and cancel button for this 'next_operation_command'
            # are handled by the main _handle_command_result because it's marked as not is_part_of_sequence.
            if callback_after_info_and_op:
                callback_after_info_and_op({"return_code": result.get("return_code", -1),
                                            "device_info": collected_props_display_keys,
                                            "operation_result": result})


        self.get_detailed_adb_info_props(callback_after_all_props=_after_all_props_fetched_for_operation)


    def get_detailed_adb_info_props(self, callback_after_all_props=None):
        collected_props_internal_keys = {}
        # Use a list for remaining_props_count to modify it within nested functions (Python 2 workaround, good practice)
        remaining_props_count_list = [len(DEVICE_INFO_PROPERTIES)]


        def _after_single_prop_fetch(result_single_prop):
            prop_key_fetched = "unknown_prop"
            # Extract the property key from the command in the result
            if result_single_prop.get("command") and len(result_single_prop["command"]) >= 4 and result_single_prop["command"][2] == "getprop":
                prop_key_fetched = result_single_prop["command"][3]

            if result_single_prop.get("return_code") == 0:
                stdout_val = result_single_prop.get("stdout", "").strip()
                collected_props_internal_keys[prop_key_fetched] = stdout_val if stdout_val else "" # Store empty if prop exists but no value
            else:
                collected_props_internal_keys[prop_key_fetched] = "Error fetching" # Or "N/A"

            remaining_props_count_list[0] -= 1

            if remaining_props_count_list[0] <= 0:
                if callback_after_all_props and callable(callback_after_all_props):
                    callback_after_all_props(collected_props_internal_keys)

        if not DEVICE_INFO_PROPERTIES: # Handle empty list case
            if callback_after_all_props and callable(callback_after_all_props):
                callback_after_all_props({})
            return

        for _, prop_to_fetch_key in DEVICE_INFO_PROPERTIES:
            self.execute_command_async(
                ["adb", "shell", "getprop", prop_to_fetch_key],
                operation_name=f"Get Property ({prop_to_fetch_key})", # For debugging logs
                callback_on_finish=_after_single_prop_fetch,
                is_part_of_sequence=True, # These are sub-steps of fetching all info
                is_info_gathering=True # Prevents verbose logging for each getprop
            )


    def set_language(self, lang):
        if lang in LABELS:
            self.app_controller.lang = lang
            self.lang = lang
            self.labels = get_labels(self.lang)
            self.theme["lang_for_cancel"] = lang # Update for ModernButton
            self._rebuild_ui()
            log_to_file_debug_globally(f"Language changed to {lang}.")
        else:
            log_to_file_debug_globally(f"Language {lang} not supported.", "WARNING")

    def set_theme(self, theme_name):
        if theme_name in THEMES:
            self.app_controller.theme_mode = theme_name
            self.theme_mode = theme_name
            self.theme = get_theme(theme_name)
            self.theme["lang_for_cancel"] = self.lang # Ensure lang is in theme for ModernButton
            self._rebuild_ui()
            log_to_file_debug_globally(f"Theme changed to {theme_name}.")
        else:
            log_to_file_debug_globally(f"Theme {theme_name} not supported.", "WARNING")

    def _rebuild_ui(self):
        log_to_file_debug_globally("Rebuilding UI...")
        current_tab_index = 0
        if hasattr(self, 'notebook') and self.notebook.winfo_exists():
            try:
                current_tab_index = self.notebook.index(self.notebook.select())
            except tk.TclError: pass # No tab selected or notebook empty


        # Destroy direct children of self (UltimateDeviceTool frame)
        # This should include menubar (if set on self), status_bar, bottom_buttons_frame, body (PanedWindow)
        children_to_destroy = list(self.winfo_children())
        for widget in children_to_destroy:
            if widget.winfo_exists():
                 # Specific handling for menubar if it's directly configured on self.master
                if isinstance(widget, tk.Menu) and widget == self.master.cget("menu"):
                    self.master.config(menu=tk.Menu(self.master)) # Clear master's menu
                widget.destroy()

        # Re-initialize styles and build UI components
        self._apply_styles() # Apply styles first
        self._build_ui()     # Rebuild UI components

        if hasattr(self, 'notebook') and self.notebook.winfo_exists():
            try:
                if self.notebook.tabs(): # Check if notebook has any tabs
                    num_tabs = len(self.notebook.tabs())
                    if num_tabs > 0:
                         self.notebook.select(current_tab_index if current_tab_index < num_tabs else 0)
            except tk.TclError:
                log_to_file_debug_globally("Error selecting tab after UI rebuild, or no tabs exist.", "WARNING")

        self.action_refresh_device_status(initial_load=True) # Refresh ADB status

        log_to_file_debug_globally("UI Rebuilt.")

    def _on_closing(self):
        log_to_file_debug_globally("Application closing attempt.")
        if messagebox.askokcancel(self.labels.get("quit_dialog_title", "Quit"),
                                 self.labels.get("quit_dialog_message", "Do you want to quit?"),
                                 parent=self.master):
            if hasattr(self, 'status_bar') and self.status_bar.winfo_exists():
                self.status_bar.cancel_adb_check()
            if hasattr(self, 'db_logger') and self.db_logger:
                self.db_logger.close()

            if hasattr(self, 'after_id_process_command_queue') and self.after_id_process_command_queue:
                self.after_cancel(self.after_id_process_command_queue)
                self.after_id_process_command_queue = None

            log_to_file_debug_globally("Application closed by user.")
            self.master.destroy() # This will terminate the Tk main loop

class SamsungTab(ttk.Frame):
    def __init__(self, parent_notebook, master_app: UltimateDeviceTool):
        log_to_file_debug_globally("SamsungTab __init__ started.")
        super().__init__(parent_notebook, style="TFrame") # Ensure TFrame style is applied
        self.master_app = master_app
        self.labels = master_app.labels
        self.theme = master_app.theme
        self.config(bg=self.theme.get("BG", "#ECEFF1")) # Explicitly set background for the tab frame itself
        self.configure(padding=(15,15))


        self.num_frp_steps = 0
        self.current_frp_step = 0
        self.current_package_disable_step = 0
        self.num_package_disable_steps = 0
        self.package_list_for_disable = []


        # Use a tk.Frame as the direct child for consistent background
        container = tk.Frame(self, bg=self.theme.get("BG", "#ECEFF1"))
        container.pack(fill=tk.BOTH, expand=True)

        group_samsung = tk.LabelFrame(container, text=self.labels.get("group_samsung", "Samsung ADB Repair & Utilities"),
                                    font=LABEL_FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                                    fg=self.theme.get("FG", "#263238"), padx=15, pady=15, relief="groove", bd=2)
        group_samsung.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        col1_frame = tk.Frame(group_samsung, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        col1_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10), anchor=tk.N)

        ModernButton(col1_frame, text=self.labels.get("btn_get_detailed_info"),
                                   command=self.action_read_device_info, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(col1_frame, text=self.labels.get("btn_reboot_rec", "Reboot Recovery"),
                                       command=self.action_reboot_recovery, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(col1_frame, text=self.labels.get("btn_reboot_dl", "Reboot Download"),
                                       command=self.action_reboot_download, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(col1_frame, text=self.labels.get("btn_reboot_bl", "Reboot Bootloader"),
                                       command=self.action_reboot_bootloader, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(col1_frame, text=self.labels.get("btn_remove_mdm"),
                                   command=self.action_remove_mdm_adb, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)


        col2_frame = tk.Frame(group_samsung, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        col2_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10,0), anchor=tk.N)

        ModernButton(col2_frame, text=self.labels.get("btn_remove_frp", "Remove FRP (ADB)"),
                                       command=self.action_remove_frp_adb, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_factory_reset", "Factory Reset (ADB)"),
                                       command=self.action_factory_reset_adb, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_screenlock_reset", "Reset Screen Lock (ADB)"),
                                       command=self.action_reset_screenlock_adb, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_arabize_device", "Arabize Device (ADB)"),
                                       command=self.action_arabize_device, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_open_browser_adb", "Open Browser (ADB)"),
                                       command=self.action_open_browser_adb, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_bypass_knox"),
                                   command=self.action_bypass_knox_adb, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)

        log_to_file_debug_globally("SamsungTab __init__ finished.")

    def action_read_device_info(self):
        self.master_app.fetch_and_log_device_info(
            operation_label_key_on_success="log_read_info_complete",
            next_operation_name=self.labels.get("btn_get_detailed_info")
            )

    def action_reboot_recovery(self):
        command = ["adb", "reboot", "recovery"]
        self.master_app.execute_command_async(command, operation_name="Reboot to Recovery")

    def action_reboot_download(self):
        command = ["adb", "reboot", "download"]
        self.master_app.execute_command_async(command, operation_name="Reboot to Download Mode")

    def action_reboot_bootloader(self):
        command = ["adb", "reboot", "bootloader"]
        self.master_app.execute_command_async(command, operation_name="Reboot to Bootloader")

    def _start_package_disable_sequence(self, packages_to_disable, operation_name_key, success_log_key, failure_log_key):
        self.package_list_for_disable = packages_to_disable
        self.num_package_disable_steps = len(self.package_list_for_disable)
        self.current_package_disable_step = 0
        self.current_operation_success_log_key = success_log_key
        self.current_operation_failure_log_key = failure_log_key
        self.current_operation_name_key = operation_name_key


        if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
            # Clear log is handled by fetch_and_log_device_info if it's the entry point
            self.master_app.log_panel.log(self.labels.get(operation_name_key, "Starting package disable sequence..."), "info", include_timestamp=True)
            self.master_app.log_panel.progress_bar.set_value(0) # Start progress at 0
            # Cancel button state is handled by fetch_and_log_device_info or execute_command_async

        self._execute_next_package_disable_step()

    def _execute_next_package_disable_step(self):
        if self.current_package_disable_step < self.num_package_disable_steps:
            package_name = self.package_list_for_disable[self.current_package_disable_step]
            op_desc = f"Disable Pkg: {package_name}"

            if self.master_app.log_panel:
                self.master_app.log_panel.log(f"Attempting: {op_desc}", "info", indent=1, include_timestamp=False)

            self.master_app.execute_command_async(
                ["adb", "shell", "pm", "disable-user", "--user", "0", package_name],
                operation_name=op_desc,
                callback_on_finish=self._package_disable_step_callback,
                is_part_of_sequence=True
            )
        else: # All steps completed
            if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
                self.master_app.log_panel.log(self.labels.get(self.current_operation_success_log_key, "Package disable sequence attempted."), "success", include_timestamp=True)
                self.master_app.log_panel.progress_bar.set_value(100)
                # Stop progress bar and disable cancel button in the main handler for the *overall* operation
                # This else block is for the *sequence completion*, not the individual step.
                # The final state update (progress bar stop, cancel button) is handled by _handle_command_result
                # for the primary operation that initiated this sequence.
            # No need to call self.master_app._update_cancel_button_state(enable=False) here,
            # as the main operation's completion will handle it.


    def _package_disable_step_callback(self, result):
        # This callback is for an individual step *within* the sequence
        self.current_package_disable_step += 1
        is_last_step = (self.current_package_disable_step >= self.num_package_disable_steps)

        if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
            progress_percentage = int((self.current_package_disable_step / self.num_package_disable_steps) * 100)
            self.master_app.log_panel.progress_bar.set_value(progress_percentage)

        if result.get("error") == "Cancelled":
            if self.master_app.log_panel:
                self.master_app.log_panel.log("Package disable sequence cancelled by user.", "warning", include_timestamp=True)
            # Stop progress and disable cancel button will be handled by the main operation's _handle_command_result
            return # Stop further steps in the sequence

        # If not cancelled, proceed to next step or finalize
        self._execute_next_package_disable_step() # This will either do next or log completion


    def action_remove_mdm_adb(self):
        if not messagebox.askokcancel(
            self.labels.get("mdm_remove_warning_title"),
            self.labels.get("mdm_remove_warning_message"),
            icon=messagebox.WARNING,
            parent=self.master_app.master):
            if self.master_app.log_panel: self.master_app.log_panel.log("MDM Removal (ADB) cancelled by user.", "info", include_timestamp=True)
            return

        MDM_PACKAGES = [
            "com.samsung.android.knox.containeragent", "com.samsung.android.knox.enrollment",
            "com.android.managedprovisioning", "com.samsung.aasaservice",
            "com.samsung.android.mdm", "com.samsung.android.unifiedmdm",
            "com.samsung.android.knox.mdm.smdms", "com.google.android.apps.work.oobconfig",
            "com.samsung.android.knox.pushmanager", "com.samsung.android.knox.kcc",
            "com.samsung.android.knox.klmsagent", "com.samsung.android.knox.knoxsetupwizardclient",
            "com.samsung.android.da.daagent", "com.samsung.android.MdmEncryption",
            "com.samsung.android.bbc.bbcagent", "com.samsung.android.knox.sdp.service",
            "com.samsung.android.smdms"
        ]
        
        operation_name_display = self.labels.get("btn_remove_mdm")

        def _after_info_for_mdm(info_result):
            if info_result.get("return_code") == 0:
                self._start_package_disable_sequence(
                    MDM_PACKAGES,
                    "log_mdm_remove_start",
                    "log_mdm_remove_ok",
                    "log_mdm_remove_fail"
                )
            else:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log("Could not get device info before MDM removal. Aborting.", "error")
                    if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                self.master_app._update_cancel_button_state(enable=False)

        # Start the main operation which includes fetching info first
        self.master_app.fetch_and_log_device_info(
            operation_label_key_on_success="log_mdm_remove_ok", # This will be logged if no further sequence
            callback_after_info_and_op=_after_info_for_mdm,
            # No next_operation_command here, the sequence is handled by _after_info_for_mdm
            next_operation_name=operation_name_display
        )


    def action_bypass_knox_adb(self):
        if not messagebox.askokcancel(
            self.labels.get("knox_bypass_warning_title"),
            self.labels.get("knox_bypass_warning_message"),
            icon=messagebox.WARNING,
            parent=self.master_app.master):
            if self.master_app.log_panel: self.master_app.log_panel.log("Knox Bypass (ADB) cancelled by user.", "info", include_timestamp=True)
            return

        KNOX_PACKAGES = [
            "com.samsung.android.knox.attestation", "com.samsung.android.knox.containercore",
            "com.samsung.android.knox.containeragent", "com.samsung.android.knox.pushmanager",
            "com.sec.knox.switcher", "com.samsung.knox.keychain",
            "com.samsung.knox.securefolder", "com.samsung.android.knox.cloudmdm.smdms",
            "com.samsung.android.knox.kcc", "com.samsung.android.knox.license.service",
            "com.samsung.android.knox.klmsagent", "com.samsung.android.knox.knoxsetupwizardclient",
            "com.samsung.android.knox.securesettings", "com.samsung.android.bbc.bbcagent",
            "com.samsung.android.taprotect", "com.samsung.knox.securefolder.dispatcher",
            "com.samsung.android.knox.analytics.uploader", "com.samsung.android.knox.core",
            "com.samsung.android.knox.ebe.android", "com.samsung.android.knox.intentresolver",
            "com.samsung.android.knox.keystore", "com.samsung.android.knox.permission",
            "com.samsung.android.knox.profile", "com.samsung.android.knox.efs.service.proxy",
            "com.samsung.android.knox.efs.sync.proxy"
        ]
        
        operation_name_display = self.labels.get("btn_bypass_knox")

        def _after_info_for_knox(info_result):
            if info_result.get("return_code") == 0:
                self._start_package_disable_sequence(
                    KNOX_PACKAGES,
                    "log_knox_bypass_start",
                    "log_knox_bypass_ok",
                    "log_knox_bypass_fail"
                )
            else:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log("Could not get device info before Knox bypass. Aborting.", "error")
                    if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                self.master_app._update_cancel_button_state(enable=False)

        self.master_app.fetch_and_log_device_info(
            operation_label_key_on_success="log_knox_bypass_ok",
            callback_after_info_and_op=_after_info_for_knox,
            next_operation_name=operation_name_display
        )

    def action_remove_frp_adb(self):
        if not messagebox.askokcancel(
            self.labels.get("frp_reset_warning_title", "FRP Reset Attempt"),
            self.labels.get("frp_reset_warning_message", "This will attempt a series of ADB commands... Proceed with caution."),
            icon=messagebox.WARNING,
            parent=self.master_app.master):
            if self.master_app.log_panel: self.master_app.log_panel.log("FRP Reset (ADB) cancelled by user.", "info", include_timestamp=True)
            return
        
        operation_name_display = self.labels.get("btn_remove_frp")

        def _start_frp_sequence_after_info(info_result):
            if info_result.get("return_code") != 0:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log("Could not get complete device info before FRP reset. Aborting FRP.", "error", include_timestamp=True)
                # Progress bar and cancel button are handled by fetch_and_log_device_info's main logic
                return

            if self.master_app.log_panel:
                self.master_app.log_panel.log("Starting FRP Reset sequence (ADB)...", "info", indent=0, include_timestamp=True)

            self.commands_frp_sequence = [
                (["adb", "shell", "settings", "put", "global", "setup_wizard_has_run", "1"], "Set setup_wizard_has_run to 1"),
                (["adb", "shell", "settings", "put", "secure", "user_setup_complete", "1"], "Set user_setup_complete (secure table)"),
                (["adb", "shell", "settings", "put", "global", "device_provisioned", "1"], "Set device_provisioned to 1"),
                (["adb", "shell", "content", "insert", "--uri", "content://settings/secure", "--bind", "name:s:user_setup_complete", "--bind", "value:s:1"], "Insert user_setup_complete via content provider")
            ]
            self.num_frp_steps = len(self.commands_frp_sequence)
            self.current_frp_step = 0

            if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
                self.master_app.log_panel.progress_bar.set_value(0) # Reset progress for this sequence

            self._execute_next_frp_step()

        self.master_app.fetch_and_log_device_info(
            operation_label_key_on_success="log_frp_reset_ok", # Logged if sequence completes successfully
            callback_after_info_and_op=_start_frp_sequence_after_info,
            next_operation_name=operation_name_display
        )


    def _execute_next_frp_step(self):
        if self.current_frp_step < self.num_frp_steps:
            command, op_desc = self.commands_frp_sequence[self.current_frp_step]

            if self.master_app.log_panel: self.master_app.log_panel.log(f"Attempting FRP Step: {op_desc}", "info", indent=1, include_timestamp=False)

            self.master_app.execute_command_async(
                command,
                operation_name=f"FRP Step: {op_desc}",
                callback_on_finish=self._frp_step_callback,
                is_part_of_sequence=True # Mark as part of sequence
            )
        else: # All FRP steps completed
            if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
                self.master_app.log_panel.log(self.labels.get("log_frp_reset_ok", "FRP Reset.... OK"), "success", include_timestamp=True)
                self.master_app.log_panel.progress_bar.set_value(100)
            # The main operation (fetch_and_log_device_info) will handle stopping progress bar and cancel button
            # if _start_frp_sequence_after_info was its final callback.


    def _frp_step_callback(self, result):
        self.current_frp_step += 1
        is_last_step = (self.current_frp_step >= self.num_frp_steps)

        if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
            progress_percentage = int((self.current_frp_step / self.num_frp_steps) * 100)
            self.master_app.log_panel.progress_bar.set_value(progress_percentage)

        if result.get("error") == "Cancelled":
            if self.master_app.log_panel: self.master_app.log_panel.log("FRP sequence cancelled by user.", "warning", include_timestamp=True)
            # Let the main operation handler deal with stopping progress bar / cancel button
            return

        if result.get("return_code", 0) != 0 and result.get("error") is None: # Step failed but not due to cancellation
            if self.master_app.log_panel: self.master_app.log_panel.log(f"FRP step '{result.get('operation_name')}' may have failed. Continuing...", "warning", indent=1, include_timestamp=False)

        # Proceed to next step or finalize
        self._execute_next_frp_step()


    def action_factory_reset_adb(self):
        if messagebox.askyesno("Confirm Factory Reset", "Are you sure you want to factory reset the device via ADB? This will erase all user data.", parent=self.master_app.master):
            command = ["adb", "shell", "wipe", "data"]
            self.master_app.execute_command_async(command, operation_name="Factory Reset (ADB)")
            if self.master_app.log_panel: self.master_app.log_panel.log("Note: Factory Reset via 'adb shell wipe data' typically requires recovery mode or root. Effectiveness varies.", "warning", include_timestamp=False)
        else:
            if self.master_app.log_panel: self.master_app.log_panel.log("Factory Reset (ADB) cancelled by user.", "info", include_timestamp=True)

    def action_reset_screenlock_adb(self):
        if messagebox.askokcancel(
            self.labels.get("screen_lock_reset_warning_title", "Screen Lock Reset Attempt"),
            self.labels.get("screen_lock_reset_warning_message", "This attempts to remove screen lock files... Proceed with extreme caution."),
            icon=messagebox.WARNING,
            parent=self.master_app.master):

            op_name = "Reset Screen Lock (ADB)"
            if self.master_app.log_panel:
                self.master_app.log_panel.clear_log()
                self.master_app.log_panel.log(self.labels.get("log_operation_started") + op_name, "info", include_timestamp=True)
                self.master_app.log_panel.progress_bar.start()
            self.master_app._update_cancel_button_state(enable=True)

            commands_to_try = [
                (["adb", "shell", "rm", "/data/system/gesture.key"], "Remove gesture.key (requires root)"),
                (["adb", "shell", "rm", "/data/system/password.key"], "Remove password.key (requires root)"),
                (["adb", "shell", "locksettings", "clear", "--old", "1234"], "Attempt locksettings clear (Android 6+ if old PIN known, placeholder 1234)"),
            ]
            num_sl_steps = len(commands_to_try)
            current_sl_step_ref = [0] # Use a list to allow modification in nested function

            def _sl_callback_chained(result_of_step, next_step_idx):
                current_sl_step_ref[0] = next_step_idx
                if self.master_app.log_panel:
                    prog = int((current_sl_step_ref[0] / num_sl_steps) * 100)
                    self.master_app.log_panel.progress_bar.set_value(prog)

                if result_of_step.get("error") == "Cancelled":
                    if self.master_app.log_panel:
                        self.master_app.log_panel.log("Screen Lock Reset sequence cancelled.", "warning", include_timestamp=True)
                    # Final cleanup of progress bar/cancel button will be handled by _handle_command_result
                    # when the "Cancelled" error bubbles up from the execute_command_async call.
                    return

                if next_step_idx >= num_sl_steps: # All steps attempted
                    if self.master_app.log_panel:
                         if not result_of_step.get("error") == "Cancelled": # Only log success if not cancelled
                            self.master_app.log_panel.log("Attempted screen lock reset commands. Reboot device to check. Effectiveness highly varies.", "info", include_timestamp=True)
                    # Final cleanup of progress bar/cancel button for the overall operation
                    if self.master_app.log_panel and self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                    self.master_app._update_cancel_button_state(enable=False)
                else:
                    _execute_next_sl_step(next_step_idx)

            def _execute_next_sl_step(step_index):
                cmd, desc = commands_to_try[step_index]
                self.master_app.execute_command_async(
                    cmd,
                    operation_name=f"Reset SL: {desc}",
                    is_part_of_sequence=True, # Mark as part of sequence
                    callback_on_finish=lambda res: _sl_callback_chained(res, step_index + 1)
                )
            _execute_next_sl_step(0) # Start the sequence
        else:
            if self.master_app.log_panel: self.master_app.log_panel.log("Screen Lock Reset (ADB) cancelled by user.", "info", include_timestamp=True)

    def action_arabize_device(self):
        if messagebox.askyesno(
            self.labels.get("arabize_confirm_title", "Confirm Arabization"),
            self.labels.get("arabize_confirm_message", "This will attempt to change the device language to Arabic (ar-AE)... Proceed?"),
            parent=self.master_app.master):

            op_name = "Arabize Device (ADB)"
            if self.master_app.log_panel:
                self.master_app.log_panel.clear_log()
                self.master_app.log_panel.log(self.labels.get("log_operation_started") + op_name, "info", include_timestamp=True)
                self.master_app.log_panel.progress_bar.start()
            self.master_app._update_cancel_button_state(enable=True)

            locale_to_set = "ar-AE"
            arabize_commands = [
                (["adb", "shell", "settings", "put", "system", "system_locales", locale_to_set], f"Set system_locales to {locale_to_set}"),
                (["adb", "shell", "setprop", "persist.sys.locale", locale_to_set], f"Set persist.sys.locale to {locale_to_set}"),
                (["adb", "shell", "am", "broadcast", "-a", "android.intent.action.LOCALE_CHANGED"], "Broadcast Locale Change")
            ]
            num_arabize_steps = len(arabize_commands)
            current_arabize_step_ref = [0] # Use list for modification in nested scope

            def _arabize_callback_chained(result_arabize_step, next_idx_arabize):
                current_arabize_step_ref[0] = next_idx_arabize
                if self.master_app.log_panel:
                    prog = int((current_arabize_step_ref[0] / num_arabize_steps) * 100)
                    self.master_app.log_panel.progress_bar.set_value(prog)

                if result_arabize_step.get("error") == "Cancelled":
                    if self.master_app.log_panel:
                        self.master_app.log_panel.log("Arabization sequence cancelled.", "warning", include_timestamp=True)
                    return

                if next_idx_arabize >= num_arabize_steps:
                     if self.master_app.log_panel:
                        if not result_arabize_step.get("error") == "Cancelled":
                            self.master_app.log_panel.log("Arabization commands sent. Check device. A reboot might be needed. Effectiveness varies.", "success", include_timestamp=True)
                     if self.master_app.log_panel and self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                     self.master_app._update_cancel_button_state(enable=False)
                else:
                    _execute_next_arabize_step(next_idx_arabize)

            def _execute_next_arabize_step(step_idx_arabize):
                cmd_arabize, desc_arabize = arabize_commands[step_idx_arabize]
                self.master_app.execute_command_async(
                    cmd_arabize,
                    operation_name=desc_arabize,
                    is_part_of_sequence=True,
                    callback_on_finish=lambda res_arabize: _arabize_callback_chained(res_arabize, step_idx_arabize + 1)
                )
            _execute_next_arabize_step(0)
        else:
            if self.master_app.log_panel: self.master_app.log_panel.log("Arabization cancelled by user.", "info", include_timestamp=True)

    def action_open_browser_adb(self):
        url = simpledialog.askstring(
            self.labels.get("open_browser_title", "Open URL"),
            self.labels.get("open_browser_prompt", "Enter URL:"),
            parent=self.master_app.master
        )
        if url and url.strip():
            if not (url.startswith("http://") or url.startswith("https://")):
                messagebox.showwarning("Invalid URL", "Please enter a full URL including http:// or https://", parent=self.master_app.master)
                if self.master_app.log_panel: self.master_app.log_panel.log(f"Invalid URL for Open Browser: {url}", "warning", include_timestamp=False)
                return

            command = ["adb", "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url.strip()]
            self.master_app.execute_command_async(command, operation_name=f"Open URL: {url.strip()}")
        elif url is not None: # User pressed OK but field was empty
             messagebox.showwarning("Empty URL", "URL cannot be empty.", parent=self.master_app.master)
             if self.master_app.log_panel: self.master_app.log_panel.log("Open Browser: URL was empty.", "info", include_timestamp=False)
        else: # User pressed Cancel
            if self.master_app.log_panel: self.master_app.log_panel.log("Open Browser action cancelled by user.", "info", include_timestamp=True)


class HonorTab(ttk.Frame):
    def __init__(self, parent_notebook, master_app: UltimateDeviceTool):
        log_to_file_debug_globally("HonorTab __init__ started.")
        super().__init__(parent_notebook, style="TFrame")
        self.master_app = master_app
        self.labels = master_app.labels
        self.theme = master_app.theme
        self.config(bg=self.theme.get("BG", "#ECEFF1"))
        self.configure(padding=(15,15))

        container = tk.Frame(self, bg=self.theme.get("BG", "#ECEFF1"))
        container.pack(fill=tk.BOTH, expand=True)

        group_honor = tk.LabelFrame(container, text=self.labels.get("group_honor", "Honor Fastboot Tools"),
                                    font=LABEL_FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                                    fg=self.theme.get("FG", "#263238"), padx=10, pady=10, relief="groove", bd=2)
        group_honor.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        ModernButton(group_honor, text=self.labels.get("btn_honor_info", "Read Serial & Software Info"),
                                   command=self.action_honor_info, theme=self.theme, width=34).pack(pady=5, anchor=tk.W)
        ModernButton(group_honor, text=self.labels.get("btn_honor_reboot_bl", "Reboot Bootloader (Honor)"),
                                       command=self.action_honor_reboot_bootloader, theme=self.theme, width=34).pack(pady=5, anchor=tk.W)
        ModernButton(group_honor, text=self.labels.get("btn_honor_reboot_edl", "Reboot EDL (Honor)"),
                                       command=self.action_honor_reboot_edl, theme=self.theme, width=34).pack(pady=5, anchor=tk.W)
        ModernButton(group_honor, text=self.labels.get("btn_honor_wipe_data_cache", "Wipe Data/Cache (Honor)"),
                                       command=self.action_honor_wipe_data_cache, theme=self.theme, width=34).pack(pady=5, anchor=tk.W)

        frp_frame = tk.Frame(group_honor, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        frp_frame.pack(fill=tk.X, pady=(10,5), anchor=tk.W)
        tk.Label(frp_frame, text=self.labels.get("honor_frp_key_label", "Honor FRP Key:"),
                 font=FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                 fg=self.theme.get("FG", "#263238")).pack(side=tk.LEFT, padx=(0,5))
        self.honor_frp_key_var = tk.StringVar()
        honor_frp_entry = tk.Entry(frp_frame, textvariable=self.honor_frp_key_var, width=20, font=FONT,
                                   bg=self.theme.get("LOG_BG", "#CFD8DC"), fg=self.theme.get("FG", "#263238"),
                                   insertbackground=self.theme["FG"], relief="flat", bd=2, highlightthickness=1,
                                   highlightbackground=self.theme.get("ACCENT2", DARK_BLUE_ACCENT2), highlightcolor=self.theme.get("ACCENT", DARK_BLUE_ACCENT))
        honor_frp_entry.pack(side=tk.LEFT, padx=5, ipady=2)
        TextContextMenu(honor_frp_entry, self.master_app.master, self.labels)

        ModernButton(frp_frame, text=self.labels.get("btn_honor_frp", "Remove FRP (Honor Code)"),
                                   command=self.action_honor_remove_frp, theme=self.theme, width=30).pack(side=tk.LEFT, padx=5)
        log_to_file_debug_globally("HonorTab __init__ finished.")

    def action_honor_info(self):
        op_name = "Honor Get Info (Fastboot)"
        command = ["fastboot", "getvar", "all"]
        self.master_app.execute_command_async(command, operation_name=op_name)

    def action_honor_reboot_bootloader(self):
        command = ["fastboot", "reboot-bootloader"]
        self.master_app.execute_command_async(command, operation_name="Honor Reboot Bootloader")

    def action_honor_reboot_edl(self):
        command = ["fastboot", "oem", "edl"]
        self.master_app.execute_command_async(command, operation_name="Honor Reboot EDL")
        if self.master_app.log_panel: self.master_app.log_panel.log("Note: 'fastboot oem edl' command effectiveness varies by device.", "warning", include_timestamp=False)


    def action_honor_wipe_data_cache(self):
        if messagebox.askyesno("Confirm Wipe", "Are you sure you want to wipe data and cache on this Honor device? This will erase all user data.", parent=self.master_app.master):
            op_name = "Honor Wipe Data/Cache"
            if self.master_app.log_panel:
                self.master_app.log_panel.clear_log()
                self.master_app.log_panel.log(self.labels.get("log_operation_started") + op_name, "info", include_timestamp=True)
                self.master_app.log_panel.progress_bar.start()
            self.master_app._update_cancel_button_state(enable=True)

            commands_wipe = [
                (["fastboot", "erase", "cache"], "Honor Wipe Cache"),
                (["fastboot", "erase", "userdata"], "Honor Wipe Userdata")
            ]
            num_wipe_steps = len(commands_wipe)
            current_wipe_step_ref = [0] # List to allow modification

            def _wipe_callback_chained(result_wipe_step, next_idx_wipe):
                current_wipe_step_ref[0] = next_idx_wipe
                if self.master_app.log_panel:
                    prog = int((current_wipe_step_ref[0] / num_wipe_steps) * 100)
                    self.master_app.log_panel.progress_bar.set_value(prog)

                if result_wipe_step.get("error") == "Cancelled":
                    if self.master_app.log_panel:
                        self.master_app.log_panel.log("Honor Wipe sequence cancelled.", "warning", include_timestamp=True)
                    return

                if next_idx_wipe >= num_wipe_steps:
                    if self.master_app.log_panel:
                        if not result_wipe_step.get("error") == "Cancelled":
                             self.master_app.log_panel.log("Honor Wipe Data/Cache commands sent. Device may need manual reboot.", "success", include_timestamp=True)
                    if self.master_app.log_panel and self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                    self.master_app._update_cancel_button_state(enable=False)
                else:
                    _execute_next_wipe_step(next_idx_wipe)

            def _execute_next_wipe_step(step_idx_wipe):
                cmd_wipe, desc_wipe = commands_wipe[step_idx_wipe]
                self.master_app.execute_command_async(
                    cmd_wipe,
                    operation_name=desc_wipe,
                    is_part_of_sequence=True,
                    callback_on_finish=lambda res_wipe: _wipe_callback_chained(res_wipe, step_idx_wipe + 1)
                )
            _execute_next_wipe_step(0)
        else:
            if self.master_app.log_panel: self.master_app.log_panel.log("Honor Wipe Data/Cache cancelled by user.", "info", include_timestamp=True)

    def action_honor_remove_frp(self):
        frp_key = self.honor_frp_key_var.get()
        if not frp_key:
            messagebox.showerror("Input Error", "Please enter the Honor FRP key.", parent=self.master_app.master)
            return

        op_name = f"Honor Remove FRP with Key"
        command = ["fastboot", "oem", "frp-unlock", frp_key]
        self.master_app.execute_command_async(command, operation_name=op_name)
        if self.master_app.log_panel: self.master_app.log_panel.log("Note: Honor FRP removal methods vary significantly and often require device-specific tools or test points. This command is a generic attempt.", "warning", include_timestamp=False)


class XiaomiTab(ttk.Frame):
    def __init__(self, parent_notebook, master_app: UltimateDeviceTool):
        log_to_file_debug_globally("XiaomiTab __init__ started.")
        super().__init__(parent_notebook, style="TFrame")
        self.master_app = master_app
        self.labels = master_app.labels
        self.theme = master_app.theme
        self.config(bg=self.theme.get("BG", "#ECEFF1"))
        self.configure(padding=(15,15))

        container = tk.Frame(self, bg=self.theme.get("BG", "#ECEFF1"))
        container.pack(fill=tk.BOTH, expand=True)

        group_adb = tk.LabelFrame(container, text=self.labels.get("group_xiaomi_adb", "Xiaomi ADB Mode"),
                                  font=LABEL_FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                                  fg=self.theme.get("FG", "#263238"), padx=10, pady=10, relief="groove", bd=2)
        group_adb.pack(pady=(0,10), padx=10, fill=tk.X, expand=False)

        adb_cols_container = tk.Frame(group_adb, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        adb_cols_container.pack(fill=tk.X)
        adb_col1 = tk.Frame(adb_cols_container, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        adb_col1.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10), anchor=tk.N, expand=True)
        adb_col2 = tk.Frame(adb_cols_container, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        adb_col2.pack(side=tk.LEFT, fill=tk.Y, padx=(10,0), anchor=tk.N, expand=True)

        ModernButton(adb_col1, text=self.labels.get("btn_xiaomi_adb_info"),
                                   command=self.action_xiaomi_adb_info, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(adb_col1, text=self.labels.get("btn_xiaomi_reboot_normal_adb", "Reboot Normal (ADB)"),
                                   command=lambda: self.master_app.execute_command_async(["adb", "reboot"], "Xiaomi Reboot Normal (ADB)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(adb_col1, text=self.labels.get("btn_xiaomi_reboot_recovery_adb", "Reboot Recovery (ADB)"),
                                   command=lambda: self.master_app.execute_command_async(["adb", "reboot", "recovery"], "Xiaomi Reboot Recovery (ADB)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)

        ModernButton(adb_col2, text=self.labels.get("btn_xiaomi_reboot_fastboot_adb", "Reboot Fastboot (ADB)"),
                                   command=lambda: self.master_app.execute_command_async(["adb", "reboot", "bootloader"], "Xiaomi Reboot Fastboot (ADB)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(adb_col2, text=self.labels.get("btn_xiaomi_reboot_edl_adb", "Reboot EDL (ADB)"),
                                   command=lambda: self.master_app.execute_command_async(["adb", "reboot", "edl"], "Xiaomi Reboot EDL (ADB)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(adb_col2, text=self.labels.get("btn_xiaomi_enable_diag_root", "Enable Diag (ROOT)") + " *",
                                   command=lambda: messagebox.showinfo("Info", "Enable Diag (ROOT) is a placeholder for specific Xiaomi Diag enabling commands, which usually require root, specific device model knowledge, and are beyond generic ADB/Fastboot. This button is for UI layout.", parent=self.master_app.master), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)


        group_fastboot = tk.LabelFrame(container, text=self.labels.get("group_xiaomi_fastboot", "Xiaomi Fastboot Mode"),
                                       font=LABEL_FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                                       fg=self.theme.get("FG", "#263238"), padx=10, pady=10, relief="groove", bd=2)
        group_fastboot.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        fb_cols_container = tk.Frame(group_fastboot, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        fb_cols_container.pack(fill=tk.X)
        fb_col1 = tk.Frame(fb_cols_container, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        fb_col1.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10), anchor=tk.N, expand=True)
        fb_col2 = tk.Frame(fb_cols_container, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        fb_col2.pack(side=tk.LEFT, fill=tk.Y, padx=(10,0), anchor=tk.N, expand=True)

        ModernButton(fb_col1, text=self.labels.get("btn_xiaomi_fastboot_info", "Read Info (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "getvar", "all"], "Xiaomi Read Info (Fastboot)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(fb_col1, text=self.labels.get("btn_xiaomi_fastboot_read_security", "Read Security (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "oem", "device-info"], "Xiaomi Read Security (Fastboot)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(fb_col1, text=self.labels.get("btn_xiaomi_fastboot_unlock", "Unlock Bootloader (Fastboot)"),
                                   command=self.action_xiaomi_fastboot_unlock, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(fb_col1, text=self.labels.get("btn_xiaomi_fastboot_lock", "Lock Bootloader (Fastboot)"),
                                   command=self.action_xiaomi_fastboot_lock, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)

        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_reboot_sys", "Reboot System (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "reboot"], "Xiaomi Reboot System (Fastboot)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_reboot_fast", "Reboot Fastboot (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "reboot-bootloader"], "Xiaomi Reboot Fastboot (Fastboot)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_reboot_edl", "Reboot EDL (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "oem", "edl"], "Xiaomi Reboot EDL (Fastboot)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_wipe_cache", "Wipe Cache (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "erase", "cache"], "Xiaomi Wipe Cache (Fastboot)"), theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_wipe_data", "Wipe Data (Fastboot)"),
                                   command=self.action_xiaomi_fastboot_wipe_data, theme=self.theme, width=32).pack(pady=5, anchor=tk.W)
        log_to_file_debug_globally("XiaomiTab __init__ finished.")

    def action_xiaomi_adb_info(self):
        self.master_app.fetch_and_log_device_info(
            operation_label_key_on_success="log_read_info_complete",
            next_operation_name=self.labels.get("btn_xiaomi_adb_info")
            )


    def action_xiaomi_fastboot_unlock(self):
        if messagebox.askyesno("Confirm Unlock", "Are you sure you want to unlock the bootloader? This will erase all user data and may void warranty. For Xiaomi, this often requires Mi Unlock Tool and an authorized account.", parent=self.master_app.master):
            self.master_app.execute_command_async(["fastboot", "oem", "unlock"], operation_name="Xiaomi Unlock Bootloader (Attempt)")
            if self.master_app.log_panel: self.master_app.log_panel.log("Note: Xiaomi bootloader unlock often requires official Mi Unlock Tool and account authorization. This command attempts the generic method.", "warning", include_timestamp=False)
        else:
            if self.master_app.log_panel: self.master_app.log_panel.log("Xiaomi Unlock Bootloader cancelled by user.", "info", include_timestamp=True)

    def action_xiaomi_fastboot_lock(self):
        if messagebox.askyesno("Confirm Lock", "Are you sure you want to lock the bootloader? This will erase all user data if the device is not already formatted for a locked state.", parent=self.master_app.master):
            self.master_app.execute_command_async(["fastboot", "oem", "lock"], operation_name="Xiaomi Lock Bootloader")
        else:
            if self.master_app.log_panel: self.master_app.log_panel.log("Xiaomi Lock Bootloader cancelled by user.", "info", include_timestamp=True)

    def action_xiaomi_fastboot_wipe_data(self):
        if messagebox.askyesno("Confirm Wipe", "Are you sure you want to wipe all user data? This cannot be undone.", parent=self.master_app.master):
            self.master_app.execute_command_async(["fastboot", "erase", "userdata"], operation_name="Xiaomi Wipe Data (Fastboot)")
        else:
            if self.master_app.log_panel: self.master_app.log_panel.log("Xiaomi Wipe Data cancelled by user.", "info", include_timestamp=True)

# ========== MTKTab Class ==========
class MTKTab(ttk.Frame):
    def __init__(self, parent_notebook, master_app: UltimateDeviceTool):
        log_to_file_debug_globally("MTKTab __init__ started.")
        super().__init__(parent_notebook, style="TFrame")
        self.master_app = master_app
        self.labels = master_app.labels
        self.theme = master_app.theme
        self.config(bg=self.theme.get("BG", "#ECEFF1"))
        self.configure(padding=(10,10)) # Adjusted padding

        self.da_file_var = tk.StringVar()
        self.auth_file_var = tk.StringVar()
        self.preloader_file_var = tk.StringVar()

        self.mtk_action_sequences = {} # For chained MTK operations like forensic project

        # --- Main container for scrolling ---
        canvas = tk.Canvas(self, bg=self.theme.get("BG", "#ECEFF1"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme.get("BG", "#ECEFF1"))

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def _on_mousewheel(event): # Cross-platform mouse wheel scrolling
            if sys.platform == "win32":
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif sys.platform == "darwin":
                canvas.yview_scroll(int(-1 * event.delta), "units")
            else: # Linux
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel) # Bind to all for when focus is not on canvas
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel) # Bind to frame as well

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Adjust scrollable frame width to canvas width
        def _adjust_frame_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _adjust_frame_width)


        # --- Custom Files Group ---
        group_files = tk.LabelFrame(scrollable_frame, text=self.labels.get("group_mtk_files"),
                                    font=LABEL_FONT, bg=self.theme.get("GROUP_BG"),
                                    fg=self.theme.get("FG"), padx=10, pady=10, relief="groove", bd=2)
        group_files.pack(pady=5, padx=5, fill=tk.X)

        self._create_file_selector(group_files, self.labels.get("label_da_file"), self.da_file_var)
        self._create_file_selector(group_files, self.labels.get("label_auth_file"), self.auth_file_var)
        self._create_file_selector(group_files, self.labels.get("label_preloader_file"), self.preloader_file_var)

        # --- Operations Groups ---
        btn_width = 38 # Standardized button width for MTK tab

        # Dump Operations
        group_dump = tk.LabelFrame(scrollable_frame, text=self.labels.get("group_mtk_dump"),
                                   font=LABEL_FONT, bg=self.theme.get("GROUP_BG"), fg=self.theme.get("FG"),
                                   padx=10, pady=10, relief="groove", bd=2)
        group_dump.pack(pady=5, padx=5, fill=tk.X)
        ModernButton(group_dump, text=self.labels.get("btn_mtk_read_full_dump"), command=self.action_mtk_read_full_dump, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_dump, text=self.labels.get("btn_mtk_read_userdata"), command=self.action_mtk_read_userdata, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_dump, text=self.labels.get("btn_mtk_read_custom_dump"), command=self.action_mtk_read_custom_dump, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_dump, text=self.labels.get("btn_mtk_auto_boot_repair_dump"), command=self.action_mtk_auto_boot_repair_dump, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_dump, text=self.labels.get("btn_mtk_write_dump"), command=self.action_mtk_write_dump, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)

        # Partitions Manager
        group_partitions = tk.LabelFrame(scrollable_frame, text=self.labels.get("group_mtk_partitions"),
                                         font=LABEL_FONT, bg=self.theme.get("GROUP_BG"), fg=self.theme.get("FG"),
                                         padx=10, pady=10, relief="groove", bd=2)
        group_partitions.pack(pady=5, padx=5, fill=tk.X)
        ModernButton(group_partitions, text=self.labels.get("btn_mtk_list_partitions"), command=self.action_mtk_list_partitions, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_partitions, text=self.labels.get("btn_mtk_backup_selected_partitions"), command=self.action_mtk_backup_selected_partitions, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_partitions, text=self.labels.get("btn_mtk_backup_security_partitions"), command=self.action_mtk_backup_security_partitions, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_partitions, text=self.labels.get("btn_mtk_format_selected_partitions"), command=self.action_mtk_format_selected_partitions, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_partitions, text=self.labels.get("btn_mtk_restore_selected_partitions"), command=self.action_mtk_restore_selected_partitions, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_partitions, text=self.labels.get("btn_mtk_reset_nv_data"), command=self.action_mtk_reset_nv_data, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)

        # FRP & Data
        group_frp_data = tk.LabelFrame(scrollable_frame, text=self.labels.get("group_mtk_frp_data"),
                                       font=LABEL_FONT, bg=self.theme.get("GROUP_BG"), fg=self.theme.get("FG"),
                                       padx=10, pady=10, relief="groove", bd=2)
        group_frp_data.pack(pady=5, padx=5, fill=tk.X)
        ModernButton(group_frp_data, text=self.labels.get("btn_mtk_erase_frp"), command=self.action_mtk_erase_frp, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_frp_data, text=self.labels.get("btn_mtk_samsung_frp"), command=self.action_mtk_samsung_frp, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_frp_data, text=self.labels.get("btn_mtk_safe_format"), command=self.action_mtk_safe_format, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_frp_data, text=self.labels.get("btn_mtk_erase_frp_write_file"), command=self.action_mtk_erase_frp_write_file, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_frp_data, text=self.labels.get("btn_mtk_wipe_data"), command=self.action_mtk_wipe_data, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)

        # Bootloader
        group_bootloader = tk.LabelFrame(scrollable_frame, text=self.labels.get("group_mtk_bootloader"),
                                         font=LABEL_FONT, bg=self.theme.get("GROUP_BG"), fg=self.theme.get("FG"),
                                         padx=10, pady=10, relief="groove", bd=2)
        group_bootloader.pack(pady=5, padx=5, fill=tk.X)
        ModernButton(group_bootloader, text=self.labels.get("btn_mtk_unlock_bootloader"), command=self.action_mtk_unlock_bootloader, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_bootloader, text=self.labels.get("btn_mtk_lock_bootloader"), command=self.action_mtk_lock_bootloader, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)

        # Key Extraction & Forensics
        group_keys_forensics = tk.LabelFrame(scrollable_frame, text=self.labels.get("group_mtk_keys_forensics"),
                                             font=LABEL_FONT, bg=self.theme.get("GROUP_BG"), fg=self.theme.get("FG"),
                                             padx=10, pady=10, relief="groove", bd=2)
        group_keys_forensics.pack(pady=5, padx=5, fill=tk.X)
        ModernButton(group_keys_forensics, text=self.labels.get("btn_mtk_extract_keys"), command=self.action_mtk_extract_keys, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_keys_forensics, text=self.labels.get("btn_mtk_generate_ewc"), command=self.action_mtk_generate_ewc, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)
        ModernButton(group_keys_forensics, text=self.labels.get("btn_mtk_build_forensic_project"), command=self.action_mtk_build_forensic_project, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)

        # Flash Operations
        group_flash = tk.LabelFrame(scrollable_frame, text=self.labels.get("group_mtk_flash"),
                                    font=LABEL_FONT, bg=self.theme.get("GROUP_BG"), fg=self.theme.get("FG"),
                                    padx=10, pady=10, relief="groove", bd=2)
        group_flash.pack(pady=5, padx=5, fill=tk.X)
        ModernButton(group_flash, text=self.labels.get("btn_mtk_flash_scatter"), command=self.action_mtk_flash_scatter, theme=self.theme, width=btn_width).pack(pady=3, anchor=tk.W)

        log_to_file_debug_globally("MTKTab __init__ finished.")

    def _create_file_selector(self, parent, label_text, var):
        frame = tk.Frame(parent, bg=self.theme.get("GROUP_BG"))
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=label_text, font=FONT, bg=self.theme.get("GROUP_BG"), fg=self.theme.get("FG")).pack(side=tk.LEFT, padx=(0,5))
        entry = tk.Entry(frame, textvariable=var, font=FONT, width=40, state="readonly",
                         bg=self.theme.get("LOG_BG"), fg=self.theme.get("FG"))
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ModernButton(frame, text=self.labels.get("btn_browse"),
                     command=lambda v=var: self._browse_file(v),
                     theme=self.theme, width=10, icon_path="browse_icon.png", icon_size=(12,12), padx=4, pady=2).pack(side=tk.LEFT, padx=(5,0))

    def _browse_file(self, var_to_set):
        filepath = filedialog.askopenfilename(parent=self.master_app.master)
        if filepath:
            var_to_set.set(filepath)
            if self.master_app.log_panel:
                self.master_app.log_panel.log(f"Selected file: {filepath}", "info")

    def _get_common_mtk_cmd_parts(self, base_cmd_list):
        """Helper to get mtk_exe and common DA/Auth/PL options."""
        mtk_exe = self.master_app.get_mtk_executable_path()
        if not mtk_exe:
            return None

        command = [mtk_exe] + base_cmd_list
        if self.da_file_var.get():
            command.extend(["-da", self.da_file_var.get()])
        if self.auth_file_var.get():
            command.extend(["-auth", self.auth_file_var.get()])
        if self.preloader_file_var.get():
            command.extend(["-loader", self.preloader_file_var.get()])
        return command

    def _execute_mtk_action(self, action_name_key, mtk_base_cmd,
                            requires_output_dir=False,
                            requires_input_file_title_key=None,
                            requires_cfg_file_title_key=None,
                            extra_cmd_parts_func=None, # func(input_file, cfg_file, output_dir) -> list
                            callback_func=None,
                            confirm=True):
        """Generic executor for MTK actions."""
        op_display_name = self.labels.get(action_name_key, action_name_key.replace("btn_mtk_", "").replace("_", " ").title())

        if confirm:
            if not messagebox.askokcancel(
                self.labels.get("mtk_confirm_action_title"),
                self.labels.get("mtk_confirm_action_msg").format(action_name=op_display_name),
                icon=messagebox.WARNING, parent=self.master_app.master):
                if self.master_app.log_panel:
                    self.master_app.log_panel.log(f"MTK Action '{op_display_name}' cancelled by user.", "info", include_timestamp=True)
                return

        command_parts = self._get_common_mtk_cmd_parts(mtk_base_cmd)
        if not command_parts:
            return # mtk_exe not found, error already shown by get_mtk_executable_path

        output_dir = None
        if requires_output_dir:
            output_dir = filedialog.askdirectory(
                title=f"{op_display_name} - {self.labels.get('mtk_output_dir_prompt_title', 'Select Output Dir')}",
                parent=self.master_app.master
            )
            if not output_dir:
                if self.master_app.log_panel: self.master_app.log_panel.log(f"{op_display_name}: Cancelled, no output directory.", "info")
                return
            command_parts.extend(["-o", output_dir])

        input_file = None
        if requires_input_file_title_key:
            input_file = filedialog.askopenfilename(
                title=self.labels.get(requires_input_file_title_key, "Select Input File"),
                parent=self.master_app.master
            )
            if not input_file:
                if self.master_app.log_panel: self.master_app.log_panel.log(f"{op_display_name}: Cancelled, no input file.", "info")
                return
            # Input file might be the main arg or part of extra_cmd_parts_func

        cfg_file = None
        if requires_cfg_file_title_key:
            cfg_file = filedialog.askopenfilename(
                title=self.labels.get(requires_cfg_file_title_key, "Select CFG File (Optional)"),
                parent=self.master_app.master
            )
            # It's optional, so proceed even if not selected

        if extra_cmd_parts_func:
            try:
                # Ensure all three potential args are passed, function can choose to ignore them
                extra_parts = extra_cmd_parts_func(input_file, cfg_file, output_dir)
                if extra_parts is None: # Indicates an issue within the function, or deliberate abort
                    if self.master_app.log_panel: self.master_app.log_panel.log(f"{op_display_name}: Aborted by extra_cmd_parts_func.", "warning")
                    return
                command_parts.extend(extra_parts)
            except TypeError as te:
                 log_to_file_debug_globally(f"TypeError in extra_cmd_parts_func for {op_display_name}: {te}", "WARNING")
                 # Attempt with fewer arguments if TypeError indicates it
                 try:
                    extra_parts = extra_cmd_parts_func(input_file, cfg_file)
                    if extra_parts is None: return
                    command_parts.extend(extra_parts)
                 except TypeError:
                    try:
                        extra_parts = extra_cmd_parts_func(input_file)
                        if extra_parts is None: return
                        command_parts.extend(extra_parts)
                    except TypeError:
                         if self.master_app.log_panel: self.master_app.log_panel.log(f"{op_display_name}: extra_cmd_parts_func has argument mismatch.", "error")
                         return # Abort due to function signature mismatch


        final_callback = callback_func
        if not final_callback: # Default callback if none provided
            def _default_cb(result):
                if self.master_app.log_panel:
                    if result.get("return_code") == 0:
                        log_msg = f"{op_display_name}: Successfully completed."
                        if output_dir: log_msg += f" Files in: {output_dir}"
                        self.master_app.log_panel.log(log_msg, "success")
                    # Failure is handled by main _handle_command_result, no need to log fail here again
            final_callback = _default_cb
        
        if self.master_app.log_panel: # Log before execution
            self.master_app.log_panel.clear_log() # Clear for new top-level MTK operation
            self.master_app.log_panel.log(f"Starting: {op_display_name}...", "info", include_timestamp=True)
            self.master_app.log_panel.log(f"  DA: {self.da_file_var.get() or 'N/A'}", "info", indent=1)
            self.master_app.log_panel.log(f"  Auth: {self.auth_file_var.get() or 'N/A'}", "info", indent=1)
            self.master_app.log_panel.log(f"  PL: {self.preloader_file_var.get() or 'N/A'}", "info", indent=1)
            if output_dir: self.master_app.log_panel.log(f"  Output: {output_dir}", "info", indent=1)
            if input_file: self.master_app.log_panel.log(f"  Input File: {input_file}", "info", indent=1)
            if cfg_file: self.master_app.log_panel.log(f"  CFG File: {cfg_file}", "info", indent=1)


        self.master_app.execute_command_async(command_parts, operation_name=op_display_name, callback_on_finish=final_callback)

    # --- Dump Operations ---
    def action_mtk_read_full_dump(self):
        self._execute_mtk_action("btn_mtk_read_full_dump", ["rf"], requires_output_dir=True)

    def action_mtk_read_userdata(self):
        self._execute_mtk_action("btn_mtk_read_userdata", ["r", "userdata"], requires_output_dir=True)

    def _get_partitions_from_user(self, op_display_name):
        partitions_str = simpledialog.askstring(
            self.labels.get("mtk_partitions_prompt_title", "Select Partitions"),
            self.labels.get("mtk_partitions_prompt_msg", "Enter partitions (comma-separated):"),
            parent=self.master_app.master
        )
        if not partitions_str or not partitions_str.strip():
            if self.master_app.log_panel:
                self.master_app.log_panel.log(f"{op_display_name}: {self.labels.get('mtk_no_partitions_selected', 'No partitions.')}", "warning")
            return None
        return [p.strip() for p in partitions_str.split(',') if p.strip()]

    def action_mtk_read_custom_dump(self):
        op_name = self.labels.get("btn_mtk_read_custom_dump")
        partitions = self._get_partitions_from_user(op_name)
        if not partitions: return

        def extra_parts(inp_file, cfg_f, out_dir): # Add out_dir for consistency
            return partitions
        self._execute_mtk_action("btn_mtk_read_custom_dump", ["r"], requires_output_dir=True, extra_cmd_parts_func=extra_parts)

    def action_mtk_auto_boot_repair_dump(self):
        boot_partitions = ["preloader", "preloader_raw", "lk", "lk2", "boot", "recovery", "para", "logo", "tee1", "tee2", "scp1", "scp2", "sspm_1", "sspm_2", "md1img", "spmfw"] # Expanded list
        def extra_parts(inp, cfg, out_dir):
            return boot_partitions

        def callback(result):
            # This callback is executed *after* the mtk command finishes.
            # The default success/failure logging is handled by _handle_command_result.
            # We only add specific logic for CFG file creation here.
            if result.get("return_code") == 0:
                # Try to determine output_dir from the command if possible
                output_dir_from_cmd = None
                cmd_list = result.get("command", [])
                try:
                    o_index = cmd_list.index("-o")
                    if o_index + 1 < len(cmd_list):
                        output_dir_from_cmd = cmd_list[o_index + 1]
                except ValueError:
                    pass # '-o' not found
                
                if output_dir_from_cmd and os.path.isdir(output_dir_from_cmd):
                    if self.master_app.log_panel: # Redundant log, but for clarity of where files are
                        self.master_app.log_panel.log(f"Boot Repair Dump files should be in: {output_dir_from_cmd}", "info", indent=1)
                    
                    cfg_file_path = os.path.join(output_dir_from_cmd, "mtk_boot_repair_dump.cfg")
                    try:
                        with open(cfg_file_path, 'w', encoding='utf-8') as f:
                            f.write("# Auto Boot Repair Dump Configuration\n")
                            for part_name in boot_partitions:
                                part_bin_name = f"{part_name}.bin" # mtkclient typically saves as {partition}.bin
                                if os.path.exists(os.path.join(output_dir_from_cmd, part_bin_name)):
                                    f.write(f"{part_name}={part_bin_name}\n") # Relative path for CFG
                        if self.master_app.log_panel:
                            self.master_app.log_panel.log(f"Generated boot repair CFG: {cfg_file_path}", "info", indent=1)
                    except Exception as e_cfg:
                        if self.master_app.log_panel:
                            self.master_app.log_panel.log(f"Error generating CFG for boot repair: {e_cfg}", "error", indent=1)
                else:
                    if self.master_app.log_panel:
                         self.master_app.log_panel.log(f"Could not determine output directory for Boot Repair CFG generation.", "warning", indent=1)


        self._execute_mtk_action("btn_mtk_auto_boot_repair_dump", ["r"],
                                 requires_output_dir=True,
                                 extra_cmd_parts_func=extra_parts,
                                 callback_func=callback)

    def action_mtk_write_dump(self):
        def extra_parts(dump_file, cfg_file, out_dir): # Add out_dir for consistency
            if not dump_file: return None # Should have been caught by requires_input_file
            parts = [dump_file] # The dump file is the main argument for 'w'
            if cfg_file:
                parts.extend(["-cfg", cfg_file])
            return parts

        self._execute_mtk_action("btn_mtk_write_dump", ["w"],
                                 requires_input_file_title_key="mtk_select_dump_file",
                                 requires_cfg_file_title_key="mtk_select_cfg_file",
                                 extra_cmd_parts_func=extra_parts)

    # --- Partitions Manager ---
    def action_mtk_list_partitions(self):
        def callback(result):
            if result.get("return_code") == 0 and self.master_app.log_panel:
                self.master_app.log_panel.log("Partitions list retrieved:", "success") # Main success
                stdout = result.get("stdout", "")
                found_partitions = []
                # Regex to capture partition name more reliably from mtkclient output
                # Example lines: "0. preloader: 0x0 - 0x80000 (512 KiB)" or "preloader (512 KiB)"
                # or "preloader" from simpler listings.
                for line in stdout.splitlines():
                    line = line.strip()
                    match = re.match(r"^\s*(?:\d+\.\s*)?([a-zA-Z0-9_-]+)\s*(?:[:(]|$)", line)
                    if match:
                        part_name = match.group(1)
                        # Filter out common headers or non-partition names
                        if part_name.lower() not in ["gpt", "idx", "name", "partition_name", "sgpt", "size", "start", "end", "addr", "type", "guid", "attributes"]:
                            found_partitions.append(part_name)
                            self.master_app.log_panel.log(f"  - {part_name}", "info", indent=1) # Log each found partition
                
                if not found_partitions:
                    if "GPT header not found" in stdout or "No partitions found" in stdout:
                         self.master_app.log_panel.log("GPT header not found or no partitions reported by mtkclient.", "warning", indent=1)
                    else:
                         self.master_app.log_panel.log("No partitions parsed from output, or output was empty. Check full mtkclient output if available in debug logs.", "warning", indent=1)

        self._execute_mtk_action("btn_mtk_list_partitions", ["gpt"], callback_func=callback, confirm=False) # List is generally safe

    def action_mtk_backup_selected_partitions(self):
        op_name = self.labels.get("btn_mtk_backup_selected_partitions")
        partitions = self._get_partitions_from_user(op_name)
        if not partitions: return
        def extra_parts(inp, cfg, out_dir): return partitions # Partitions are main args for 'r'
        self._execute_mtk_action("btn_mtk_backup_selected_partitions", ["r"],
                                 requires_output_dir=True, extra_cmd_parts_func=extra_parts)

    def action_mtk_backup_security_partitions(self):
        security_partitions = ["proinfo", "nvram", "nvdata", "nvcfg", "protect1", "protect2", "seccfg", "secro", "metadata", "oemkeystore", "keystore", "frp", "otp"]
        def extra_parts(inp, cfg, out_dir): return security_partitions
        self._execute_mtk_action("btn_mtk_backup_security_partitions", ["r"],
                                 requires_output_dir=True, extra_cmd_parts_func=extra_parts)

    def action_mtk_format_selected_partitions(self):
        op_name = self.labels.get("btn_mtk_format_selected_partitions")
        partitions = self._get_partitions_from_user(op_name)
        if not partitions: return
        def extra_parts(inp, cfg, out_dir): return partitions # Partitions are main args for 'e'
        self._execute_mtk_action("btn_mtk_format_selected_partitions", ["e"], extra_cmd_parts_func=extra_parts)

    def action_mtk_restore_selected_partitions(self):
        # mtkclient uses -cfg for writing partitions from files specified in the CFG
        def extra_parts(main_input_file_ignored, cfg_file, out_dir_ignored): # input_file and out_dir are not directly used here
            if not cfg_file:
                messagebox.showerror("CFG File Missing", "A CFG file specifying partitions and their image files is required for restore.", parent=self.master_app.master)
                return None # Abort
            # For restoring partitions from files, the CFG *is* the primary argument after 'w' and DA/Auth/PL
            # The mtkclient command structure is `mtk w -cfg your_config.cfg`
            # So, the base command is 'w', and this function provides ['-cfg', cfg_file]
            return ["-cfg", cfg_file]

        self._execute_mtk_action("btn_mtk_restore_selected_partitions", ["w"], # Base command is 'w'
                                 requires_cfg_file_title_key="mtk_select_cfg_file", # Only CFG file is needed
                                 extra_cmd_parts_func=extra_parts)


    def action_mtk_reset_nv_data(self):
        nv_partitions = ["nvram", "nvdata", "nvcfg"]
        def extra_parts(inp, cfg, out_dir): return nv_partitions
        self._execute_mtk_action("btn_mtk_reset_nv_data", ["e"], extra_cmd_parts_func=extra_parts)

    # --- FRP & Data ---
    def action_mtk_erase_frp(self):
        self._execute_mtk_action("btn_mtk_erase_frp", ["e", "frp"])

    def action_mtk_samsung_frp(self):
        samsung_frp_partitions = ["frp", "persistent", "PERSISTENT", "steady", "STEADY", "param", "PARAM"] # Case variations
        def extra_parts(inp, cfg, out_dir): return samsung_frp_partitions
        self._execute_mtk_action("btn_mtk_samsung_frp", ["e"], extra_cmd_parts_func=extra_parts)

    def action_mtk_safe_format(self):
        safe_partitions_to_format = ["cache", "metadata"]
        if not messagebox.askokcancel(
                self.labels.get("mtk_confirm_action_title"),
                f"This will attempt to format: {', '.join(safe_partitions_to_format)}. THIS IS RISKY. Data loss on these partitions will occur. Proceed?",
                icon=messagebox.WARNING, parent=self.master_app.master):
            if self.master_app.log_panel: self.master_app.log_panel.log("Safe Format cancelled.", "info")
            return

        def extra_parts(inp, cfg, out_dir): return safe_partitions_to_format
        self._execute_mtk_action("btn_mtk_safe_format", ["e"], extra_cmd_parts_func=extra_parts, confirm=False) # Already confirmed

    def action_mtk_erase_frp_write_file(self):
        temp_cfg_file_path_holder = [None] # Use a list to pass by reference for modification in nested func

        def extra_parts(frp_file, cfg_file_ignored, out_dir_ignored):
            if not frp_file: return None # Should be caught if input_file was required

            try:
                # Create a temporary CFG file
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cfg', encoding='utf-8') as temp_cfg_file:
                    temp_cfg_file.write(f"frp={frp_file}\n") # Assumes frp_file is the path to the image for 'frp' partition
                    temp_cfg_file_path_holder[0] = temp_cfg_file.name
                return ["-cfg", temp_cfg_file_path_holder[0]]
            except Exception as e:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log(f"Error creating temporary CFG for FRP write: {e}", "error")
                return None # Abort if temp file creation fails

        def callback_frp_write(result):
            # This callback is executed after the mtk command finishes.
            # Clean up the temporary CFG file.
            if temp_cfg_file_path_holder[0] and os.path.exists(temp_cfg_file_path_holder[0]):
                try:
                    os.unlink(temp_cfg_file_path_holder[0])
                    if self.master_app.log_panel: self.master_app.log_panel.log("Temporary FRP CFG file deleted.", "info", indent=1)
                except Exception as e_unlink:
                    if self.master_app.log_panel: self.master_app.log_panel.log(f"Error deleting temporary FRP CFG: {e_unlink}", "warning", indent=1)
            # Default success/fail logging for the main operation is handled by _handle_command_result.

        self._execute_mtk_action("btn_mtk_erase_frp_write_file", ["w"], # Base command is 'w'
                                 requires_input_file_title_key="mtk_select_frp_file", # This is the frp image file
                                 extra_cmd_parts_func=extra_parts,
                                 callback_func=callback_frp_write)

    def action_mtk_wipe_data(self):
        self._execute_mtk_action("btn_mtk_wipe_data", ["e", "userdata"])

    # --- Bootloader ---
    def action_mtk_unlock_bootloader(self):
        self._execute_mtk_action("btn_mtk_unlock_bootloader", ["da", "seccfg", "unlock"])

    def action_mtk_lock_bootloader(self):
        self._execute_mtk_action("btn_mtk_lock_bootloader", ["da", "seccfg", "lock"])

    # --- Key Extraction & Forensics ---
    def action_mtk_extract_keys(self):
        self._execute_mtk_action("btn_mtk_extract_keys", ["keys"], requires_output_dir=True)

    def action_mtk_generate_ewc(self):
        op_display_name = self.labels.get("btn_mtk_generate_ewc")

        if not messagebox.askokcancel(
            self.labels.get("mtk_confirm_action_title"),
            self.labels.get("mtk_confirm_action_msg").format(action_name=op_display_name) + "\nThis will first attempt to extract keys.",
            icon=messagebox.WARNING, parent=self.master_app.master):
            if self.master_app.log_panel: self.master_app.log_panel.log(f"'{op_display_name}' cancelled by user.", "info")
            return

        ewc_project_dir = filedialog.askdirectory(
            title=f"{op_display_name} - {self.labels.get('mtk_output_dir_prompt_title')}",
            parent=self.master_app.master
        )
        if not ewc_project_dir:
            if self.master_app.log_panel: self.master_app.log_panel.log(f"{op_display_name}: Cancelled, no output directory.", "info")
            return

        keys_dir = os.path.join(ewc_project_dir, "keys_for_ewc")
        os.makedirs(keys_dir, exist_ok=True)

        command_parts_keys = self._get_common_mtk_cmd_parts(["keys"])
        if not command_parts_keys: return # mtkclient not found
        command_parts_keys.extend(["-o", keys_dir])

        if self.master_app.log_panel:
            self.master_app.log_panel.clear_log()
            self.master_app.log_panel.log(f"Starting: {op_display_name}...", "info", include_timestamp=True)
            self.master_app.log_panel.log(f"  Step 1: Extracting keys to {keys_dir}", "info", indent=1)

        def _keys_extracted_callback(key_result):
            if key_result.get("return_code") != 0:
                if self.master_app.log_panel: self.master_app.log_panel.log("Failed to extract keys. Cannot generate EWC file.", "error")
                return # Stop here

            if self.master_app.log_panel: self.master_app.log_panel.log("Keys extracted successfully. Proceeding to generate EWC.", "success", indent=1)

            ewc_file_path = os.path.join(ewc_project_dir, f"mtk_forensic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ewc")
            try:
                found_key_files_content = []
                if os.path.exists(keys_dir):
                    for item in os.listdir(keys_dir):
                        if item.endswith((".key", ".bin")) or "key" in item.lower(): # Broader check for key files
                            item_path = os.path.join(keys_dir, item)
                            if os.path.isfile(item_path):
                                try:
                                    with open(item_path, 'r', encoding='utf-8', errors='ignore') as kf:
                                        found_key_files_content.append((item, kf.read()))
                                except Exception: # If not readable as text, skip content for EWC or mark as binary
                                    found_key_files_content.append((item, "[Binary Key Data - Not Displayed]"))


                with open(ewc_file_path, 'w', encoding='utf-8') as f_ewc:
                    f_ewc.write("<!-- Simulated EWC Content for Oxygen Forensic -->\n")
                    f_ewc.write(f"<ewc_project tool_version=\"{self.labels.get('title')}\" created=\"{datetime.now().isoformat()}\">\n")
                    f_ewc.write("  <device_info model=\"MTK Device (Generic)\">\n")
                    f_ewc.write(f"    <da_file path=\"{self.da_file_var.get() or 'N/A'}\"/>\n")
                    f_ewc.write(f"    <auth_file path=\"{self.auth_file_var.get() or 'N/A'}\"/>\n")
                    f_ewc.write(f"    <preloader_file path=\"{self.preloader_file_var.get() or 'N/A'}\"/>\n")
                    f_ewc.write("  </device_info>\n")
                    f_ewc.write("  <extracted_keys>\n")
                    if found_key_files_content:
                        for key_name, key_value in found_key_files_content:
                            # Sanitize key_name for XML tag if needed, though CDATA helps for value
                            safe_key_name = re.sub(r'\W+', '_', key_name.split('.')[0]) # Basic sanitization
                            f_ewc.write(f"    <key name=\"{safe_key_name}\" original_filename=\"{key_name}\"><![CDATA[{key_value.strip()}]]></key>\n")
                    else:
                        f_ewc.write("    <!-- No specific key files found or parsed from key extraction step -->\n")
                    f_ewc.write("  </extracted_keys>\n")
                    f_ewc.write("</ewc_project>\n")

                if self.master_app.log_panel:
                    self.master_app.log_panel.log(f"EWC file generated successfully: {ewc_file_path}", "success")
            except Exception as e_ewc_gen:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log(f"Error generating EWC file content: {e_ewc_gen}", "error")
                log_to_file_debug_globally(f"EWC Generation Error: {e_ewc_gen}\n{traceback.format_exc()}", "ERROR_TRACE")


        # Execute the key extraction part of the EWC generation
        self.master_app.execute_command_async(command_parts_keys,
                                             operation_name=f"{op_display_name} (Key Extraction Step)",
                                             callback_on_finish=_keys_extracted_callback)


    def action_mtk_build_forensic_project(self):
        op_display_name = self.labels.get("btn_mtk_build_forensic_project")

        if not messagebox.askokcancel(
            self.labels.get("mtk_confirm_action_title"),
            self.labels.get("mtk_confirm_action_msg").format(action_name=op_display_name) + "\nThis will perform multiple operations and create a project folder.",
            icon=messagebox.WARNING, parent=self.master_app.master):
            if self.master_app.log_panel: self.master_app.log_panel.log(f"'{op_display_name}' cancelled by user.", "info")
            return

        project_base_dir = filedialog.askdirectory(
            title=f"{op_display_name} - {self.labels.get('mtk_output_dir_prompt_title', 'Select Project Base Directory')}",
            parent=self.master_app.master
        )
        if not project_base_dir:
            if self.master_app.log_panel: self.master_app.log_panel.log(f"{op_display_name}: Cancelled, no project directory selected.", "info")
            return

        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_dir = os.path.join(project_base_dir, f"MTK_Forensic_Project_{timestamp_str}")
        keys_dir = os.path.join(project_dir, "keys")
        dumps_dir = os.path.join(project_dir, "dumps")
        metadata_dir = os.path.join(project_dir, "metadata")

        try:
            os.makedirs(keys_dir, exist_ok=True)
            os.makedirs(dumps_dir, exist_ok=True)
            os.makedirs(metadata_dir, exist_ok=True)
        except OSError as e_mkdir:
            if self.master_app.log_panel: self.master_app.log_panel.log(f"Error creating project directories: {e_mkdir}", "error")
            messagebox.showerror("Directory Error", f"Could not create project directories: {e_mkdir}", parent=self.master_app.master)
            return

        if self.master_app.log_panel:
            self.master_app.log_panel.clear_log()
            self.master_app.log_panel.log(f"Starting: {op_display_name}...", "info", include_timestamp=True)
            self.master_app.log_panel.log(f"Project directory: {project_dir}", "info", indent=1)
            self.master_app.log_panel.progress_bar.start() # Start overall progress
        self.master_app._update_cancel_button_state(enable=True)


        self.mtk_action_sequences['forensic_project'] = {
            'project_dir': project_dir, 'keys_dir': keys_dir, 'dumps_dir': dumps_dir, 'metadata_dir': metadata_dir,
            'current_step': 0,
            'steps': [
                {'name': 'Extract Keys', 'func': self._fp_step_extract_keys, 'op_name_log': "FP: Extract Keys"},
                {'name': 'List Partitions', 'func': self._fp_step_list_partitions, 'op_name_log': "FP: List Partitions"},
                {'name': 'Backup Security Partitions', 'func': self._fp_step_backup_security, 'op_name_log': "FP: Backup Security"},
                # Optional: Read Full Userarea Dump (can be very large and time-consuming)
                # {'name': 'Read Full Userarea Dump (Optional)', 'func': self._fp_step_read_full_dump_optional, 'op_name_log': "FP: Read Full Dump"},
                {'name': 'Generate EWC', 'func': self._fp_step_generate_ewc_for_project, 'op_name_log': "FP: Generate EWC"}, # EWC generation is local
                {'name': 'Finalize Project', 'func': self._fp_step_finalize, 'op_name_log': "FP: Finalize"} # Local file writing
            ]
        }
        self._run_next_forensic_project_step()

    def _fp_abort(self):
        """Helper to abort forensic project sequence."""
        if self.master_app.log_panel:
            self.master_app.log_panel.log("Forensic project build aborted due to mtkclient path issue.", "error")
            if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
        self.master_app._update_cancel_button_state(enable=False)
        self.mtk_action_sequences.pop('forensic_project', None)


    def _run_next_forensic_project_step(self):
        sequence = self.mtk_action_sequences.get('forensic_project')
        if not sequence: # Sequence might have been aborted/cleared
            if self.master_app.log_panel and self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
            self.master_app._update_cancel_button_state(enable=False)
            return

        if sequence['current_step'] >= len(sequence['steps']):
            if self.master_app.log_panel:
                 self.master_app.log_panel.log("Forensic project build sequence completed.", "success", include_timestamp=True)
                 if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
            self.master_app._update_cancel_button_state(enable=False)
            self.mtk_action_sequences.pop('forensic_project', None) # Clear sequence
            return

        step_info = sequence['steps'][sequence['current_step']]
        if self.master_app.log_panel:
             self.master_app.log_panel.log(f"Forensic Project - Step {sequence['current_step'] + 1}/{len(sequence['steps'])}: {step_info['name']}", "info", indent=1, include_timestamp=False)
        
        # Update progress bar for the overall sequence
        if self.master_app.log_panel:
            overall_progress = int(((sequence['current_step']) / len(sequence['steps'])) * 100)
            self.master_app.log_panel.progress_bar.set_value(overall_progress)

        try:
            step_info['func']() # Execute the current step's function
        except Exception as e_step_func:
            log_msg = f"Error executing forensic project step '{step_info['name']}': {e_step_func}"
            if self.master_app.log_panel: self.master_app.log_panel.log(log_msg, "error", indent=2)
            log_to_file_debug_globally(log_msg + f"\n{traceback.format_exc()}", "ERROR_TRACE")
            self.mtk_action_sequences.pop('forensic_project', None) # Abort sequence
            if self.master_app.log_panel and self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
            self.master_app._update_cancel_button_state(enable=False)


    def _fp_step_callback_factory(self, success_msg_key):
        """Creates a callback for a step in the forensic project sequence."""
        def _callback(result):
            sequence = self.mtk_action_sequences.get('forensic_project')
            if not sequence: return # Sequence was aborted

            step_failed = False
            if result.get("error") == "Cancelled":
                if self.master