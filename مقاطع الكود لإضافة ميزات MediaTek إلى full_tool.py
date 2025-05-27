# مقاطع الكود لإضافة ميزات MediaTek إلى full_tool.py

**ملاحظة هامة:** بسبب مشكلة تقنية متكررة في حفظ الملف المعدل، يتم تقديم هذه الإضافات كمقاطع كود منفصلة. يرجى دمجها يدوياً في نسختك الأصلية من `full_tool.py` في الأماكن الموضحة.

## 1. إضافة النصوص (Labels)

أضف المفاتيح والقيم التالية داخل القواميس `LABELS['en']` و `LABELS['ar']` الموجودة في بداية السكربت:

```python
# داخل LABELS['en'] أضف:
"tab_mediatek": "MediaTek (BROM/Preloader)",
"group_mediatek_tools": "MediaTek Tools",
"btn_mtk_detect": "Detect Device (BROM)",
"btn_mtk_read_info": "Read Info (BROM)",
"btn_mtk_list_models": "Show Supported Models",
"btn_mtk_extract_keys_brom": "Extract Keys (BROM)",
"btn_mtk_extract_keys_preloader": "Extract Keys (Preloader)",
"btn_mtk_generate_ewc": "Generate EWC File",
"mtk_status_not_connected": "MTK: Not Connected",
"mtk_status_connected": "MTK: Device Detected",
"mtk_unsupported_feature_title": "Feature Not Fully Implemented",
"mtk_unsupported_feature_msg": "This feature ({feature_name}) requires specific technical details or commands for key extraction/EWC generation which are not yet available. This button currently acts as a placeholder.",
"mtk_key_extraction_info": "Key extraction requires device in BROM or Preloader mode. Output will be saved in the tool's directory.",
"mtk_ewc_info": "EWC generation requires extracted dump and keys. Ensure they are available.",
"mtk_model_list_title": "Supported Processors & Models (Examples)",
"mtk_model_list_content": """
Supported Processors:
- V5: MT6735, MT6737, MT6750, MT6755, MT6771, ...
- V6: MT6761, MT6765, MT6768, MT6769, MT6785, MT6789, MT6833, MT6873, MT6893, ...

Supported Models (Examples - Requires specific DA/Preloader sometimes):
- Huawei: CRO-U00, JAT-L29, LUA-L22, MYA-L22
- Infinix/Tecno: X5514, X5515, X606, X609, X624
- Lenovo: TB-7104I, TB-7304F, TB-7304I, TB3-730M
- Oppo/Realme: Devices based on MT6789
- Samsung: SM-A037F, SM-A037M, SM-A042F, SM-A045F, SM-A225B, SM-T225, SM-X110
- Xiaomi: Mi 12t, Poco C61, Poco C65, Poco C75, Poco X6 Pro 5G, Redmi 13C, Redmi 14C, Redmi A3, Redmi A3 Pro, Redmi Note 13R Pro, Redmi Note 13 5G, Redmi Pad SE 4G, Redmi Pad SE 8.7
""",

# داخل LABELS['ar'] أضف:
"tab_mediatek": "ميدياتك (BROM/Preloader)",
"group_mediatek_tools": "أدوات ميدياتك",
"btn_mtk_detect": "كشف الجهاز (BROM)",
"btn_mtk_read_info": "قراءة المعلومات (BROM)",
"btn_mtk_list_models": "عرض الموديلات المدعومة",
"btn_mtk_extract_keys_brom": "استخراج المفاتيح (BROM)",
"btn_mtk_extract_keys_preloader": "استخراج المفاتيح (Preloader)",
"btn_mtk_generate_ewc": "توليد ملف EWC",
"mtk_status_not_connected": "MTK: غير متصل",
"mtk_status_connected": "MTK: تم كشف الجهاز",
"mtk_unsupported_feature_title": "الميزة غير مكتملة التنفيذ",
"mtk_unsupported_feature_msg": "هذه الميزة ({feature_name}) تتطلب تفاصيل تقنية أو أوامر محددة لاستخراج المفاتيح/توليد EWC وهي غير متوفرة حالياً. هذا الزر يعمل كعنصر نائب.",
"mtk_key_extraction_info": "استخراج المفاتيح يتطلب أن يكون الجهاز في وضع BROM أو Preloader. سيتم حفظ المخرجات في مجلد الأداة.",
"mtk_ewc_info": "توليد EWC يتطلب وجود ملف Dump والمفاتيح المستخرجة. تأكد من توفرها.",
"mtk_model_list_title": "المعالجات والموديلات المدعومة (أمثلة)",
"mtk_model_list_content": """
المعالجات المدعومة:
- V5: MT6735, MT6737, MT6750, MT6755, MT6771، ...
- V6: MT6761, MT6765, MT6768, MT6769, MT6785, MT6789, MT6833, MT6873, MT6893، ...

الموديلات المدعومة (أمثلة - قد تتطلب DA/Preloader معين):
- Huawei: CRO-U00, JAT-L29, LUA-L22, MYA-L22
- Infinix/Tecno: X5514, X5515, X606, X609, X624
- Lenovo: TB-7104I, TB-7304F, TB-7304I, TB3-730M
- Oppo/Realme: الأجهزة المعتمدة على MT6789
- Samsung: SM-A037F, SM-A037M, SM-A042F, SM-A045F, SM-A225B, SM-T225, SM-X110
- Xiaomi: Mi 12t, Poco C61, Poco C65, Poco C75, Poco X6 Pro 5G, Redmi 13C, Redmi 14C, Redmi A3, Redmi A3 Pro, Redmi Note 13R Pro, Redmi Note 13 5G, Redmi Pad SE 4G, Redmi Pad SE 8.7
""",
```

