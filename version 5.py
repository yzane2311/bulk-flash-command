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
        "log": "Operation Log",
        "group_samsung": "Samsung ADB Repair & Utilities",
        "group_file": "File & App Management",
        "group_honor": "Honor Fastboot Tools",
        "group_xiaomi_adb": "Xiaomi ADB Mode",
        "group_xiaomi_fastboot": "Xiaomi Fastboot Mode",
        "group_advanced_cmd": "Advanced Command Execution",
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
        "search_log_label": "Search Log:",
        "find_button": "Find",
        "all_button": "All",
        "export_button": "Export to TXT",
        "btn_export_csv": "Export to CSV",
        "btn_cancel_operation": "Cancel Operation",
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
        "frp_reset_warning_message": "This will attempt a series of common ADB commands to reset FRP. These commands are not guaranteed to work on all devices or Android versions and may require specific device states. Proceed with caution.",
        "screen_lock_reset_warning_title": "Screen Lock Reset Attempt",
        "screen_lock_reset_warning_message": "This attempts to remove screen lock files. It usually requires ROOT access and is unlikely to work on modern Android versions due to encryption. Data loss is possible. Proceed with extreme caution.",
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
        "btn_group_support": "Group Support", # New Label
        "device_status_panel_title": "ADB Connection Status", # Modified Label
        "status_model": "Model:",
        "status_android": "Android:",
        "status_connection": "Connection:",
        "status_root": "Root:",
        "status_unknown": "Unknown",
        "btn_refresh_status": "Refresh",
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
        "mdm_remove_warning_message": "This will attempt to disable common MDM-related packages via ADB. This operation is not guaranteed to work on all devices/setups and might have unintended consequences if essential system components are disabled. Proceed with caution. A device reboot may be required.",
        "knox_bypass_warning_title": "Knox Bypass Attempt",
        "knox_bypass_warning_message": "This will attempt to disable common Knox-related packages via ADB. This operation is intended for specific scenarios like school tablets after use and is not guaranteed to work on all devices/setups. Disabling Knox components might affect device security and functionality. Proceed with extreme caution. A device reboot may be required.",
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
        "log": "سجل العمليات",
        "group_samsung": "إصلاح سامسونج وأدوات ADB",
        "group_file": "إدارة الملفات والتطبيقات",
        "group_honor": "أدوات هونور Fastboot",
        "group_xiaomi_adb": "شاومي وضع ADB",
        "group_xiaomi_fastboot": "شاومي وضع Fastboot",
        "group_advanced_cmd": "تنفيذ أوامر متقدمة",
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
        "search_log_label": "بحث في السجل:",
        "find_button": "بحث",
        "all_button": "الكل",
        "export_button": "تصدير إلى TXT",
        "btn_export_csv": "تصدير إلى CSV",
        "btn_cancel_operation": "إلغاء العملية",
        "quit_dialog_title": "خروج",
        "quit_dialog_message": "هل تريد الخروج من أداة Ultimat-Unlock؟",
        "dependency_check_title": "فحص الاعتماديات",
        "adb_not_found_message": "ADB (Android Debug Bridge) غير موجود أو لا يعمل. بعض الميزات لن تكون متاحة. الرجاء تثبيت/تكوين ADB وإضافته إلى مسار النظام.",
        "fastboot_not_found_message": "Fastboot غير موجود أو لا يعمل. بعض الميزات لن تكون متاحة. الرجاء تثبيت/تكوين Fastboot وإضافته إلى مسار النظام.",
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
        "arabize_confirm_message": "سيحاول هذا الإجراء تغيير لغة الجهاز إلى العربية (ar-AE).\nقد يتطلب هذا أذونات معينة وقد لا يعمل على جميع الأجهزة.\nمتابعة؟",
        "arabize_note": "ملاحظة: قد يتطلب التعريب إذن WRITE_SECURE_SETTINGS أو صلاحيات الروت على بعض الأجهزة. تختلف الفعالية.",
        "open_browser_title": "فتح رابط في متصفح الجهاز",
        "open_browser_prompt": "أدخل الرابط الكامل للفتح (مثال: https://ultimat-unlock.com/):",
        "frp_reset_warning_title": "محاولة إزالة FRP",
        "frp_reset_warning_message": "سيقوم هذا الإجراء بمحاولة تنفيذ سلسلة من أوامر ADB الشائعة لإزالة قفل FRP. هذه الأوامر ليست مضمونة للعمل على جميع الأجهزة أو إصدارات أندرويد وقد تتطلب حالات معينة بالجهاز. تابع بحذر.",
        "screen_lock_reset_warning_title": "محاولة إزالة قفل الشاشة",
        "screen_lock_reset_warning_message": "يحاول هذا الإجراء إزالة ملفات قفل الشاشة. يتطلب عادةً صلاحيات الروت ومن غير المرجح أن يعمل على إصدارات أندرويد الحديثة بسبب التشفير. فقدان البيانات محتمل. تابع بحذر شديد.",
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
        "btn_group_support": "دعم المجموعة", # New Label
        "device_status_panel_title": "حالة اتصال ADB", # Modified Label
        "status_model": "الطراز:",
        "status_android": "أندرويد:",
        "status_connection": "الاتصال:",
        "status_root": "الروت:",
        "status_unknown": "غير معروف",
        "btn_refresh_status": "تحديث",
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
        "mdm_remove_warning_message": "سيحاول هذا الإجراء تعطيل حزم MDM الشائعة عبر ADB. هذا الإجراء غير مضمون للعمل على جميع الأجهزة/الإعدادات وقد يكون له عواقب غير مقصودة إذا تم تعطيل مكونات نظام أساسية. تابع بحذر. قد تكون إعادة تشغيل الجهاز ضرورية.",
        "knox_bypass_warning_title": "محاولة تجاوز Knox",
        "knox_bypass_warning_message": "سيحاول هذا الإجراء تعطيل حزم Knox الشائعة عبر ADB. هذا الإجراء مخصص لسيناريوهات محددة مثل أجهزة التابلت المدرسية بعد الاستخدام وغير مضمون للعمل على جميع الأجهزة/الإعدادات. قد يؤثر تعطيل مكونات Knox على أمان الجهاز ووظائفه. تابع بحذر شديد. قد تكون إعادة تشغيل الجهاز ضرورية.",
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
        "NOTEBOOK_TAB_ACTIVE_BG": DARK_BLUE_ACCENT2
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
        "NOTEBOOK_TAB_ACTIVE_BG": DARK_BLUE_ACCENT2
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
        "TITLE_FG": "#FFFFFF", "EDITION_FG": "#AAB8C5"
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
BTN_FONT = ("Segoe UI", 9, "bold") 
LOG_FONT = ("Consolas", 11)
log_to_file_debug_globally("FONTS defined.")

app_images = {}