## 2. إضافة استيراد subprocess

تأكد من وجود السطر التالي مع بقية جمل `import` في بداية الملف:

```python
import subprocess
```

## 3. تعديل دالة `log_operation` (اختياري ولكن موصى به)

لتحسين عرض حالة النجاح/الفشل في السجل بالألوان، يمكنك تعديل دالة `log_operation` الحالية (أو التأكد من أنها تدعم العلامات tags بالألوان). تأكد من تعريف الألوان للعلامات 'success' و 'error' عند إعداد `self.log_text`:

```python
# داخل دالة __init__ أو setup_ui حيث يتم إنشاء self.log_text
self.log_text.tag_configure("info", foreground="black")
self.log_text.tag_configure("error", foreground="red")
self.log_text.tag_configure("success", foreground="green") # تأكد من وجود هذه
self.log_text.tag_configure("warning", foreground="orange") # أو أي لون آخر

# ... (بقية الكود)

# تعديل دالة log_operation لتقبل علامة الحالة
def log_operation(self, message, level="info"):
    # ... (الكود الحالي للدالة)
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.config(state=tk.NORMAL)
        # استخدم level كعلامة tag
        self.log_text.insert(tk.END, log_entry, level) 
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        # ... (الكود الحالي لحفظ السجل في ملف)
    except Exception as e:
        # ... (معالجة الخطأ)
```

## 4. إضافة دوال عمليات MediaTek

أضف الدوال التالية إلى الكلاس الرئيسي للتطبيق (مثلاً `UltimatUnlockTool`):

```python
    # ========== MediaTek Functions ==========

    def run_mtk_command(self, command_args, operation_name):
        """Runs an mtkclient command in a separate thread and logs the output."""
        # المسار إلى سكربت mtkclient الرئيسي. قد تحتاج لتعديله إذا وضعته في مكان آخر.
        mtk_script_path = "/home/ubuntu/mtkclient/mtk"
        
        # الأمر الكامل لاستدعاء mtkclient
        full_command = [sys.executable, mtk_script_path] + command_args
        
        self.log_operation(f"{operation_name} - Operation Started: {' '.join(full_command)}", level="info")
        start_time = datetime.now()
        
        # استخدم نفس آلية الـ thread والـ queue الموجودة في السكربت
        self.start_operation_thread(self._execute_mtk_command_thread, (full_command, operation_name, start_time))

    def _execute_mtk_command_thread(self, full_command, operation_name, start_time):
        """Thread function to execute mtkclient command."""
        try:
            # ملاحظة: قد تحتاج mtkclient إلى صلاحيات خاصة للوصول لـ USB
            # قد تحتاج لتشغيل الأداة بصلاحيات sudo أو إعداد قواعد udev
            process = subprocess.run(full_command, capture_output=True, text=True, check=False, encoding='utf-8', errors='ignore')
            end_time = datetime.now()
            duration = end_time - start_time
            
            output = process.stdout + "\n" + process.stderr
            
            if process.returncode == 0:
                result_message = f"{operation_name} - Operation Successful (Duration: {duration})\nOutput:\n{output}"
                self.queue.put(("log", result_message, "success"))
            else:
                result_message = f"{operation_name} - Operation Failed (Return Code: {process.returncode}, Duration: {duration})\nOutput:\n{output}"
                self.queue.put(("log", result_message, "error"))

        except FileNotFoundError:
            end_time = datetime.now()
            duration = end_time - start_time
            error_message = f"{operation_name} - Operation Failed: mtk script not found at {full_command[1]}. (Duration: {duration})"
            self.queue.put(("log", error_message, "error"))
        except Exception as e:
            end_time = datetime.now()
            duration = end_time - start_time
            error_message = f"{operation_name} - An unexpected error occurred: {e}\n{traceback.format_exc()} (Duration: {duration})"
            self.queue.put(("log", error_message, "error"))

    def mtk_detect_device(self):
        self.run_mtk_command(["brom"], "MTK Detect Device (BROM)") # الأمر قد يختلف قليلاً

    def mtk_read_info(self):
        # الأمر 'r', 'info' قد لا يكون دقيقاً، راجع وثائق mtkclient للأمر الصحيح لقراءة المعلومات
        self.run_mtk_command(["r", "info"], "MTK Read Info (BROM)") 

    def mtk_list_models(self):
        title = self.get_label("mtk_model_list_title")
        content = self.get_label("mtk_model_list_content")
        messagebox.showinfo(title, content)
        self.log_operation("Displayed supported models list.", level="info")

    def mtk_extract_keys_brom(self):
        # !!! تحذير: هذه الميزة تتطلب أوامر mtkclient محددة وتفاصيل تقنية غير متوفرة !!!
        # !!! هذا مجرد عنصر نائب Placeholder !!!
        feature_name = "Extract Keys (BROM)"
        title = self.get_label("mtk_unsupported_feature_title")
        message = self.get_label("mtk_unsupported_feature_msg").format(feature_name=feature_name)
        messagebox.showwarning(title, message)
        self.log_operation(f"{feature_name}: Feature is a placeholder. Requires specific commands.", level="warning")
        # self.run_mtk_command(['--extract-keys-brom-command'], "MTK Extract Keys (BROM)") # مثال على أمر وهمي

    def mtk_extract_keys_preloader(self):
        # !!! تحذير: هذه الميزة تتطلب أوامر mtkclient محددة وتفاصيل تقنية غير متوفرة !!!
        # !!! هذا مجرد عنصر نائب Placeholder !!!
        feature_name = "Extract Keys (Preloader)"
        title = self.get_label("mtk_unsupported_feature_title")
        message = self.get_label("mtk_unsupported_feature_msg").format(feature_name=feature_name)
        messagebox.showwarning(title, message)
        self.log_operation(f"{feature_name}: Feature is a placeholder. Requires specific commands.", level="warning")
        # self.run_mtk_command(['--extract-keys-preloader-command'], "MTK Extract Keys (Preloader)") # مثال على أمر وهمي

    def mtk_generate_ewc(self):
        # !!! تحذير: هذه الميزة تتطلب معرفة بتنسيق ملف EWC الخاص بـ Oxygen Forensic !!!
        # !!! هذا مجرد عنصر نائب Placeholder !!!
        feature_name = "Generate EWC File"
        title = self.get_label("mtk_unsupported_feature_title")
        message = self.get_label("mtk_unsupported_feature_msg").format(feature_name=feature_name)
        messagebox.showwarning(title, message)
        self.log_operation(f"{feature_name}: Feature is a placeholder. Requires EWC format details.", level="warning")
        # هنا يجب إضافة كود لتوليد الملف بناءً على Dump والمفاتيح
```

## 5. إنشاء تبويب MediaTek

أضف الدالة التالية إلى الكلاس الرئيسي للتطبيق (مثلاً `UltimatUnlockTool`):