def load_image(image_path, size=None):
    if not PIL_AVAILABLE:
        log_to_file_debug_globally(f"Pillow not available, cannot load {image_path}.", "WARNING")
        return None
    try:
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        full_path = os.path.join(base_dir, image_path)
        img = Image.open(full_path)
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except FileNotFoundError:
        log_to_file_debug_globally(f"Image file not found: {full_path}", "WARNING")
    except Exception as e:
        log_to_file_debug_globally(f"Error loading image {full_path}: {e}", "ERROR")
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
    def __init__(self, master, text, command, theme, width=26, height=1, icon_path=None, icon_size=(14,14), state=tk.NORMAL, **kwargs): # Default width=26
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

        super().__init__(
            master, text=text, command=command, font=kwargs.pop('font', BTN_FONT),
            bg=bg_color, fg=fg_color,
            activebackground=active_bg_color, activeforeground=active_fg_color,
            bd=0, relief="flat", cursor="hand2", height=height, width=width,
            padx=kwargs.pop('padx', 3 if self.icon_image else 6), 
            pady=kwargs.pop('pady', 2), 
            image=self.icon_image, compound=tk.LEFT if self.icon_image else tk.NONE,
            state=state, **kwargs)

        self.theme = theme
        self.default_bg = bg_color
        self.hover_bg = active_bg_color
        self.config(highlightbackground=theme.get("BTN_BORDER", theme["ACCENT"]), highlightthickness=1)

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
                base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                dbfile = os.path.join(base_dir, "operation_log.db")
                os.makedirs(os.path.dirname(dbfile), exist_ok=True)
                with open(dbfile, "a") as f_db_check:
                    os.utime(dbfile, None)
                log_to_file_debug_globally(f"DBLogger: DB file path set to: {dbfile}")
            except Exception as e_db_path1:
                log_to_file_debug_globally(f"DBLogger: Failed to create DB at primary path {dbfile}: {e_db_path1}", "WARNING")
                try:
                    user_dir = os.path.expanduser("~")
                    dbfile_fallback = os.path.join(user_dir, ".UltimatUnlockTool", "operation_log.db")
                    os.makedirs(os.path.dirname(dbfile_fallback), exist_ok=True)
                    with open(dbfile_fallback, "a") as f_db_check_fb:
                         os.utime(dbfile_fallback, None)
                    dbfile = dbfile_fallback
                    log_to_file_debug_globally(f"DBLogger: DB file path set to fallback: {dbfile}")
                except Exception as e_db_path2:
                    log_to_file_debug_globally(f"DBLogger: Failed to create DB at fallback path {dbfile_fallback}: {e_db_path2}", "ERROR")
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
                                           theme=theme, width=20, height=1, icon_path=None, state=tk.DISABLED)
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
            try:
                flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                out = subprocess.check_output(['adb', 'get-state'], stderr=subprocess.STDOUT, text=True, timeout=2, creationflags=flags)
                if "device" in out:
                    stat = self.labels["adb_status_connected"]
                    color = self.theme.get("LOG_FG_SUCCESS", "#4CAF50")
            except Exception: pass

            if self.winfo_exists() and self.master.winfo_exists():
                 self.master.after(0, lambda s=stat, c=color: self.set_status(s, c))

            if self.winfo_exists():
                 self._check_adb_after_id = self.after(5000, self._check_adb)

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

        if parent_width < 50 or parent_height < 50:
             parent_width = self.parent.winfo_screenwidth()
             parent_height = self.parent.winfo_screenheight()
             parent_x = 0
             parent_y = 0

        x = parent_x + (parent_width // 2) - (380 // 2)
        y = parent_y + (parent_height // 2) - (580 // 2)
        self.geometry(f"+{x}+{y}")

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
                icon_filename = f"{icon_name_key.replace('_login','')}.png"
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


        self.grab_set()
        self.focus_set()
        self.username_entry.focus()

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
                                 parent=self)
            self.password_entry.delete(0, tk.END)
            self.username_entry.focus()

    def _on_closing_login(self):
        log_to_file_debug_globally("Login window closed by user. Exiting application.")
        self.parent.destroy()

class AppController:
    def __init__(self):
        log_to_file_debug_globally("AppController __init__ started.")
        self.root = tk.Tk()

        app_images['app_icon'] = load_image("logo.png")
        if app_images.get('app_icon'):
            self.root.iconphoto(True, app_images['app_icon'])
        else:
            try:
                 self.root.iconbitmap("logo.ico")
            except Exception:
                 log_to_file_debug_globally("Failed to set window icon from logo.png or logo.ico.", "WARNING")


        self.root.withdraw()

        self.lang = "en" 
        self.theme_mode = "light" 
        self.labels = get_labels(self.lang)
        self.theme = get_theme(self.theme_mode)

        self.main_app_window = None
        self.cancel_button_ref = None

        app_images['telegram_icon'] = load_image("telegram_icon.png", size=(18,18)) 
        app_images['telegram_icon_small'] = load_image("telegram_icon.png", size=(14,14)) # Made small icon consistent

        self.login_window = LoginWindow(self.root, self)
        log_to_file_debug_globally("LoginWindow instantiated.")

    def start(self):
        log_to_file_debug_globally("AppController start, entering root.mainloop().")
        self.root.mainloop()

    def show_main_app(self):
        log_to_file_debug_globally("show_main_app called.")
        self.root.deiconify()
        first_time_showing_main_app = False
        if self.main_app_window is None:
            self.main_app_window = UltimateDeviceTool(master_tk_instance=self.root, app_controller=self)
            first_time_showing_main_app = True
            log_to_file_debug_globally("UltimateDeviceTool instantiated as main_app_window.")
        else:
            log_to_file_debug_globally("Main app window already exists, deiconifying.", "WARNING")
            if isinstance(self.main_app_window, UltimateDeviceTool) and self.main_app_window.winfo_exists():
                 self.main_app_window.master.deiconify()
            else: 
                 self.main_app_window = UltimateDeviceTool(master_tk_instance=self.root, app_controller=self)
                 first_time_showing_main_app = True 
        
        if first_time_showing_main_app:
            try:
                webbrowser.open("https://ultimat-unlock.com/")
                log_to_file_debug_globally("Website https://ultimat-unlock.com/ opened automatically.")
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

        app_images['title_logo'] = load_image("logo.png", size=(38, 38))

        self.db_logger = DBLogger(tk_root=self.master)
        log_to_file_debug_globally("Instance variables (lang, theme, db_logger) initialized.")

        self.master.title(self.labels["title"])
        self.master.geometry("1450x820") 
        self.master.wm_minsize(1200, 750) 
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing)
        log_to_file_debug_globally("Window properties (title, geometry, minsize, protocol) set on master.")

        self.pack(fill=tk.BOTH, expand=True)

        self._apply_styles()
        self._build_ui()
        self.command_queue = queue.Queue()
        self.current_popen_process = None
        self.after_id_process_command_queue = self.after(100, self._process_command_queue)
        log_to_file_debug_globally("UltimateDeviceTool __init__ finished successfully.")

    def _apply_styles(self):
        log_to_file_debug_globally("Applying styles...")
        self.style = ttk.Style(self.master)
        try:
            self.style.theme_use('clam') 
        except tk.TclError:
            log_to_file_debug_globally("Clam theme not available. Default theme will be used.", "WARNING")

        self.style.configure("TNotebook", background=self.theme["BG"], borderwidth=0, tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab",
                             background=self.theme.get("NOTEBOOK_TAB_BG", self.theme["GROUP_BG"]),
                             foreground=self.theme.get("NOTEBOOK_TAB_FG", self.theme["FG"]),
                             padding=[10, 5], font=("Segoe UI", 9, "bold"), borderwidth=0, 
                             relief="flat")
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.theme.get("NOTEBOOK_TAB_SELECTED_BG", self.theme["ACCENT"])),
                                   ("active", self.theme.get("NOTEBOOK_TAB_ACTIVE_BG", self.theme["ACCENT2"]))],
                       foreground=[("selected", self.theme.get("NOTEBOOK_TAB_SELECTED_FG", self.theme["BTN_FG"]))],
                       relief=[("selected", "flat")])

        self.style.configure("TPanedwindow", background=self.theme["BG"])
        self.style.configure("TFrame", background=self.theme["BG"])
        log_to_file_debug_globally("Styles applied.")

    def _build_ui(self):
        log_to_file_debug_globally("Building UI...")
        self.config(bg=self.theme["BG"])

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

        self.status_bar = StatusBar(self, self.theme, self.labels)

        bottom_buttons_frame = tk.Frame(self, bg=self.theme["BG"])

        green_button_bg = "#00B050"  
        green_button_fg = "#FFFFFF"  
        green_button_active_bg = "#008C40" 

        ModernButton(bottom_buttons_frame, text=self.labels.get("btn_telegram_channel", "Telegram Channel"),
                     command=lambda: webbrowser.open("https://t.me/UltimatUnlock1"),
                     theme=self.theme, width=18, icon_path="telegram_icon.png", icon_size=(14,14), 
                     padx=3, pady=2, font=("Segoe UI", 9, "bold"), 
                     bg=green_button_bg, fg=green_button_fg, activebackground=green_button_active_bg, activeforeground=green_button_fg
                     ).pack(side=tk.LEFT, padx=(10,5), pady=2)

        ModernButton(bottom_buttons_frame, text=self.labels.get("btn_contact_support", "Contact Support"),
                     command=lambda: webbrowser.open("https://t.me/UltimatUnlock"),
                     theme=self.theme, width=18, icon_path="telegram_icon.png", icon_size=(14,14), 
                     padx=3, pady=2, font=("Segoe UI", 9, "bold"), 
                     bg=green_button_bg, fg=green_button_fg, activebackground=green_button_active_bg, activeforeground=green_button_fg
                     ).pack(side=tk.LEFT, padx=5, pady=2)
        
        ModernButton(bottom_buttons_frame, text=self.labels.get("btn_group_support", "Group Support"),
                     command=lambda: webbrowser.open("https://t.me/SYRIANUNLOCKER1"),
                     theme=self.theme, width=18, icon_path="telegram_icon.png", icon_size=(14,14), 
                     padx=3, pady=2, font=("Segoe UI", 9, "bold"), 
                     bg=green_button_bg, fg=green_button_fg, activebackground=green_button_active_bg, activeforeground=green_button_fg
                     ).pack(side=tk.LEFT, padx=5, pady=2)


        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,2), padx=0)


        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL, style="TPanedwindow")
        body.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_area_container = tk.Frame(body, bg=self.theme["BG"])
        right_area_container = tk.Frame(body, bg=self.theme["BG"])
        
        body.add(left_area_container, weight=3) 
        body.add(right_area_container, weight=1)

        def set_sash_position_after_delay():
            try:
                self.master.update_idletasks() 
                total_width = body.winfo_width()
                if total_width > 1:
                    sash_pos = int(total_width * 0.72) 
                    min_right_width = 300 
                    if total_width - sash_pos < min_right_width:
                        sash_pos = total_width - min_right_width
                    if sash_pos > 50: 
                        body.sashpos(0, sash_pos)
                        log_to_file_debug_globally(f"PanedWindow sash set to {sash_pos} (total: {total_width})")
                    else:
                        log_to_file_debug_globally(f"Calculated sash position {sash_pos} too small, not setting.", "WARNING")
                else:
                    log_to_file_debug_globally("PanedWindow total_width is not > 1 for sash setting.", "WARNING")
            except tk.TclError as e:
                log_to_file_debug_globally(f"TclError setting sash position: {e}", "WARNING")
            except Exception as e_sash_generic:
                log_to_file_debug_globally(f"Generic error setting sash position: {e_sash_generic}", "ERROR")

        self.master.after(150, set_sash_position_after_delay) 


        header_frame = tk.Frame(left_area_container, bg=self.theme["BG"])
        header_frame.pack(fill=tk.X, pady=(10, 5), padx=(15,0))

        if app_images.get('title_logo'):
            logo_label = tk.Label(header_frame, image=app_images['title_logo'], bg=self.theme["BG"])
            logo_label.image = app_images['title_logo']
            logo_label.pack(side=tk.LEFT, padx=(0,10), pady=0)

        title_text_frame = tk.Frame(header_frame, bg=self.theme["BG"])
        title_text_frame.pack(side=tk.LEFT, anchor=tk.W, pady=0)
        tk.Label(title_text_frame, text=self.labels["title"], font=APP_LOGO_TITLE_FONT, bg=self.theme["BG"], fg=self.theme.get("TITLE_FG", self.theme["ACCENT"]) ).pack(anchor=tk.NW)
        tk.Label(title_text_frame, text=self.labels["edition"], font=SUBTITLE_FONT, bg=self.theme["BG"], fg=self.theme.get("EDITION_FG", self.theme["FG"]) ).pack(anchor=tk.NW)

        # Simplified ADB Status Bar (replaces Device Status Panel)
        self.adb_status_bar_top = tk.Frame(left_area_container, bg=self.theme.get("DEVICE_STATUS_BG", self.theme["GROUP_BG"]), relief="groove", bd=1)
        self.adb_status_bar_top.pack(fill=tk.X, padx=15, pady=(5,10))
        self.adb_status_label_top_var = tk.StringVar(value=self.labels.get("adb_status_not_connected", "ADB: Not Connected"))
        self.adb_status_label_top_widget = tk.Label(self.adb_status_bar_top, textvariable=self.adb_status_label_top_var,
                                              font=DEVICE_STATUS_FONT_LABEL, # Using label font for prominence
                                              bg=self.theme.get("DEVICE_STATUS_BG", self.theme["GROUP_BG"]),
                                              fg=self.theme.get("LOG_FG_ERROR", "#F44336"), # Default to error color
                                              padx=10, pady=5)
        self.adb_status_label_top_widget.pack(fill=tk.X)
        self._update_top_adb_status_bar() # Initial update


        self.notebook = ttk.Notebook(left_area_container, style="TNotebook")
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=15, pady=(0,15))

        try:
            self.log_panel = LogPanel(right_area_container, self.theme, self.labels, db_logger=self.db_logger, tk_root=self.master, app_controller=self.app_controller)
            self.log_panel.pack(fill=tk.BOTH, expand=True, padx=(5,15), pady=(15,15))
            log_to_file_debug_globally("Log panel created.")
        except Exception as e_log_panel:
            log_to_file_debug_globally(f"Error creating LogPanel: {e_log_panel}", "CRITICAL")
            traceback.print_exc(file=open(_DEBUG_LOG_PATH, "a"))

        tabs_to_add = [
            (SamsungTab, "tab_samsung"),
            (HonorTab, "tab_honor"),
            (XiaomiTab, "tab_xiaomi"),
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
                traceback.print_exc(file=open(_DEBUG_LOG_PATH, "a"))
                messagebox.showerror("UI Build Error", f"Failed to build {self.labels[label_key]} tab: {e_tab_creation}", parent=self.master)

        log_to_file_debug_globally("UI Building finished.")

    def _update_top_adb_status_bar(self):
        if not self.winfo_exists() or not hasattr(self, 'status_bar') or not self.status_bar.winfo_exists():
            if hasattr(self, 'adb_status_label_top_var'): # Schedule retry if status bar not ready
                 self.master.after(200, self._update_top_adb_status_bar)
            return

        adb_full_status_bottom = self.status_bar.cget("text")
        current_text = self.adb_status_label_top_var.get()
        new_text = ""
        new_color = self.theme.get("LOG_FG_ERROR", "#F44336") # Default to error color

        if self.labels.get("adb_status_connected") in adb_full_status_bottom:
            new_text = self.labels.get("adb_status_connected", "ADB: Connected")
            new_color = self.theme.get("LOG_FG_SUCCESS", "#4CAF50")
        else: # Covers "Not Connected" and any other states from bottom bar
            new_text = self.labels.get("adb_status_not_connected", "ADB: Not Connected")
            # Color remains error/default for not connected

        if current_text != new_text or self.adb_status_label_top_widget.cget("fg") != new_color :
            self.adb_status_label_top_var.set(new_text)
            if self.adb_status_label_top_widget.winfo_exists():
                 self.adb_status_label_top_widget.config(fg=new_color)
        
        if self.winfo_exists(): # Keep polling
            self.master.after(1000, self._update_top_adb_status_bar)


    def _build_device_status_widgets(self, parent_frame):
        # This method is now simplified to only update the top ADB status bar
        # The actual creation of the top ADB status bar is in _build_ui
        # This function will be called by action_refresh_device_status,
        # but its primary role is now just to trigger the update of the top bar.
        self._update_top_adb_status_bar()


    def action_refresh_device_status(self, initial_load=False):
        # This now primarily triggers an update of the top ADB status bar
        # The detailed device info (model, android, root) is no longer displayed here.
        if not initial_load and self.log_panel:
            self.log_panel.log("Refreshing ADB connection status...", "info", include_timestamp=False)
        
        self._update_top_adb_status_bar() # Directly call the update for the top bar


    def _update_cancel_button_state(self, enable=False):
        if self.app_controller and self.app_controller.cancel_button_ref:
            button = self.app_controller.cancel_button_ref
            if button.winfo_exists():
                 button.config(state=tk.NORMAL if enable else tk.DISABLED)
                 if not enable:
                     button.config(bg=self.theme.get("GROUP_BG", "#ECEFF1" if self.theme["BG"] == "#ECEFF1" else "#2C313A"), 
                                   fg=self.theme.get("NOTEBOOK_TAB_FG", "#AAB8C5"))
                 else:
                     button.config(bg=self.theme["BTN_BG"], fg=self.theme["BTN_FG"])


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
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE

                process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           text=True, encoding='utf-8', errors='replace',
                                           startupinfo=startupinfo,
                                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                self.current_popen_process = process
                stdout, stderr = process.communicate(timeout=120) 
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
                if process and process.returncode is not None and process.returncode < 0 : 
                     self.command_queue.put({"error": "Cancelled", "operation_name": operation_name, "command": command_list, "callback": callback_on_finish, "is_part_of_sequence": is_part_of_sequence, "is_info_gathering": is_info_gathering})
                else:
                     log_to_file_debug_globally(f"Exception for {operation_name} ({command_str_for_debug}): {e}", "ERROR")
                     traceback.print_exc(file=open(_DEBUG_LOG_PATH, "a"))
                     self.command_queue.put({"error": str(e), "operation_name": operation_name, "command": command_list, "callback": callback_on_finish, "is_part_of_sequence": is_part_of_sequence, "is_info_gathering": is_info_gathering})
            finally:
                self.current_popen_process = None

        threading.Thread(target=_command_thread, daemon=True).start()

    def _process_command_queue(self):
        try:
            while not self.command_queue.empty():
                result = self.command_queue.get_nowait()
                self._handle_command_result(result)
        except Exception as e:
            log_to_file_debug_globally(f"Error in _process_command_queue: {e}", "ERROR")
            traceback.print_exc(file=open(_DEBUG_LOG_PATH, "a"))
        finally:
            if self.winfo_exists(): 
                self.after_id_process_command_queue = self.after(100, self._process_command_queue)


    def _handle_command_result(self, result):
        log_panel_available = hasattr(self, 'log_panel') and self.log_panel is not None and self.log_panel.winfo_exists()
        log_method = self.log_panel.log if log_panel_available else log_to_file_debug_globally

        operation_name = result.get("operation_name", "Unknown Operation")
        is_part_of_sequence = result.get("is_part_of_sequence", False)
        is_info_gathering = result.get("is_info_gathering", False)

        if is_info_gathering and "error" not in result and result.get("return_code") == 0:
            pass
        elif is_part_of_sequence: 
            if "error" in result:
                log_method(f"Step Error ({operation_name}): {result['error']}", "error", indent=1, include_timestamp=False)
            elif result.get("return_code", -1) != 0:
                stderr = result.get("stderr", "").strip()
                stdout = result.get("stdout", "").strip()
                details = stderr if stderr else stdout
                log_method(f"Step Failed ({operation_name}): {details.splitlines()[0] if details else 'Unknown reason'}", "error", indent=1, include_timestamp=False)
            else: 
                stdout = result.get("stdout", "").strip()
                if stdout and not any(kw in stdout.lower() for kw in ["success", "already", "performed", "daemon started successfully", ""]):
                     log_method(f"Step OK: {stdout.splitlines()[0]}", "info", indent=1, include_timestamp=False)
        else: 
            if "error" in result:
                error_type = result["error"]
                error_message_summary = ""
                if error_type == "TimeoutExpired": error_message_summary = "Operation timed out"
                elif error_type == "FileNotFound": error_message_summary = f"Command '{result.get('command_name', 'N/A')}' not found. Ensure ADB/Fastboot is in PATH."
                elif error_type == "Cancelled": error_message_summary = "Operation cancelled by user"
                else: error_message_summary = f"Error - {error_type}"
                log_method(f"{operation_name}: {error_message_summary}", "error", include_timestamp=True)
            else:
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                return_code = result.get("return_code", -1)

                if not operation_name.startswith("Get Property"): 
                    if return_code == 0:
                        log_method(f"{operation_name}: Completed successfully.", "success", include_timestamp=True)
                        if stdout.strip() and not any(kw in stdout.lower() for kw in ["success", "already", "performed", "daemon started successfully"]):
                            summary_stdout = stdout.strip().splitlines()[0]
                            if len(summary_stdout) > 100: summary_stdout = summary_stdout[:100] + "..."
                            log_method(f"Detail: {summary_stdout}", "info", indent=1, include_timestamp=False)
                        if stderr.strip():
                            summary_stderr = stderr.strip().splitlines()[0]
                            if len(summary_stderr) > 100: summary_stderr = summary_stderr[:100] + "..."
                            log_method(f"Output (stderr): {summary_stderr}", "warning", indent=1, include_timestamp=False)
                    else: 
                        log_method(f"{operation_name}: Failed (Code: {return_code}).", "fail", include_timestamp=True)
                        details = stderr.strip() if stderr.strip() else stdout.strip()
                        if details:
                            summary_details = details.splitlines()[0]
                            if len(summary_details) > 120: summary_details = summary_details[:120] + "..."
                            log_method(f"Error Details: {summary_details}", "error", indent=1, include_timestamp=False)
                        else:
                            log_method("No specific error message from command.", "error", indent=1, include_timestamp=False)

        if log_panel_available and not is_part_of_sequence and not is_info_gathering:
            if self.log_panel.progress_bar.running: self.log_panel.progress_bar.stop()
            self._update_cancel_button_state(enable=False)

        callback = result.get("callback")
        if callback and callable(callback):
            try:
                callback(result)
            except Exception as e_callback:
                log_to_file_debug_globally(f"Error in command callback for {operation_name}: {e_callback}", "ERROR")
                traceback.print_exc(file=open(_DEBUG_LOG_PATH, "a"))


    def action_cancel_operation(self):
        if self.current_popen_process and self.current_popen_process.poll() is None:
            try:
                self.current_popen_process.terminate() 
                log_msg = "Attempting to cancel current operation..."
                if hasattr(self, 'log_panel') and self.log_panel and self.log_panel.winfo_exists():
                    self.log_panel.log(log_msg, "warning", include_timestamp=False)
                else:
                    log_to_file_debug_globally(log_msg, "WARNING")
            except Exception as e:
                log_msg = f"Error during cancellation: {e}"
                if hasattr(self, 'log_panel') and self.log_panel and self.log_panel.winfo_exists():
                    self.log_panel.log(log_msg, "error", include_timestamp=True)
                else:
                    log_to_file_debug_globally(log_msg, "ERROR")
        else:
            log_msg = "No operation currently running to cancel."
            if hasattr(self, 'log_panel') and self.log_panel and self.log_panel.winfo_exists():
                self.log_panel.log(log_msg, "info", include_timestamp=False)
            else:
                log_to_file_debug_globally(log_msg, "INFO")
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

            # No longer updating the removed device status panel with model/android/root here
            # The simplified top ADB status bar is updated by _update_top_adb_status_bar() via the main status_bar

            if log_panel_available:
                self.log_panel.log_device_info_block(collected_props_display_keys)

            if next_operation_command:
                if log_panel_available:
                     self.log_panel.log(self.labels.get("log_operation_started", "Operation Started: ") + next_operation_name, "info", indent=1, include_timestamp=True)

                self.execute_command_async(
                    next_operation_command,
                    operation_name=next_operation_name,
                    callback_on_finish=_after_next_operation_completed,
                    is_part_of_sequence=False 
                )
            else:
                if log_panel_available:
                    self.log_panel.log(self.labels.get(operation_label_key_on_success, "Operation successful."), "success", include_timestamp=True)
                    if self.log_panel.progress_bar.running: self.log_panel.progress_bar.stop()
                    self._update_cancel_button_state(enable=False)
                if callback_after_info_and_op:
                    callback_after_info_and_op({"return_code": 0, "device_info": collected_props_display_keys})

        def _after_next_operation_completed(result):
            if callback_after_info_and_op:
                callback_after_info_and_op({"return_code": result.get("return_code", -1),
                                            "device_info": collected_props_display_keys,
                                            "operation_result": result})
            if log_panel_available:
                if self.log_panel.progress_bar.running : self.log_panel.progress_bar.stop()
                self._update_cancel_button_state(enable=False)


        self.get_detailed_adb_info_props(callback_after_all_props=_after_all_props_fetched_for_operation)


    def get_detailed_adb_info_props(self, callback_after_all_props=None):
        collected_props_internal_keys = {}
        remaining_props_count = len(DEVICE_INFO_PROPERTIES)

        def _after_single_prop_fetch(result_single_prop):
            nonlocal remaining_props_count
            prop_key_fetched = "unknown_prop"
            if result_single_prop.get("command") and len(result_single_prop["command"]) > 3:
                prop_key_fetched = result_single_prop["command"][3]

            if result_single_prop.get("return_code") == 0:
                stdout_val = result_single_prop.get("stdout", "").strip()
                collected_props_internal_keys[prop_key_fetched] = stdout_val if stdout_val else ""
            else:
                collected_props_internal_keys[prop_key_fetched] = "Error fetching"

            remaining_props_count -= 1

            if remaining_props_count <= 0:
                if callback_after_all_props and callable(callback_after_all_props):
                    callback_after_all_props(collected_props_internal_keys)

        for _, prop_to_fetch_key in DEVICE_INFO_PROPERTIES:
            self.execute_command_async(
                ["adb", "shell", "getprop", prop_to_fetch_key],
                operation_name=f"Get Property ({prop_to_fetch_key})",
                callback_on_finish=_after_single_prop_fetch,
                is_part_of_sequence=True,
                is_info_gathering=True
            )


    def set_language(self, lang):
        if lang in LABELS:
            self.app_controller.lang = lang
            self.lang = lang
            self.labels = get_labels(self.lang)
            self._rebuild_ui()
            log_to_file_debug_globally(f"Language changed to {lang}.")
        else:
            log_to_file_debug_globally(f"Language {lang} not supported.", "WARNING")

    def set_theme(self, theme_name):
        if theme_name in THEMES:
            self.app_controller.theme_mode = theme_name
            self.theme_mode = theme_name
            self.theme = get_theme(theme_name)
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
            except tk.TclError: pass

        # No need to save status_vars as the panel is removed/simplified
        # temp_status_vars = None
        # if hasattr(self, 'status_vars'):
        #     temp_status_vars = {k: v.get() for k, v in self.status_vars.items()}

        children_to_destroy = list(self.winfo_children())
        for widget in children_to_destroy:
            if widget.winfo_exists():
                 widget.destroy()

        self._apply_styles()
        self._build_ui() # This will now build the simplified ADB status bar

        if hasattr(self, 'notebook') and self.notebook.winfo_exists():
            try:
                if self.notebook.tabs(): 
                    num_tabs = len(self.notebook.tabs())
                    if num_tabs > 0:
                         self.notebook.select(current_tab_index if current_tab_index < num_tabs else 0)
            except tk.TclError:
                log_to_file_debug_globally("Error selecting tab after UI rebuild, or no tabs exist.", "WARNING")

        # No need to restore status_vars as the panel is removed/simplified
        # if temp_status_vars and hasattr(self, 'status_vars'):
        #     for key, value in temp_status_vars.items():
        #         if key in self.status_vars:
        #             self.status_vars[key].set(value)
        # elif hasattr(self, 'adb_status_bar_top'): # Check for the new simplified bar
        self.action_refresh_device_status(initial_load=True) # This will update the new bar

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
            self.master.destroy()

class SamsungTab(ttk.Frame):
    def __init__(self, parent_notebook, master_app: UltimateDeviceTool):
        log_to_file_debug_globally("SamsungTab __init__ started.")
        super().__init__(parent_notebook, style="TFrame")
        self.master_app = master_app
        self.labels = master_app.labels
        self.theme = master_app.theme
        self.configure(padding=(15,15))

        self.num_frp_steps = 0
        self.current_frp_step = 0
        self.current_package_disable_step = 0
        self.num_package_disable_steps = 0
        self.package_list_for_disable = []


        container = tk.Frame(self, bg=self.theme.get("BG", "#ECEFF1")) 
        container.pack(fill=tk.BOTH, expand=True)

        group_samsung = tk.LabelFrame(container, text=self.labels.get("group_samsung", "Samsung ADB Repair & Utilities"),
                                    font=LABEL_FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                                    fg=self.theme.get("FG", "#263238"), padx=15, pady=15, relief="groove", bd=2)
        group_samsung.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        col1_frame = tk.Frame(group_samsung, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        col1_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10), anchor=tk.N)

        ModernButton(col1_frame, text=self.labels.get("btn_get_detailed_info"),
                                   command=self.action_read_device_info, theme=self.theme, width=30).pack(pady=4, anchor=tk.W) 
        ModernButton(col1_frame, text=self.labels.get("btn_reboot_rec", "Reboot Recovery"),
                                       command=self.action_reboot_recovery, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(col1_frame, text=self.labels.get("btn_reboot_dl", "Reboot Download"),
                                       command=self.action_reboot_download, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(col1_frame, text=self.labels.get("btn_reboot_bl", "Reboot Bootloader"),
                                       command=self.action_reboot_bootloader, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(col1_frame, text=self.labels.get("btn_remove_mdm"),
                                   command=self.action_remove_mdm_adb, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)


        col2_frame = tk.Frame(group_samsung, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        col2_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10,0), anchor=tk.N)

        ModernButton(col2_frame, text=self.labels.get("btn_remove_frp", "Remove FRP (ADB)"),
                                       command=self.action_remove_frp_adb, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_factory_reset", "Factory Reset (ADB)"),
                                       command=self.action_factory_reset_adb, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_screenlock_reset", "Reset Screen Lock (ADB)"),
                                       command=self.action_reset_screenlock_adb, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_arabize_device", "Arabize Device (ADB)"),
                                       command=self.action_arabize_device, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_open_browser_adb", "Open Browser (ADB)"),
                                       command=self.action_open_browser_adb, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(col2_frame, text=self.labels.get("btn_bypass_knox"),
                                   command=self.action_bypass_knox_adb, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)

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
            self.master_app.log_panel.log(self.labels.get(operation_name_key, "Starting package disable sequence..."), "info", include_timestamp=True)
            self.master_app.log_panel.progress_bar.set_value(0) 
            self.master_app._update_cancel_button_state(enable=True)


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
        else: 
            if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
                self.master_app.log_panel.log(self.labels.get(self.current_operation_success_log_key, "Package disable sequence attempted."), "success", include_timestamp=True)
                self.master_app.log_panel.progress_bar.set_value(100)
                self.master_app.after(100, lambda: self.master_app.log_panel.progress_bar.stop() if self.master_app.log_panel and self.master_app.log_panel.winfo_exists() and self.master_app.log_panel.progress_bar.running else None)
                self.master_app._update_cancel_button_state(enable=False)

    def _package_disable_step_callback(self, result):
        self.current_package_disable_step += 1
        is_last_step = (self.current_package_disable_step >= self.num_package_disable_steps)

        if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
            progress_percentage = int((self.current_package_disable_step / self.num_package_disable_steps) * 100)
            self.master_app.log_panel.progress_bar.set_value(progress_percentage)

        if result.get("error") == "Cancelled":
            if self.master_app.log_panel:
                self.master_app.log_panel.log("Package disable sequence cancelled by user.", "warning", include_timestamp=True)
            if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
                if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
            self.master_app._update_cancel_button_state(enable=False)
            return

        if not is_last_step:
            self._execute_next_package_disable_step()
        else:
            self._execute_next_package_disable_step()


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
        
        self.master_app.fetch_and_log_device_info(
            operation_label_key_on_success="log_mdm_remove_ok", 
            callback_after_info_and_op=lambda info_result: self._start_package_disable_sequence(
                MDM_PACKAGES,
                "log_mdm_remove_start",
                "log_mdm_remove_ok",
                "log_mdm_remove_fail"
            ) if info_result.get("return_code") == 0 else (
                self.master_app.log_panel.log("Could not get device info before MDM removal. Aborting.", "error") if self.master_app.log_panel else None,
                self.master_app.log_panel.progress_bar.stop() if self.master_app.log_panel and self.master_app.log_panel.progress_bar.running else None,
                self.master_app._update_cancel_button_state(enable=False)
            ),
            next_operation_name=self.labels.get("btn_remove_mdm") 
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
        
        self.master_app.fetch_and_log_device_info(
            operation_label_key_on_success="log_knox_bypass_ok", 
            callback_after_info_and_op=lambda info_result: self._start_package_disable_sequence(
                KNOX_PACKAGES,
                "log_knox_bypass_start",
                "log_knox_bypass_ok",
                "log_knox_bypass_fail"
            ) if info_result.get("return_code") == 0 else (
                self.master_app.log_panel.log("Could not get device info before Knox bypass. Aborting.", "error") if self.master_app.log_panel else None,
                self.master_app.log_panel.progress_bar.stop() if self.master_app.log_panel and self.master_app.log_panel.progress_bar.running else None,
                self.master_app._update_cancel_button_state(enable=False)
            ),
            next_operation_name=self.labels.get("btn_bypass_knox")
        )

    def action_remove_frp_adb(self):
        if not messagebox.askokcancel(
            self.labels.get("frp_reset_warning_title", "FRP Reset Attempt"),
            self.labels.get("frp_reset_warning_message", "This will attempt a series of ADB commands... Proceed with caution."),
            icon=messagebox.WARNING,
            parent=self.master_app.master):
            if self.master_app.log_panel: self.master_app.log_panel.log("FRP Reset (ADB) cancelled by user.", "info", include_timestamp=True)
            return

        def _start_frp_sequence_after_info(info_result):
            if info_result.get("return_code") != 0:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log("Could not get complete device info before FRP reset. Aborting FRP.", "error", include_timestamp=True)
                    if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                    self.master_app._update_cancel_button_state(enable=False)
                return

            if self.master_app.log_panel:
                self.master_app.log_panel.log("Starting FRP Reset sequence (ADB)...", "info", indent=0, include_timestamp=True)

            self.commands_frp_sequence = [
                (["adb", "shell", "settings", "put", "global", "setup_wizard_has_run", "1"], "Set setup_wizard_has_run to 1"),
                (["adb", "shell", "settings", "put", "secure", "user_setup_complete", "1"], "Set user_setup_complete (secure table)"),
                (["adb", "shell", "settings", "put", "global", "device_provisioned", "1"], "Set device_provisioned to 1"),
                (["adb", "shell", "content", "insert", "--uri", "content://settings/secure", "--bind", "name:s:user_setup_complete", "--bind", "value:s:1"], "Insert user_setup_complete via content provider"),
            ]
            self.num_frp_steps = len(self.commands_frp_sequence)
            self.current_frp_step = 0

            if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
                self.master_app.log_panel.progress_bar.set_value(0)

            self._execute_next_frp_step()

        self.master_app.fetch_and_log_device_info(
            operation_label_key_on_success="log_frp_reset_ok",
            callback_after_info_and_op=_start_frp_sequence_after_info,
            next_operation_name=self.labels.get("btn_remove_frp")
        )


    def _execute_next_frp_step(self):
        if self.current_frp_step < self.num_frp_steps:
            command, op_desc = self.commands_frp_sequence[self.current_frp_step]

            if self.master_app.log_panel: self.master_app.log_panel.log(f"Attempting FRP Step: {op_desc}", "info", indent=1, include_timestamp=False)

            self.master_app.execute_command_async(
                command,
                operation_name=f"FRP Step: {op_desc}",
                callback_on_finish=self._frp_step_callback,
                is_part_of_sequence=True
            )
        else: 
            if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
                self.master_app.log_panel.log(self.labels.get("log_frp_reset_ok", "FRP Reset.... OK"), "success", include_timestamp=True)
                self.master_app.log_panel.progress_bar.set_value(100)
                self.master_app.after(100, lambda: self.master_app.log_panel.progress_bar.stop() if self.master_app.log_panel and self.master_app.log_panel.winfo_exists() and self.master_app.log_panel.progress_bar.running else None)
                self.master_app._update_cancel_button_state(enable=False)


    def _frp_step_callback(self, result):
        self.current_frp_step += 1
        is_last_step = (self.current_frp_step >= self.num_frp_steps)

        if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
            progress_percentage = int((self.current_frp_step / self.num_frp_steps) * 100)
            self.master_app.log_panel.progress_bar.set_value(progress_percentage)

        if result.get("error") == "Cancelled":
            if self.master_app.log_panel: self.master_app.log_panel.log("FRP sequence cancelled.", "warning", include_timestamp=True)
            if self.master_app.log_panel and self.master_app.log_panel.winfo_exists():
                if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                self.master_app._update_cancel_button_state(enable=False)
            return

        if result.get("return_code", 0) != 0 and result.get("error") is None:
            if self.master_app.log_panel: self.master_app.log_panel.log(f"FRP step '{result.get('operation_name')}' may have failed. Continuing...", "warning", indent=1, include_timestamp=False)
        
        if not is_last_step:
            self._execute_next_frp_step()
        else: 
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
            current_sl_step_ref = [0] 

            def _sl_callback_chained(result_of_step, next_step_idx):
                current_sl_step_ref[0] = next_step_idx
                if self.master_app.log_panel:
                    prog = int((current_sl_step_ref[0] / num_sl_steps) * 100)
                    self.master_app.log_panel.progress_bar.set_value(prog)

                if result_of_step.get("error") == "Cancelled":
                    if self.master_app.log_panel:
                        self.master_app.log_panel.log("Screen Lock Reset sequence cancelled.", "warning", include_timestamp=True)
                        if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                    if self.master_app.app_controller.cancel_button_ref.cget('state') == tk.NORMAL : self.master_app._update_cancel_button_state(enable=False)
                    return
                
                if next_step_idx >= num_sl_steps:
                    if self.master_app.log_panel:
                         if not result_of_step.get("error") == "Cancelled":
                            self.master_app.log_panel.log("Attempted screen lock reset commands. Reboot device to check. Effectiveness highly varies.", "info", include_timestamp=True)
                         if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                    if self.master_app.app_controller.cancel_button_ref.cget('state') == tk.NORMAL : self.master_app._update_cancel_button_state(enable=False)
                else:
                    _execute_next_sl_step(next_step_idx)

            def _execute_next_sl_step(step_index):
                cmd, desc = commands_to_try[step_index]
                self.master_app.execute_command_async(
                    cmd,
                    operation_name=f"Reset SL: {desc}",
                    is_part_of_sequence=True,
                    callback_on_finish=lambda res: _sl_callback_chained(res, step_index + 1)
                )
            _execute_next_sl_step(0)
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
            current_arabize_step_ref = [0]

            def _arabize_callback_chained(result_arabize_step, next_idx_arabize):
                current_arabize_step_ref[0] = next_idx_arabize
                if self.master_app.log_panel:
                    prog = int((current_arabize_step_ref[0] / num_arabize_steps) * 100)
                    self.master_app.log_panel.progress_bar.set_value(prog)

                if result_arabize_step.get("error") == "Cancelled":
                    if self.master_app.log_panel:
                        self.master_app.log_panel.log("Arabization sequence cancelled.", "warning", include_timestamp=True)
                        if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                    if self.master_app.app_controller.cancel_button_ref.cget('state') == tk.NORMAL : self.master_app._update_cancel_button_state(enable=False)
                    return

                if next_idx_arabize >= num_arabize_steps:
                     if self.master_app.log_panel:
                        if not result_arabize_step.get("error") == "Cancelled":
                            self.master_app.log_panel.log("Arabization commands sent. Check device. A reboot might be needed. Effectiveness varies.", "success", include_timestamp=True)
                        if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                     if self.master_app.app_controller.cancel_button_ref.cget('state') == tk.NORMAL : self.master_app._update_cancel_button_state(enable=False)
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
        elif url is not None: 
             messagebox.showwarning("Empty URL", "URL cannot be empty.", parent=self.master_app.master)
             if self.master_app.log_panel: self.master_app.log_panel.log("Open Browser: URL was empty.", "info", include_timestamp=False)
        else: 
            if self.master_app.log_panel: self.master_app.log_panel.log("Open Browser action cancelled by user.", "info", include_timestamp=True)


class HonorTab(ttk.Frame):
    def __init__(self, parent_notebook, master_app: UltimateDeviceTool):
        log_to_file_debug_globally("HonorTab __init__ started.")
        super().__init__(parent_notebook, style="TFrame")
        self.master_app = master_app
        self.labels = master_app.labels
        self.theme = master_app.theme
        self.configure(padding=(15,15))

        container = tk.Frame(self, bg=self.theme.get("BG", "#ECEFF1"))
        container.pack(fill=tk.BOTH, expand=True)

        group_honor = tk.LabelFrame(container, text=self.labels.get("group_honor", "Honor Fastboot Tools"),
                                    font=LABEL_FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                                    fg=self.theme.get("FG", "#263238"), padx=10, pady=10, relief="groove", bd=2)
        group_honor.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        ModernButton(group_honor, text=self.labels.get("btn_honor_info", "Read Serial & Software Info"),
                                   command=self.action_honor_info, theme=self.theme, width=32).pack(pady=4, anchor=tk.W)
        ModernButton(group_honor, text=self.labels.get("btn_honor_reboot_bl", "Reboot Bootloader (Honor)"),
                                       command=self.action_honor_reboot_bootloader, theme=self.theme, width=32).pack(pady=4, anchor=tk.W)
        ModernButton(group_honor, text=self.labels.get("btn_honor_reboot_edl", "Reboot EDL (Honor)"),
                                       command=self.action_honor_reboot_edl, theme=self.theme, width=32).pack(pady=4, anchor=tk.W)
        ModernButton(group_honor, text=self.labels.get("btn_honor_wipe_data_cache", "Wipe Data/Cache (Honor)"),
                                       command=self.action_honor_wipe_data_cache, theme=self.theme, width=32).pack(pady=4, anchor=tk.W)

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
                                   command=self.action_honor_remove_frp, theme=self.theme, width=28).pack(side=tk.LEFT, padx=5) 
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
            current_wipe_step_ref = [0]

            def _wipe_callback_chained(result_wipe_step, next_idx_wipe):
                current_wipe_step_ref[0] = next_idx_wipe
                if self.master_app.log_panel:
                    prog = int((current_wipe_step_ref[0] / num_wipe_steps) * 100)
                    self.master_app.log_panel.progress_bar.set_value(prog)

                if result_wipe_step.get("error") == "Cancelled":
                    if self.master_app.log_panel:
                        self.master_app.log_panel.log("Honor Wipe sequence cancelled.", "warning", include_timestamp=True)
                        if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                    if self.master_app.app_controller.cancel_button_ref.cget('state') == tk.NORMAL : self.master_app._update_cancel_button_state(enable=False)
                    return

                if next_idx_wipe >= num_wipe_steps:
                    if self.master_app.log_panel:
                        if not result_wipe_step.get("error") == "Cancelled":
                             self.master_app.log_panel.log("Honor Wipe Data/Cache commands sent. Device may need manual reboot.", "success", include_timestamp=True)
                        if self.master_app.log_panel.progress_bar.running: self.master_app.log_panel.progress_bar.stop()
                    if self.master_app.app_controller.cancel_button_ref.cget('state') == tk.NORMAL : self.master_app._update_cancel_button_state(enable=False)
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
                                   command=self.action_xiaomi_adb_info, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(adb_col1, text=self.labels.get("btn_xiaomi_reboot_normal_adb", "Reboot Normal (ADB)"),
                                   command=lambda: self.master_app.execute_command_async(["adb", "reboot"], "Xiaomi Reboot Normal (ADB)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(adb_col1, text=self.labels.get("btn_xiaomi_reboot_recovery_adb", "Reboot Recovery (ADB)"),
                                   command=lambda: self.master_app.execute_command_async(["adb", "reboot", "recovery"], "Xiaomi Reboot Recovery (ADB)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)

        ModernButton(adb_col2, text=self.labels.get("btn_xiaomi_reboot_fastboot_adb", "Reboot Fastboot (ADB)"),
                                   command=lambda: self.master_app.execute_command_async(["adb", "reboot", "bootloader"], "Xiaomi Reboot Fastboot (ADB)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(adb_col2, text=self.labels.get("btn_xiaomi_reboot_edl_adb", "Reboot EDL (ADB)"),
                                   command=lambda: self.master_app.execute_command_async(["adb", "reboot", "edl"], "Xiaomi Reboot EDL (ADB)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(adb_col2, text=self.labels.get("btn_xiaomi_enable_diag_root", "Enable Diag (ROOT)") + " *",
                                   command=lambda: messagebox.showinfo("Info", "Enable Diag (ROOT) is a placeholder for specific Xiaomi Diag enabling commands, which usually require root, specific device models, and Qualcomm chipsets. Generic commands are not typically available.", parent=self.master_app.master), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)


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
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "getvar", "all"], "Xiaomi Read Info (Fastboot)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(fb_col1, text=self.labels.get("btn_xiaomi_fastboot_read_security", "Read Security (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "oem", "device-info"], "Xiaomi Read Security (Fastboot)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(fb_col1, text=self.labels.get("btn_xiaomi_fastboot_unlock", "Unlock Bootloader (Fastboot)"),
                                   command=self.action_xiaomi_fastboot_unlock, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(fb_col1, text=self.labels.get("btn_xiaomi_fastboot_lock", "Lock Bootloader (Fastboot)"),
                                   command=self.action_xiaomi_fastboot_lock, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)

        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_reboot_sys", "Reboot System (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "reboot"], "Xiaomi Reboot System (Fastboot)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_reboot_fast", "Reboot Fastboot (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "reboot-bootloader"], "Xiaomi Reboot Fastboot (Fastboot)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_reboot_edl", "Reboot EDL (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "oem", "edl"], "Xiaomi Reboot EDL (Fastboot)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_wipe_cache", "Wipe Cache (Fastboot)"),
                                   command=lambda: self.master_app.execute_command_async(["fastboot", "erase", "cache"], "Xiaomi Wipe Cache (Fastboot)"), theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(fb_col2, text=self.labels.get("btn_xiaomi_fastboot_wipe_data", "Wipe Data (Fastboot)"),
                                   command=self.action_xiaomi_fastboot_wipe_data, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        log_to_file_debug_globally("XiaomiTab __init__ finished.")

    def action_xiaomi_adb_info(self):
        self.master_app.fetch_and_log_device_info(
            operation_label_key_on_success="log_read_info_complete",
            next_operation_name=self.labels.get("btn_xiaomi_adb_info")
            )


    def action_xiaomi_fastboot_unlock(self):
        if messagebox.askyesno("Confirm Unlock", "Are you sure you want to unlock the bootloader? This will erase all user data and may void warranty. For Xiaomi, this often requires Mi Unlock Tool and an authorized account.", parent=self.master_app.master):
            self.master_app.execute_command_async(["fastboot", "oem", "unlock"], operation_name="Xiaomi Unlock Bootloader (Attempt)")
            if self.master_app.log_panel: self.master_app.log_panel.log("Note: Xiaomi bootloader unlock often requires official Mi Unlock Tool and account authorization. This command attempts the generic unlock.", "warning", include_timestamp=False)
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

class FileAdvancedTab(ttk.Frame):
    def __init__(self, parent_notebook, master_app: UltimateDeviceTool):
        log_to_file_debug_globally("FileAdvancedTab __init__ started.")
        super().__init__(parent_notebook, style="TFrame")
        self.master_app = master_app
        self.labels = master_app.labels
        self.theme = master_app.theme
        self.configure(padding=(15,15))

        container = tk.Frame(self, bg=self.theme.get("BG", "#ECEFF1"))
        container.pack(fill=tk.BOTH, expand=True)

        group_file = tk.LabelFrame(container, text=self.labels.get("group_file", "File & App Management"),
                                   font=LABEL_FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                                   fg=self.theme.get("FG", "#263238"), padx=10, pady=10, relief="groove", bd=2)
        group_file.pack(pady=(0,10), padx=10, fill=tk.X, expand=False)

        file_cols_container = tk.Frame(group_file, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        file_cols_container.pack(fill=tk.X)
        file_col1 = tk.Frame(file_cols_container, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        file_col1.pack(side=tk.LEFT, fill=tk.Y, padx=(0,5), anchor=tk.N, expand=True)
        file_col2 = tk.Frame(file_cols_container, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        file_col2.pack(side=tk.LEFT, fill=tk.Y, padx=(5,0), anchor=tk.N, expand=True)

        ModernButton(file_col1, text=self.labels.get("btn_pull_file", "Pull File from Device"),
                                   command=self.action_pull_file, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(file_col1, text=self.labels.get("btn_push_file", "Push File to Device"),
                                   command=self.action_push_file, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(file_col1, text=self.labels.get("btn_backup_user_data_adb", "Backup User Data (ADB)"),
                                   command=self.action_backup_user_data, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)

        ModernButton(file_col2, text=self.labels.get("btn_install_apk", "Install APK"),
                                   command=self.action_install_apk, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(file_col2, text=self.labels.get("btn_uninstall_app", "Uninstall App (Legacy)"), 
                                   command=self.action_uninstall_app_legacy, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        ModernButton(file_col2, text=self.labels.get("btn_restore_user_data_adb", "Restore User Data (ADB)"),
                                   command=self.action_restore_user_data, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)
        
        ModernButton(file_col1, text=self.labels.get("btn_pull_contacts_vcf", "Pull Contacts (VCF)"),
                     command=self.action_pull_contacts_vcf, theme=self.theme, width=30).pack(pady=4, anchor=tk.W)


        group_advanced = tk.LabelFrame(container, text=self.labels.get("group_advanced_cmd", "Advanced Command Execution"),
                                       font=LABEL_FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                                       fg=self.theme.get("FG", "#263238"), padx=10, pady=10, relief="groove", bd=2)
        group_advanced.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        tk.Label(group_advanced, text=self.labels.get("advanced_cmd_label", "Enter ADB or Fastboot command:"),
                 font=FONT, bg=self.theme.get("GROUP_BG", self.theme["BG"]),
                 fg=self.theme.get("FG", "#263238")).pack(anchor=tk.W, pady=(5,2))

        self.advanced_cmd_var = tk.StringVar()
        advanced_cmd_entry = tk.Entry(group_advanced, textvariable=self.advanced_cmd_var, width=60, font=FONT,
                                      bg=self.theme.get("LOG_BG", "#CFD8DC"), fg=self.theme.get("FG", "#263238"),
                                      insertbackground=self.theme["FG"], relief="flat", bd=2, highlightthickness=1,
                                      highlightbackground=self.theme.get("ACCENT2", DARK_BLUE_ACCENT2), highlightcolor=self.theme.get("ACCENT", DARK_BLUE_ACCENT))
        advanced_cmd_entry.pack(fill=tk.X, pady=(0,5), ipady=3)
        TextContextMenu(advanced_cmd_entry, self.master_app.master, self.labels)

        ModernButton(group_advanced, text=self.labels.get("btn_run_advanced_cmd", "Run Command"),
                                   command=self.action_run_advanced_cmd, theme=self.theme, width=20).pack(pady=5, anchor=tk.W)
        log_to_file_debug_globally("FileAdvancedTab __init__ finished.")

    def action_pull_file(self):
        device_path = simpledialog.askstring(self.labels.get("pull_file_title", "Pull File from Device"),
                                            self.labels.get("pull_file_device_path_msg", "Enter device source path:"),
                                            parent=self.master_app.master)
        if not device_path or not device_path.strip():
            if self.master_app.log_panel: self.master_app.log_panel.log("Pull file: No device path entered.", "info", include_timestamp=False)
            return

        local_path = filedialog.asksaveasfilename(parent=self.master_app.master, title="Save File As", initialfile=os.path.basename(device_path.strip()))
        if not local_path:
            if self.master_app.log_panel: self.master_app.log_panel.log("Pull file: No local save path selected.", "info", include_timestamp=False)
            return

        self.master_app.execute_command_async(["adb", "pull", device_path.strip(), local_path],
                                             operation_name=f"Pull File: {os.path.basename(device_path.strip())}")

    def action_push_file(self):
        local_path = filedialog.askopenfilename(parent=self.master_app.master, title="Select File to Push")
        if not local_path:
            if self.master_app.log_panel: self.master_app.log_panel.log("Push file: No local file selected.", "info", include_timestamp=False)
            return

        device_path = simpledialog.askstring(self.labels.get("push_file_title", "Push File to Device"),
                                            self.labels.get("push_file_device_path_msg", "Enter device destination path:"),
                                            parent=self.master_app.master, initialvalue=f"/sdcard/{os.path.basename(local_path)}")
        if not device_path or not device_path.strip():
            if self.master_app.log_panel: self.master_app.log_panel.log("Push file: No device path entered.", "info", include_timestamp=False)
            return

        self.master_app.execute_command_async(["adb", "push", local_path, device_path.strip()],
                                             operation_name=f"Push File: {os.path.basename(local_path)}")

    def action_install_apk(self):
        apk_path = filedialog.askopenfilename(title=self.labels.get("install_apk_title", "Select APK to Install"),
                                             filetypes=[("APK Files", "*.apk"), ("All Files", "*.*")],
                                             parent=self.master_app.master)
        if not apk_path:
            if self.master_app.log_panel: self.master_app.log_panel.log("Install APK: No APK file selected.", "info", include_timestamp=False)
            return

        self.master_app.execute_command_async(["adb", "install", "-r", apk_path], 
                                             operation_name=f"Install APK: {os.path.basename(apk_path)}")

    def action_uninstall_app_legacy(self): 
        package_name = simpledialog.askstring(self.labels.get("uninstall_title", "Uninstall App"),
                                             self.labels.get("uninstall_msg", "Enter package name:"),
                                             parent=self.master_app.master)
        if not package_name or not package_name.strip():
            if self.master_app.log_panel: self.master_app.log_panel.log("Uninstall App: No package name entered.", "info", include_timestamp=False)
            return

        self.master_app.execute_command_async(["adb", "uninstall", package_name.strip()],
                                             operation_name=f"Uninstall App: {package_name.strip()}")

    def action_backup_user_data(self):
        backup_file_path = filedialog.asksaveasfilename(
            title=self.labels.get("backup_user_data_title", "Save Backup As"),
            defaultextension=".ab",
            filetypes=[("ADB Backup Files", "*.ab"), ("All Files", "*.*")],
            parent=self.master_app.master
        )
        if not backup_file_path:
            if self.master_app.log_panel: self.master_app.log_panel.log("Backup User Data: Cancelled by user.", "info", include_timestamp=True)
            return
        command = ["adb", "backup", "-f", backup_file_path, "-apk", "-all", "-nosystem"] 
        operation_name = "Backup User Apps Data"

        if self.master_app.log_panel:
            self.master_app.log_panel.log("ADB Backup requires confirmation on the device. The operation will wait.", "warning", include_timestamp=False)
        self.master_app.execute_command_async(command, operation_name=operation_name)


    def action_restore_user_data(self):
        backup_file_path = filedialog.askopenfilename(
            title=self.labels.get("restore_user_data_title", "Select Backup to Restore"),
            filetypes=[("ADB Backup Files", "*.ab"), ("All Files", "*.*")],
            parent=self.master_app.master
        )
        if not backup_file_path:
            if self.master_app.log_panel: self.master_app.log_panel.log("Restore User Data: Cancelled by user.", "info", include_timestamp=True)
            return

        command = ["adb", "restore", backup_file_path]
        operation_name = "Restore User Data"
        if self.master_app.log_panel:
            self.master_app.log_panel.log("ADB Restore requires confirmation on the device. The operation will wait.", "warning", include_timestamp=False)

        self.master_app.execute_command_async(command, operation_name=operation_name)

    def action_pull_contacts_vcf(self):
        if not messagebox.askokcancel(
            self.labels.get("pull_contacts_title", "Pull Contacts"),
            self.labels.get("pull_contacts_confirm_msg", "Attempt to pull contacts...?"),
            icon=messagebox.INFO,
            parent=self.master_app.master):
            if self.master_app.log_panel: self.master_app.log_panel.log("Pull Contacts (VCF) cancelled by user.", "info", include_timestamp=True)
            return

        vcf_path = filedialog.asksaveasfilename(
            title=self.labels.get("pull_contacts_title", "Save Contacts As"),
            defaultextension=".vcf",
            filetypes=[("vCard Files", "*.vcf"), ("All Files", "*.*")],
            parent=self.master_app.master
        )
        if not vcf_path:
            if self.master_app.log_panel: self.master_app.log_panel.log("Pull Contacts: No save path selected.", "info", include_timestamp=False)
            return

        op_name = "Pull Contacts to VCF"
        adb_command = [
            "adb", "shell", "content", "query", "--uri", "content://com.android.contacts/data",
            "--projection", "display_name,data1",
            "--where", "mimetype='vnd.android.cursor.item/phone_v2'"
        ]

        def _contacts_callback(result):
            if result.get("error") or result.get("return_code") != 0:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log(f"{op_name}: Failed to query contacts. Error: {result.get('stderr', 'Unknown')}", "error")
                return

            stdout = result.get("stdout", "")
            if not stdout.strip():
                if self.master_app.log_panel:
                    self.master_app.log_panel.log(self.labels.get("pull_contacts_no_output", "No contacts data retrieved."), "warning")
                return

            vcf_entries = []
            for line in stdout.splitlines():
                if not line.strip().startswith("Row:"): continue
                
                name_match = re.search(r"display_name=([^,]+)", line)
                number_match = re.search(r"data1=([^,]+)", line)

                name = name_match.group(1) if name_match else "Unknown"
                number = number_match.group(1) if number_match else None
                
                if name == "null": name = "Unknown"
                if number == "null": number = None

                if number:
                    vcf_entries.append("BEGIN:VCARD")
                    vcf_entries.append("VERSION:3.0")
                    vcf_entries.append(f"FN:{name.strip()}")
                    vcf_entries.append(f"N:{name.strip()};;;;") 
                    vcf_entries.append(f"TEL;TYPE=CELL:{number.strip()}")
                    vcf_entries.append("END:VCARD")
            
            if not vcf_entries:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log(self.labels.get("pull_contacts_no_output", "No contacts data parsed."), "warning")
                return

            try:
                with open(vcf_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(vcf_entries))
                if self.master_app.log_panel:
                    self.master_app.log_panel.log(f"{op_name}: Contacts saved to {vcf_path}", "success")
            except IOError as e:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log(f"{self.labels.get('pull_contacts_file_error', 'File error')}: {e}", "error")

        self.master_app.execute_command_async(adb_command, operation_name=op_name, callback_on_finish=_contacts_callback)


    def action_run_advanced_cmd(self):
        cmd_str = self.advanced_cmd_var.get().strip()
        if not cmd_str:
            if self.master_app.log_panel: self.master_app.log_panel.log("Advanced Command: No command entered.", "info", include_timestamp=False)
            return

        cmd_parts = cmd_str.split()
        if not cmd_parts:
            if self.master_app.log_panel: self.master_app.log_panel.log("Advanced Command: Command is empty after parsing.", "info", include_timestamp=False)
            return

        if self.master_app.log_panel: self.master_app.log_panel.log(f"Executing: {cmd_str}", "cmd", include_timestamp=False)
        self.master_app.execute_command_async(cmd_parts, operation_name=f"Advanced CMD: {cmd_parts[0]}")


class AppManagerTab(ttk.Frame):
    def __init__(self, parent_notebook, master_app: UltimateDeviceTool):
        log_to_file_debug_globally("AppManagerTab __init__ started.")
        super().__init__(parent_notebook, style="TFrame")
        self.master_app = master_app
        self.labels = master_app.labels
        self.theme = master_app.theme
        self.configure(padding=(15, 15))

        container = tk.Frame(self, bg=self.theme.get("BG", "#ECEFF1"))
        container.pack(fill=tk.BOTH, expand=True)

        controls_frame = tk.Frame(container, bg=self.theme.get("GROUP_BG", self.theme["BG"]))
        controls_frame.pack(fill=tk.X, pady=(0,10), padx=5)
        
        self.filter_var = tk.StringVar(value="all")
        filters = [
            (self.labels.get("app_manager_filter_all", "All"), "all"),
            (self.labels.get("app_manager_filter_third_party", "3rd Party"), "third_party"),
            (self.labels.get("app_manager_filter_system", "System"), "system")
        ]
        for text, val in filters:
            rb = tk.Radiobutton(controls_frame, text=text, variable=self.filter_var, value=val,
                                command=self.action_refresh_app_list,
                                bg=self.theme.get("GROUP_BG"), fg=self.theme.get("FG"), selectcolor=self.theme.get("LOG_BG"),
                                activebackground=self.theme.get("GROUP_BG"), activeforeground=self.theme.get("FG"), font=FONT)
            rb.pack(side=tk.LEFT, padx=5)

        tk.Label(controls_frame, text=self.labels.get("app_manager_search_label", "Search:"),
                 font=FONT, bg=self.theme.get("GROUP_BG"), fg=self.theme.get("FG")).pack(side=tk.LEFT, padx=(10,2))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(controls_frame, textvariable=self.search_var, font=FONT, width=25,
                                bg=self.theme.get("LOG_BG"), fg=self.theme.get("FG"), insertbackground=self.theme.get("FG"))
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_app_list_display())


        ModernButton(controls_frame, text=self.labels.get("btn_refresh_app_list", "Refresh"),
                     command=self.action_refresh_app_list, theme=self.theme, width=12, padx=5).pack(side=tk.RIGHT, padx=5) 

        tree_frame = tk.Frame(container, bg=self.theme.get("BG"))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        self.app_tree = ttk.Treeview(tree_frame, columns=("package", "path"), show="headings", selectmode="browse")
        self.app_tree.heading("package", text="Package Name")
        self.app_tree.heading("path", text="Path")
        self.app_tree.column("package", width=300, anchor=tk.W)
        self.app_tree.column("path", width=400, anchor=tk.W)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.app_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.app_tree.xview)
        self.app_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.app_tree.pack(fill=tk.BOTH, expand=True)
        
        self.app_tree.bind("<Button-3>", self._show_app_context_menu)
        self.app_context_menu = tk.Menu(self.app_tree, tearoff=0, bg=self.theme["GROUP_BG"], fg=self.theme["FG"])
        self.app_context_menu.add_command(label=self.labels.get("btn_copy_package_name", "Copy Package Name"), command=self.action_copy_package_name)
        self.app_context_menu.add_command(label=self.labels.get("btn_uninstall_selected_app", "Uninstall App"), command=self.action_uninstall_selected_app)


        action_buttons_frame = tk.Frame(container, bg=self.theme.get("GROUP_BG"))
        action_buttons_frame.pack(fill=tk.X, pady=(10,0), padx=5)

        ModernButton(action_buttons_frame, text=self.labels.get("btn_copy_package_name", "Copy Package"),
                     command=self.action_copy_package_name, theme=self.theme, width=20).pack(side=tk.LEFT, padx=5, pady=5) 
        ModernButton(action_buttons_frame, text=self.labels.get("btn_uninstall_selected_app", "Uninstall"),
                     command=self.action_uninstall_selected_app, theme=self.theme, width=20).pack(side=tk.LEFT, padx=5, pady=5) 
        
        self.all_packages_cache = [] 
        self.action_refresh_app_list() 
        log_to_file_debug_globally("AppManagerTab __init__ finished.")

    def _show_app_context_menu(self, event):
        iid = self.app_tree.identify_row(event.y)
        if iid:
            self.app_tree.selection_set(iid) 
            self.app_context_menu.tk_popup(event.x_root, event.y_root)


    def action_refresh_app_list(self):
        filter_mode = self.filter_var.get()
        cmd = ["adb", "shell", "pm", "list", "packages", "-f"] 
        if filter_mode == "third_party":
            cmd.append("-3")
        elif filter_mode == "system":
            cmd.append("-s")

        op_name = f"List Apps ({filter_mode})"
        if self.master_app.log_panel:
            self.master_app.log_panel.log(f"Refreshing app list ({filter_mode})...", "info")
            self.master_app.log_panel.progress_bar.start()

        def _list_apps_callback(result):
            if self.master_app.log_panel and self.master_app.log_panel.progress_bar.running:
                self.master_app.log_panel.progress_bar.stop()

            self.all_packages_cache.clear()
            if result.get("error") or result.get("return_code") != 0:
                if self.master_app.log_panel:
                    self.master_app.log_panel.log(f"{op_name} Failed: {result.get('stderr', 'Unknown error')}", "error")
                return
            
            stdout = result.get("stdout", "")
            raw_lines = stdout.splitlines()
            for line in raw_lines:
                line = line.strip()
                if line.startswith("package:"):
                    parts = line.split("=", 1)
                    path = parts[0][len("package:"):]
                    package_name = parts[1] if len(parts) > 1 else "N/A"
                    self.all_packages_cache.append({"package": package_name, "path": path})
            
            self.filter_app_list_display() 
            if self.master_app.log_panel:
                self.master_app.log_panel.log(f"App list refreshed. Found {len(self.all_packages_cache)} apps.", "success" if self.all_packages_cache else "warning")


        self.master_app.execute_command_async(cmd, operation_name=op_name, callback_on_finish=_list_apps_callback)

    def filter_app_list_display(self):
        for i in self.app_tree.get_children():
            self.app_tree.delete(i)
        
        search_term = self.search_var.get().lower()
        
        for app_info in self.all_packages_cache:
            if search_term in app_info["package"].lower() or search_term in app_info["path"].lower():
                self.app_tree.insert("", tk.END, values=(app_info["package"], app_info["path"]))

    def action_copy_package_name(self):
        selected_item = self.app_tree.selection()
        if not selected_item:
            messagebox.showwarning(self.labels.get("no_app_selected_title", "No Selection"),
                                   self.labels.get("no_app_selected_message", "Please select an app."), parent=self.master_app.master)
            return
        item_values = self.app_tree.item(selected_item[0], "values")
        package_name = item_values[0]
        self.master_app.clipboard_clear()
        self.master_app.clipboard_append(package_name)
        if self.master_app.log_panel:
            self.master_app.log_panel.log(f"Copied to clipboard: {package_name}", "info")

    def action_uninstall_selected_app(self):
        selected_item = self.app_tree.selection()
        if not selected_item:
            messagebox.showwarning(self.labels.get("no_app_selected_title", "No Selection"),
                                   self.labels.get("no_app_selected_message", "Please select an app."), parent=self.master_app.master)
            return
        item_values = self.app_tree.item(selected_item[0], "values")
        package_name = item_values[0]

        confirm_msg = self.labels.get("uninstall_app_confirm_message", "Uninstall {package_name}?").format(package_name=package_name)
        if messagebox.askyesno(self.labels.get("uninstall_app_confirm_title", "Confirm Uninstall"), confirm_msg, parent=self.master_app.master):
            op_name = f"Uninstall App: {package_name}"
            cmd = ["adb", "shell", "pm", "uninstall", package_name]

            def _uninstall_callback(result):
                if result.get("return_code") == 0 and "Success" in result.get("stdout",""):
                    if self.master_app.log_panel:
                        self.master_app.log_panel.log(f"Successfully uninstalled {package_name}.", "success")
                    self.action_refresh_app_list() 
                else:
                    if self.master_app.log_panel:
                        err_msg = result.get("stderr","") or result.get("stdout","") or "Unknown error"
                        self.master_app.log_panel.log(f"Failed to uninstall {package_name}: {err_msg.strip()}", "error")
            
            self.master_app.execute_command_async(cmd, operation_name=op_name, callback_on_finish=_uninstall_callback)


if __name__ == "__main__":
    if not PIL_AVAILABLE:
        log_to_file_debug_globally("Pillow not installed. UI may not display images correctly.", "CRITICAL")

    try:
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as f_log_check:
            f_log_check.write(f"[{datetime.now()}] [INFO] Main execution block started.\n")
    except Exception as e_log_main_check:
        print(f"[CRITICAL_ERROR] Cannot write to main debug log '{_DEBUG_LOG_PATH}': {e_log_main_check}", file=sys.stderr)
        _DEBUG_LOG_PATH = "application_debug_log_local.txt" 
        try:
            with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as f_log_fallback:
                f_log_fallback.write(f"[{datetime.now()}] [INFO] Using fallback debug log: '{_DEBUG_LOG_PATH}'.\n")
        except Exception as e_log_fallback_create:
            print(f"[CRITICAL_ERROR] Cannot write to fallback debug log '{_DEBUG_LOG_PATH}': {e_log_fallback_create}", file=sys.stderr)

    try:
        try:
            subprocess.check_output(["adb", "version"], stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            log_to_file_debug_globally("ADB found and working.")
        except Exception:
            log_to_file_debug_globally("ADB not found or not working. Some features might be unavailable.", "WARNING")

        try:
            subprocess.check_output(["fastboot", "--version"], stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            log_to_file_debug_globally("Fastboot found and working.")
        except Exception:
            log_to_file_debug_globally("Fastboot not found or not working. Some features might be unavailable.", "WARNING")

        controller = AppController()
        controller.start()

    except Exception as e:
        log_to_file_debug_globally(f"Fatal error in main execution: {e}", "CRITICAL")
        traceback.print_exc(file=open(_DEBUG_LOG_PATH, "a")) 
        try:
            root_err = tk.Tk()
            root_err.withdraw() 
            messagebox.showerror("Fatal Error", f"A critical error occurred: {e}\n\nPlease check '{_DEBUG_LOG_PATH}' for details.", parent=None)
            root_err.destroy()
        except Exception as e_tk_fatal:
            print(f"A critical error occurred: {e}. Check '{_DEBUG_LOG_PATH}'. Tkinter error dialog also failed: {e_tk_fatal}", file=sys.stderr)