```python
    def create_mediatek_tab(self, notebook):
        mediatek_frame = ttk.Frame(notebook, padding="10")
        notebook.add(mediatek_frame, text=self.get_label("tab_mediatek"))

        # --- MediaTek Tools Group ---
        mtk_tools_group = ttk.LabelFrame(mediatek_frame, text=self.get_label("group_mediatek_tools"), padding="10")
        mtk_tools_group.pack(pady=5, padx=5, fill="x")

        # الأزرار
        btn_detect = ttk.Button(mtk_tools_group, text=self.get_label("btn_mtk_detect"), command=self.mtk_detect_device, width=25)
        btn_detect.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_read_info = ttk.Button(mtk_tools_group, text=self.get_label("btn_mtk_read_info"), command=self.mtk_read_info, width=25)
        btn_read_info.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        btn_list_models = ttk.Button(mtk_tools_group, text=self.get_label("btn_mtk_list_models"), command=self.mtk_list_models, width=25)
        btn_list_models.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # --- Key Extraction & EWC Group ---
        mtk_advanced_group = ttk.LabelFrame(mediatek_frame, text="Key Extraction & Forensic", padding="10")
        mtk_advanced_group.pack(pady=5, padx=5, fill="x")

        btn_extract_brom = ttk.Button(mtk_advanced_group, text=self.get_label("btn_mtk_extract_keys_brom"), command=self.mtk_extract_keys_brom, width=25)
        btn_extract_brom.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(mtk_advanced_group, text=self.get_label("mtk_key_extraction_info"), wraplength=300, justify=tk.LEFT).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        btn_extract_preloader = ttk.Button(mtk_advanced_group, text=self.get_label("btn_mtk_extract_keys_preloader"), command=self.mtk_extract_keys_preloader, width=25)
        btn_extract_preloader.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_generate_ewc = ttk.Button(mtk_advanced_group, text=self.get_label("btn_mtk_generate_ewc"), command=self.mtk_generate_ewc, width=25)
        btn_generate_ewc.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(mtk_advanced_group, text=self.get_label("mtk_ewc_info"), wraplength=300, justify=tk.LEFT).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # --- Status Label (اختياري) ---
        # يمكنك إضافة تسمية لعرض حالة اتصال MTK إذا أردت
        # self.mtk_status_label = ttk.Label(mediatek_frame, text=self.get_label("mtk_status_not_connected"))
        # self.mtk_status_label.pack(pady=5)
```

## 6. إضافة التبويب إلى الواجهة الرئيسية

في دالة `setup_ui` أو المكان الذي تضيف فيه التبويبات الأخرى (`self.notebook.add(...)`)، أضف السطر التالي لاستدعاء دالة إنشاء تبويب MediaTek:

```python
        # ... (إضافة التبويبات الأخرى مثل Samsung, Honor, Xiaomi)
        self.create_mediatek_tab(self.notebook)
        self.create_file_advanced_tab(self.notebook)
        # ... (بقية إعدادات الواجهة)
```

**ملاحظات هامة بعد الدمج:**

1.  **مسار `mtkclient`:** تأكد من أن المسار `mtk_script_path` في دالة `run_mtk_command` صحيح ويشير إلى مكان وجود سكربت `mtk` داخل المجلد الذي تم استنساخه (`/home/ubuntu/mtkclient/mtk` في هذا المثال).
2.  **أوامر `mtkclient`:** الأوامر المستخدمة في الدوال (`mtk_detect_device`, `mtk_read_info`) هي مجرد تخمين وقد تحتاج إلى تعديل بناءً على الوثائق الرسمية أو تجارب استخدام `mtkclient`. ابحث عن الأوامر الصحيحة لكشف الجهاز وقراءة المعلومات في وضع BROM.
3.  **استخراج المفاتيح و EWC:** كما هو مذكور في التعليقات، هذه الوظائف هي مجرد هياكل مكانية (placeholders) وتحتاج إلى معرفة تقنية دقيقة بأوامر `mtkclient` المطلوبة وتنسيق ملف EWC المتوافق مع Oxygen Forensic. ستحتاج للبحث عن هذه التفاصيل أو الحصول عليها لتنفيذ هذه الميزات بشكل كامل.
4.  **الصلاحيات:** قد يتطلب تشغيل `mtkclient` صلاحيات خاصة للوصول إلى جهاز USB (مثل `sudo` أو إعداد قواعد `udev` على نظام Linux). قد تحتاج إلى تشغيل الأداة بأكملها بصلاحيات `sudo` أو إيجاد طريقة لمنح الصلاحيات اللازمة لـ `mtkclient`.
5.  **الاختبار:** الاختبار الفعلي ضروري باستخدام الأجهزة المذكورة للتأكد من عمل الأوامر واستجابة الأجهزة بشكل صحيح.

آمل أن تساعدك هذه المقاطع في دمج الميزات المطلوبة. أعتذر مرة أخرى عن المشكلة التقنية التي منعتني من تسليم السكربت كاملاً.
