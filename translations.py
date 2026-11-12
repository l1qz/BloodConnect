"""Centralized English, Arabic, and Kurdish Sorani interface translations."""

import re
from flask import session


# English is the canonical key set. Missing translations fall back to English
# rather than silently returning a mixture of translated and untranslated text.
EN = {
    "Arabic": "Arabic", "Kurdish (Sorani)": "Kurdish (Sorani)", "English": "English",
    "Donor Matcher - Kirkuk": "Donor Matcher - Kirkuk",
    "Notifications": "Notifications", "New notifications": "New notifications",
    "No new notifications": "No new notifications", "Logout": "Log out",
    "Login": "Log in", "Register as donor": "Register as donor",
    "Register hospital": "Register hospital", "Language": "Language",
    "Donor card": "Donor card", "Rewards": "Rewards", "Rewards admin": "Rewards admin",
    "Help": "Help", "Why donate?": "Why donate?",
    "A blood unit at the right time saves a patient": "A blood unit at the right time saves a patient",
    "When a hospital in Kirkuk needs a rare blood type, we reach qualified nearby donors within minutes.": "When a hospital in Kirkuk needs a rare blood type, we reach qualified nearby donors within minutes.",
    "Phone number": "Phone number", "Password": "Password",
    "Password (at least 6 characters)": "Password (at least 6 characters)",
    "You do not have an account?": "You do not have an account?", "or": "or",
    "Sign in": "Sign in", "Register": "Register", "Register as a donor": "Register as a donor",
    "Hospital registration": "Hospital registration", "Register a hospital": "Register a hospital",
    "Full name": "Full name", "Blood type": "Blood type", "District": "District",
    "Select district": "Select district", "Select blood type": "Select blood type",
    "Gender": "Gender", "Male": "Male", "Female": "Female", "Birth date": "Birth date",
    "Weight (kg)": "Weight (kg)", "Create account": "Create account",
    "I have an account": "I have an account", "Hospital name": "Hospital name",
    "Address": "Address", "Send registration request": "Send registration request",
    "Donor dashboard": "Donor dashboard", "Last donation": "Last donation",
    "Not donated yet": "Not donated yet", "Available to donate now": "Available to donate now",
    "Currently unavailable": "Currently unavailable",
    "Cases matching your blood type": "Cases matching your blood type",
    "I can donate": "I can donate", "I cannot": "I cannot",
    "No cases currently. We will notify you when a hospital needs your blood type.": "No cases currently. We will notify you when a hospital needs your blood type.",
    "Your donation history": "Your donation history",
    "You have no recorded donations yet.": "You have no recorded donations yet.",
    "Hospital dashboard": "Hospital dashboard", "Blood requests you published": "Blood requests you published",
    "New blood request": "New blood request",
    "Your account is awaiting administrator approval. You can publish blood requests after approval.": "Your account is awaiting administrator approval. You can publish blood requests after approval.",
    "No request published yet. Press “New blood request” to reach suitable donors.": "No request published yet. Press “New blood request” to reach suitable donors.",
    "Patient blood type": "Patient blood type", "Number of units": "Number of units",
    "Urgency": "Urgency", "Critical": "Critical", "Urgent": "Urgent", "Normal": "Normal",
    "Notes for donors (optional)": "Notes for donors (optional)",
    "Post request and notify donors": "Post request and notify donors", "Back": "Back",
    "Overview": "System overview", "Registered donors": "Registered donors",
    "Approved hospitals": "Approved hospitals", "Open requests": "Open requests",
    "Completed donations": "Completed donations", "Pending hospital approvals": "Hospitals pending approval",
    "Approve": "Approve", "No pending registration requests.": "No pending registration requests.",
    "Donors by blood type": "Donors by blood type", "Request": "Request", "Received": "Received",
    "Accepted donors": "Accepted donors", "Matching donors": "Matching donors", "Donor": "Donor",
    "Status": "Status", "Confirm donation": "Confirm donation",
    "No eligible donors for this blood type currently.": "No eligible donors for this blood type currently.",
    "The donor's phone number appears only after their approval.": "The donor's phone number appears only after their approval.",
    "Return home": "Return home", "Cancel request": "Cancel request",
    "Are you sure you want to cancel this request?": "Are you sure you want to cancel this request?",
    "Received units": "Received units", "Donor name": "Donor name", "Area": "Area", "Phone": "Phone",
    "No eligible donors are currently available for this blood type.": "No eligible donors are currently available for this blood type.",
    "The donor's phone number is shown only after approval.": "The donor's phone number is shown only after approval.",
    "Example: surgery tomorrow morning in the emergency department": "Example: surgery tomorrow morning in the emergency department",
    "Published on": "Published on", "Please fill in all fields": "Please fill in all fields",
    "Password must be at least 6 characters": "Password must be at least 6 characters",
    "Account created successfully. Please sign in.": "Account created successfully. Please sign in.",
    "Phone number is already registered or the data is invalid": "Phone number is already registered or the data is invalid",
    "Registration submitted. Awaiting administrator approval.": "Registration submitted. Awaiting administrator approval.",
    "Phone number is already registered": "Phone number is already registered",
    "Incorrect phone number or password": "Incorrect phone number or password",
    "Your account is awaiting administrator approval": "Your account is awaiting administrator approval",
    "Invalid number of units": "Invalid number of units",
    "Request published and {count} donors notified": "Request published and {count} donors notified",
    "Request not found": "Request not found", "Donation confirmed": "Donation confirmed",
    "Donation could not be confirmed": "Donation could not be confirmed", "Request cancelled": "Request cancelled",
    "Hospital approved": "Hospital approved", "Error": "Error",
    "You are not allowed to open this page": "You are not allowed to open this page",
    "Page not found": "Page not found",
    "Digital donor card": "Digital donor card", "Download QR": "Download QR",
    "Verified donor": "Verified donor", "Donor number": "Donor number",
    "Not recorded": "Not recorded", "Recorded donations": "Recorded donations",
    "The QR code contains a protected verification link. Staff access is required to view records.": "The QR code contains a protected verification link. Staff access is required to view records.",
    "Donation helper": "Donation helper", "Blood donation helper": "Blood donation helper",
    "Friendly general information, not a medical diagnosis.": "Friendly general information, not a medical diagnosis.",
    "Ask about eligibility, preparation, blood types, recovery, or fear of needles.": "Ask about eligibility, preparation, blood types, recovery, or fear of needles.",
    "Question": "Question", "How should I prepare?": "How should I prepare?", "Ask": "Ask",
    "Donor rewards": "Donor rewards", "Points are awarded only after staff verify a donation.": "Points are awarded only after staff verify a donation.",
    "points": "points", "Redeem": "Redeem", "No rewards are currently available.": "No rewards are currently available.",
    "Redemption history": "Redemption history", "No redemptions yet.": "No redemptions yet.",
    "Manage rewards": "Manage rewards", "Reward name": "Reward name", "Description": "Description",
    "Points": "Points", "Add": "Add", "Active": "Active", "Inactive": "Inactive",
    "Disable": "Disable", "Enable": "Enable", "Authorized donor verification": "Authorized donor verification",
    "QR token": "QR token", "Scan QR or paste verification token": "Scan QR or paste verification token",
    "Verify": "Verify", "This QR code is invalid or expired.": "This QR code is invalid or expired.",
    "Verified donation records": "Verified donation records", "No records found.": "No records found.",
    "Donor #": "Donor #", "Last donation:": "Last donation:", "Recorded donations:": "Recorded donations:",
    "This information is general and does not replace professional medical advice.": "This information is general and does not replace professional medical advice.",
    "Reward requested. Staff will follow up with you.": "Reward requested. Staff will follow up with you.",
    "Invalid reward.": "Invalid reward.", "You do not have enough points for this reward.": "You do not have enough points for this reward.",
    "Reward name and a positive point cost are required.": "Reward name and a positive point cost are required.",
    "Every donation matters": "Every donation matters",
    "Your donation could be someone's second chance at life.": "Your donation could be someone's second chance at life.",
    "Feeling nervous is normal. You do not have to pretend otherwise. Tell the donation team, ask questions, and take things one step at a time.": "Feeling nervous is normal. You do not have to pretend otherwise. Tell the donation team, ask questions, and take things one step at a time.",
    "Why it matters": "Why it matters",
    "Donated blood helps hospitals care for people after serious injuries, during surgery and childbirth complications, and throughout some cancer and blood-disorder treatments.": "Donated blood helps hospitals care for people after serious injuries, during surgery and childbirth complications, and throughout some cancer and blood-disorder treatments.",
    "A calm, guided process": "A calm, guided process",
    "First, staff ask about your health and check whether donating is suitable. If you qualify, they guide you through the donation while you are seated, then ask you to rest.": "First, staff ask about your health and check whether donating is suitable. If you qualify, they guide you through the donation while you are seated, then ask you to rest.",
    "Small steps that can make it easier": "Small steps that can make it easier",
    "Eat a normal meal, drink water, sleep well, and wear comfortable clothing. Tell staff if needles make you nervous. You can look away, breathe slowly, and ask to pause.": "Eat a normal meal, drink water, sleep well, and wear comfortable clothing. Tell staff if needles make you nervous. You can look away, breathe slowly, and ask to pause.",
    "You are in control": "You are in control",
    "You can ask questions before you begin. Screening is private, trained staff supervise the process, and you can tell them if you feel uncomfortable. Never donate when you feel unwell.": "You can ask questions before you begin. Screening is private, trained staff supervise the process, and you can tell them if you feel uncomfortable. Never donate when you feel unwell.",
    "One donation is a meaningful act of care.": "One donation is a meaningful act of care.",
    "Thank you for considering it. Donating is voluntary, and your health comes first.": "Thank you for considering it. Donating is voluntary, and your health comes first.",
    "Talk to trained staff": "Talk to trained staff",
    "Eligibility depends on your health and local blood-service rules. The donation team makes the final decision.": "Eligibility depends on your health and local blood-service rules. The donation team makes the final decision.",
    "I feel nervous about needles.": "I feel nervous about needles.",
    "A little fear does not mean you cannot donate. Tell the staff before the process starts. They can explain each step, help you lie back if appropriate, and give you time to feel ready. You can pause or stop at any point.": "A little fear does not mean you cannot donate. Tell the staff before the process starts. They can explain each step, help you lie back if appropriate, and give you time to feel ready. You can pause or stop at any point.",
    "A hospital needs blood type {blood_type} at {hospital}. Can you help?": "A hospital needs blood type {blood_type} at {hospital}. Can you help?",
    "A donor accepted the request for blood type {blood_type}.": "A donor accepted the request for blood type {blood_type}.",
    "Thank you for donating blood. Your kindness matters.": "Thank you for donating blood. Your kindness matters.",
    "Your response was recorded.": "Your response was recorded.",
    "Thank you! The hospital will contact you.": "Thank you! The hospital will contact you.",
    "An error occurred": "An error occurred", "Invalid action": "Invalid action",
    "Not found": "Not found", "You cannot respond to this request": "You cannot respond to this request",
}

AR = {
    "Arabic": "العربية", "Kurdish (Sorani)": "الكردية (السورانية)", "English": "الإنجليزية",
    "Donor Matcher - Kirkuk": "منصة مطابقة المتبرعين بالدم - كركوك",
    "Notifications": "الإشعارات", "New notifications": "إشعارات جديدة", "No new notifications": "لا توجد إشعارات جديدة",
    "Logout": "تسجيل الخروج", "Login": "تسجيل الدخول", "Register as donor": "التسجيل كمتبرع",
    "Register hospital": "تسجيل مستشفى", "Language": "اللغة", "Donor card": "بطاقة المتبرع",
    "Rewards": "المكافآت", "Rewards admin": "إدارة المكافآت", "Help": "المساعدة", "Why donate?": "لماذا نتبرع بالدم؟",
    "A blood unit at the right time saves a patient": "وحدة دم في الوقت المناسب قد تنقذ حياة مريض",
    "When a hospital in Kirkuk needs a rare blood type, we reach qualified nearby donors within minutes.": "عندما يحتاج مستشفى في كركوك إلى فصيلة دم نادرة، نصل إلى المتبرعين المؤهلين القريبين خلال دقائق.",
    "Phone number": "رقم الهاتف", "Password": "كلمة المرور", "Password (at least 6 characters)": "كلمة المرور (6 أحرف على الأقل)",
    "You do not have an account?": "ليس لديك حساب؟", "or": "أو", "Sign in": "دخول", "Register": "تسجيل",
    "Register as a donor": "التسجيل كمتبرع", "Hospital registration": "تسجيل مستشفى", "Register a hospital": "تسجيل مستشفى",
    "Full name": "الاسم الكامل", "Blood type": "فصيلة الدم", "District": "المنطقة", "Select district": "اختر المنطقة",
    "Select blood type": "اختر فصيلة الدم", "Gender": "الجنس", "Male": "ذكر", "Female": "أنثى",
    "Birth date": "تاريخ الميلاد", "Weight (kg)": "الوزن (كغ)", "Create account": "إنشاء الحساب",
    "I have an account": "لدي حساب", "Hospital name": "اسم المستشفى", "Address": "العنوان",
    "Send registration request": "إرسال طلب التسجيل", "Donor dashboard": "لوحة المتبرع", "Last donation": "آخر تبرع",
    "Not donated yet": "لم تتبرع بعد", "Available to donate now": "متاح للتبرع الآن", "Currently unavailable": "غير متاح حاليًا",
    "Cases matching your blood type": "الحالات المطابقة لفصيلة دمك", "I can donate": "أستطيع التبرع", "I cannot": "لا أستطيع",
    "No cases currently. We will notify you when a hospital needs your blood type.": "لا توجد حالات حاليًا. سنبلغك عندما يحتاج مستشفى إلى فصيلة دمك.",
    "Your donation history": "سجل تبرعاتك", "You have no recorded donations yet.": "لا توجد تبرعات مسجلة لك بعد.",
    "Hospital dashboard": "لوحة المستشفى", "Blood requests you published": "طلبات الدم التي نشرتها", "New blood request": "طلب دم جديد",
    "Your account is awaiting administrator approval. You can publish blood requests after approval.": "حسابك بانتظار موافقة المدير. يمكنك نشر طلبات الدم بعد الموافقة.",
    "No request published yet. Press “New blood request” to reach suitable donors.": "لم تنشر أي طلب بعد. اضغط «طلب دم جديد» للوصول إلى المتبرعين المناسبين.",
    "Patient blood type": "فصيلة دم المريض", "Number of units": "عدد الوحدات", "Urgency": "درجة الاستعجال",
    "Critical": "حرجة جدًا", "Urgent": "عاجلة", "Normal": "عادية", "Notes for donors (optional)": "ملاحظات للمتبرعين (اختياري)",
    "Post request and notify donors": "نشر الطلب وإبلاغ المتبرعين", "Back": "رجوع", "Overview": "نظرة عامة على النظام",
    "Registered donors": "المتبرعون المسجلون", "Approved hospitals": "المستشفيات المعتمدة", "Open requests": "الطلبات المفتوحة",
    "Completed donations": "التبرعات المكتملة", "Pending hospital approvals": "المستشفيات بانتظار الموافقة", "Approve": "موافقة",
    "No pending registration requests.": "لا توجد طلبات تسجيل بانتظار الموافقة.", "Donors by blood type": "المتبرعون حسب فصيلة الدم",
    "Request": "طلب", "Received": "تم الاستلام", "Accepted donors": "المتبرعون الموافقون", "Matching donors": "المتبرعون المطابقون",
    "Donor": "المتبرع", "Status": "الحالة", "Confirm donation": "تأكيد التبرع",
    "No eligible donors for this blood type currently.": "لا يوجد متبرعون مؤهلون لهذه الفصيلة حاليًا.",
    "The donor's phone number appears only after their approval.": "يظهر رقم هاتف المتبرع فقط بعد موافقته.",
    "Return home": "العودة إلى الرئيسية", "Cancel request": "إلغاء الطلب",
    "Are you sure you want to cancel this request?": "هل تريد إلغاء هذا الطلب؟", "Received units": "الوحدات المستلمة",
    "Donor name": "اسم المتبرع", "Area": "المنطقة", "Phone": "الهاتف",
    "No eligible donors are currently available for this blood type.": "لا يوجد متبرعون مؤهلون متاحون لهذه الفصيلة حاليًا.",
    "The donor's phone number is shown only after approval.": "يظهر رقم هاتف المتبرع فقط بعد الموافقة.",
    "Example: surgery tomorrow morning in the emergency department": "مثال: عملية جراحية صباح الغد في قسم الطوارئ",
    "Published on": "نُشر في", "Please fill in all fields": "يرجى تعبئة جميع الحقول",
    "Password must be at least 6 characters": "يجب ألا تقل كلمة المرور عن 6 أحرف",
    "Account created successfully. Please sign in.": "تم إنشاء الحساب بنجاح. يرجى تسجيل الدخول.",
    "Phone number is already registered or the data is invalid": "رقم الهاتف مسجل مسبقًا أو أن البيانات غير صالحة",
    "Registration submitted. Awaiting administrator approval.": "تم إرسال طلب التسجيل. بانتظار موافقة المدير.",
    "Phone number is already registered": "رقم الهاتف مسجل مسبقًا", "Incorrect phone number or password": "رقم الهاتف أو كلمة المرور غير صحيحة",
    "Your account is awaiting administrator approval": "حسابك بانتظار موافقة المدير", "Invalid number of units": "عدد الوحدات غير صالح",
    "Request published and {count} donors notified": "تم نشر الطلب وإشعار {count} متبرعًا",
    "Request not found": "الطلب غير موجود", "Donation confirmed": "تم تأكيد التبرع",
    "Donation could not be confirmed": "تعذّر تأكيد التبرع", "Request cancelled": "تم إلغاء الطلب", "Hospital approved": "تمت الموافقة على المستشفى",
    "Error": "خطأ", "You are not allowed to open this page": "ليس لديك صلاحية لفتح هذه الصفحة", "Page not found": "الصفحة غير موجودة",
    "Digital donor card": "بطاقة المتبرع الرقمية", "Download QR": "تنزيل رمز QR", "Verified donor": "متبرع موثّق",
    "Donor number": "رقم المتبرع", "Not recorded": "غير مسجل", "Recorded donations": "التبرعات المسجلة",
    "The QR code contains a protected verification link. Staff access is required to view records.": "يحتوي رمز QR على رابط تحقق محمي. يلزم دخول الموظفين لعرض السجلات.",
    "Donation helper": "مساعد التبرع", "Blood donation helper": "مساعد التبرع بالدم",
    "Friendly general information, not a medical diagnosis.": "معلومات عامة ومبسطة، وليست تشخيصًا طبيًا.",
    "Ask about eligibility, preparation, blood types, recovery, or fear of needles.": "اسأل عن شروط التبرع أو الاستعداد أو فصائل الدم أو التعافي أو الخوف من الإبر.",
    "Question": "السؤال", "How should I prepare?": "كيف أستعد للتبرع؟", "Ask": "اسأل",
    "Donor rewards": "مكافآت المتبرعين", "Points are awarded only after staff verify a donation.": "تُمنح النقاط بعد أن يؤكد الموظفون إتمام التبرع.",
    "points": "نقطة", "Redeem": "استبدال", "No rewards are currently available.": "لا توجد مكافآت متاحة حاليًا.",
    "Redemption history": "سجل الاستبدال", "No redemptions yet.": "لا توجد عمليات استبدال بعد.",
    "Manage rewards": "إدارة المكافآت", "Reward name": "اسم المكافأة", "Description": "الوصف", "Points": "النقاط", "Add": "إضافة",
    "Active": "مفعّلة", "Inactive": "غير مفعّلة", "Disable": "تعطيل", "Enable": "تفعيل",
    "Authorized donor verification": "التحقق من متبرع مخوّل", "QR token": "رمز QR", "Scan QR or paste verification token": "امسح رمز QR أو الصق رمز التحقق",
    "Verify": "تحقق", "This QR code is invalid or expired.": "رمز QR غير صالح أو انتهت صلاحيته.",
    "Verified donation records": "سجلات التبرع المؤكدة", "No records found.": "لم يتم العثور على سجلات.",
    "Last donation:": "آخر تبرع:", "Recorded donations:": "التبرعات المسجلة:",
    "Reward requested. Staff will follow up with you.": "تم إرسال طلب المكافأة. سيتابع الموظفون الطلب.",
    "Invalid reward.": "المكافأة غير صالحة.", "You do not have enough points for this reward.": "ليس لديك نقاط كافية لهذه المكافأة.",
    "Reward name and a positive point cost are required.": "اسم المكافأة وتكلفة نقاط أكبر من صفر مطلوبان.",
    "Every donation matters": "كل تبرع يصنع فرقًا", "Your donation could be someone's second chance at life.": "قد يكون تبرعك فرصة ثانية لشخص كي يواصل الحياة.",
    "Feeling nervous is normal. You do not have to pretend otherwise. Tell the donation team, ask questions, and take things one step at a time.": "من الطبيعي أن تشعر بالتوتر. لا داعي لإخفاء ذلك. أخبر فريق التبرع، واطرح أسئلتك، وخذ الأمور خطوة بخطوة.",
    "Why it matters": "لماذا يعد التبرع مهمًا؟",
    "Donated blood helps hospitals care for people after serious injuries, during surgery and childbirth complications, and throughout some cancer and blood-disorder treatments.": "يساعد الدم المتبرع به المستشفيات في علاج المصابين بإصابات خطيرة، ودعم العمليات الجراحية ومضاعفات الولادة، وعلاج بعض حالات السرطان واضطرابات الدم.",
    "A calm, guided process": "عملية هادئة بإشراف المختصين",
    "First, staff ask about your health and check whether donating is suitable. If you qualify, they guide you through the donation while you are seated, then ask you to rest.": "أولًا، يسألك الموظفون عن صحتك ويتحققون من ملاءمة التبرع لك. إذا كنت مؤهلًا، سيرشدونك خلال التبرع وأنت جالس، ثم يطلبون منك الراحة.",
    "Small steps that can make it easier": "خطوات بسيطة تجعل التجربة أسهل",
    "Eat a normal meal, drink water, sleep well, and wear comfortable clothing. Tell staff if needles make you nervous. You can look away, breathe slowly, and ask to pause.": "تناول وجبة طبيعية، واشرب الماء، ونم جيدًا، وارتدِ ملابس مريحة. أخبر الموظفين إن كنت تخاف الإبر. يمكنك النظر بعيدًا والتنفس ببطء وطلب التوقف قليلًا.",
    "You are in control": "أنت من يقرر",
    "You can ask questions before you begin. Screening is private, trained staff supervise the process, and you can tell them if you feel uncomfortable. Never donate when you feel unwell.": "يمكنك طرح الأسئلة قبل البدء. يتم الفحص بسرية ويشرف موظفون مدربون على العملية. أخبرهم إن شعرت بعدم الارتياح، ولا تتبرع عندما تكون مريضًا أو متوعكًا.",
    "One donation is a meaningful act of care.": "التبرع عمل إنساني له قيمة كبيرة.",
    "Thank you for considering it. Donating is voluntary, and your health comes first.": "شكرًا لتفكيرك في التبرع. التبرع عمل اختياري، وصحتك تأتي أولًا.",
    "Talk to trained staff": "تحدث مع الطاقم المختص",
    "Eligibility depends on your health and local blood-service rules. The donation team makes the final decision.": "تعتمد الأهلية على حالتك الصحية وتعليمات خدمة الدم المحلية. فريق التبرع هو من يقرر أهليتك النهائية.",
    "I feel nervous about needles.": "أشعر بالخوف من الإبر.",
    "A little fear does not mean you cannot donate. Tell the staff before the process starts. They can explain each step, help you lie back if appropriate, and give you time to feel ready. You can pause or stop at any point.": "الخوف البسيط لا يعني أنك لا تستطيع التبرع. أخبر الموظفين قبل البدء. يمكنهم شرح كل خطوة ومساعدتك على الاستلقاء عند الحاجة ومنحك الوقت حتى تشعر بالاستعداد. يمكنك طلب التوقف أو إنهاء العملية في أي وقت.",
    "A hospital needs blood type {blood_type} at {hospital}. Can you help?": "يحتاج مستشفى {hospital} إلى فصيلة الدم {blood_type}. هل يمكنك المساعدة؟",
    "A donor accepted the request for blood type {blood_type}.": "وافق أحد المتبرعين على طلب فصيلة الدم {blood_type}.",
    "Thank you for donating blood. Your kindness matters.": "شكرًا لتبرعك بالدم. لطفك يصنع فرقًا.",
    "Your response was recorded.": "تم تسجيل ردك.", "Thank you! The hospital will contact you.": "شكرًا لك! سيتواصل معك المستشفى.",
    "An error occurred": "حدث خطأ", "Invalid action": "إجراء غير صالح", "Not found": "غير موجود",
    "You cannot respond to this request": "لا يمكنك الرد على هذا الطلب",
}

KU = {
    "Arabic": "عەرەبی", "Kurdish (Sorani)": "کوردی (سۆرانی)", "English": "ئینگلیزی",
    "Donor Matcher - Kirkuk": "پلاتفۆرمی دۆزینەوەی بەخشەرانی خوێن - کەرکووک",
    "Notifications": "ئاگادارکردنەوەکان", "New notifications": "ئاگادارکردنەوە نوێکان", "No new notifications": "هیچ ئاگادارکردنەوەیەکی نوێ نییە",
    "Logout": "چوونەدەرەوە", "Login": "چوونەژوورەوە", "Register as donor": "خۆتۆمارکردن وەک بەخشەر",
    "Register hospital": "تۆمارکردنی نەخۆشخانە", "Language": "زمان", "Donor card": "کارتی بەخشەر",
    "Rewards": "خەڵاتەکان", "Rewards admin": "بەڕێوەبردنی خەڵاتەکان", "Help": "یارمەتی", "Why donate?": "بۆچی خوێن ببەخشین؟",
    "A blood unit at the right time saves a patient": "یەک یەکە خوێن لە کاتی گونجاودا ژیانی نەخۆشێک ڕزگار دەکات",
    "When a hospital in Kirkuk needs a rare blood type, we reach qualified nearby donors within minutes.": "کاتێک نەخۆشخانەیەک لە کەرکووک پێویستی بە جۆرێکی دەگمەن لە خوێن هەبێت، لە چەند خولەکێکدا بەخشەرە شیاوە نزیکەکان دەدۆزینەوە.",
    "Phone number": "ژمارەی تەلەفۆن", "Password": "وشەی نهێنی", "Password (at least 6 characters)": "وشەی نهێنی (لانیکەم ٦ پیت)",
    "You do not have an account?": "هەژمارت نییە؟", "or": "یان", "Sign in": "چوونەژوورەوە", "Register": "تۆمارکردن",
    "Register as a donor": "خۆتۆمارکردن وەک بەخشەر", "Hospital registration": "تۆمارکردنی نەخۆشخانە", "Register a hospital": "تۆمارکردنی نەخۆشخانە",
    "Full name": "ناوی تەواو", "Blood type": "جۆری خوێن", "District": "ناوچە", "Select district": "ناوچە هەڵبژێرە",
    "Select blood type": "جۆری خوێن هەڵبژێرە", "Gender": "ڕەگەز", "Male": "نێر", "Female": "مێ",
    "Birth date": "بەرواری لەدایکبوون", "Weight (kg)": "کێش (کگ)", "Create account": "دروستکردنی هەژمار",
    "I have an account": "هەژمارم هەیە", "Hospital name": "ناوی نەخۆشخانە", "Address": "ناونیشان",
    "Send registration request": "ناردنی داواکاری تۆمارکردن", "Donor dashboard": "داشبۆردی بەخشەر", "Last donation": "دواین بەخشین",
    "Not donated yet": "هێشتا هیچ بەخشینێک نەکراوە", "Available to donate now": "ئێستا ئامادەم بۆ بەخشین", "Currently unavailable": "لە ئێستادا بەردەست نیم",
    "Cases matching your blood type": "ئەو حاڵەتانەی لەگەڵ جۆری خوێنت دەگونجێن", "I can donate": "دەتوانم بەخشم", "I cannot": "ناتوانم",
    "No cases currently. We will notify you when a hospital needs your blood type.": "لە ئێستادا هیچ حاڵەتێک نییە. کاتێک نەخۆشخانەیەک پێویستی بە جۆری خوێنت هەبێت ئاگادارت دەکەینەوە.",
    "Your donation history": "مێژووی بەخشینەکانت", "You have no recorded donations yet.": "هێشتا هیچ بەخشینێکت تۆمار نەکراوە.",
    "Hospital dashboard": "داشبۆردی نەخۆشخانە", "Blood requests you published": "داواکارییەکانی خوێن کە بڵاوت کردوونەتەوە",
    "New blood request": "داواکارییەکی نوێی خوێن",
    "Your account is awaiting administrator approval. You can publish blood requests after approval.": "هەژمارەکەت چاوەڕێی پەسەندکردنی بەڕێوەبەرە. دوای پەسەندکردن دەتوانیت داواکاری خوێن بڵاوبکەیتەوە.",
    "No request published yet. Press “New blood request” to reach suitable donors.": "هێشتا هیچ داواکارییەک بڵاونەکراوەتەوە. «داواکارییەکی نوێی خوێن» دابگرە بۆ گەیشتن بە بەخشەرە گونجاوەکان.",
    "Patient blood type": "جۆری خوێنی نەخۆش", "Number of units": "ژمارەی یەکەکان", "Urgency": "ئاستی فۆریبوون",
    "Critical": "زۆر فۆری", "Urgent": "فۆری", "Normal": "ئاسایی", "Notes for donors (optional)": "تێبینی بۆ بەخشەرەکان (ئارەزوومەندانە)",
    "Post request and notify donors": "بڵاوکردنەوەی داواکاری و ئاگادارکردنەوەی بەخشەرەکان", "Back": "گەڕانەوە",
    "Overview": "پوختەی سیستەم", "Registered donors": "بەخشەرە تۆمارکراوەکان", "Approved hospitals": "نەخۆشخانە پەسەندکراوەکان",
    "Open requests": "داواکارییە کراوەکان", "Completed donations": "بەخشینە تەواوبووەکان", "Pending hospital approvals": "نەخۆشخانە چاوەڕوانەکانی پەسەندکردن",
    "Approve": "پەسەندکردن", "No pending registration requests.": "هیچ داواکارییەکی تۆمارکردنی چاوەڕوان نییە.",
    "Donors by blood type": "بەخشەرەکان بەپێی جۆری خوێن", "Request": "داواکاری", "Received": "وەرگیراو",
    "Accepted donors": "بەخشەرە ڕازیبووەکان", "Matching donors": "بەخشەرە گونجاوەکان", "Donor": "بەخشەر", "Status": "دۆخ",
    "Confirm donation": "پشتڕاستکردنەوەی بەخشین", "No eligible donors for this blood type currently.": "لە ئێستادا هیچ بەخشەرێکی شیاو بۆ ئەم جۆرەی خوێن نییە.",
    "The donor's phone number appears only after their approval.": "ژمارەی تەلەفۆنی بەخشەر تەنها دوای ڕەزامەندییەکەی دەردەکەوێت.",
    "Return home": "گەڕانەوە بۆ سەرەتا", "Cancel request": "هەڵوەشاندنەوەی داواکاری",
    "Are you sure you want to cancel this request?": "دڵنیایت دەتەوێت ئەم داواکارییە هەڵبوەشێنیتەوە؟", "Received units": "یەکە وەرگیراوەکان",
    "Donor name": "ناوی بەخشەر", "Area": "ناوچە", "Phone": "تەلەفۆن",
    "No eligible donors are currently available for this blood type.": "لە ئێستادا هیچ بەخشەرێکی شیاو بۆ ئەم جۆرەی خوێن بەردەست نییە.",
    "The donor's phone number is shown only after approval.": "ژمارەی تەلەفۆنی بەخشەر تەنها دوای پەسەندکردن دەردەکەوێت.",
    "Example: surgery tomorrow morning in the emergency department": "نموونە: نەشتەرگەری سبەی بەیانی لە بەشی فریاکەوتن",
    "Published on": "بڵاوکراوەتەوە لە", "Please fill in all fields": "تکایە هەموو خانەکان پڕ بکەرەوە",
    "Password must be at least 6 characters": "وشەی نهێنی دەبێت لانیکەم ٦ پیت بێت",
    "Account created successfully. Please sign in.": "هەژمارەکەت بە سەرکەوتوویی دروست کرا. تکایە بچۆ ژوورەوە.",
    "Phone number is already registered or the data is invalid": "ژمارەی تەلەفۆن پێشتر تۆمار کراوە یان زانیارییەکان نادروستن",
    "Registration submitted. Awaiting administrator approval.": "داواکارییەکە نێردرا. چاوەڕێی پەسەندکردنی بەڕێوەبەرە.",
    "Phone number is already registered": "ژمارەی تەلەفۆن پێشتر تۆمار کراوە", "Incorrect phone number or password": "ژمارەی تەلەفۆن یان وشەی نهێنی هەڵەیە",
    "Your account is awaiting administrator approval": "هەژمارەکەت چاوەڕێی پەسەندکردنی بەڕێوەبەرە", "Invalid number of units": "ژمارەی یەکەکان نادروستە",
    "Request published and {count} donors notified": "داواکارییەکە بڵاوکرایەوە و {count} بەخشەر ئاگادارکرانەوە",
    "Request not found": "داواکارییەکە نەدۆزرایەوە", "Donation confirmed": "بەخشین پشتڕاستکرایەوە",
    "Donation could not be confirmed": "نەتوانرا بەخشین پشتڕاست بکرێتەوە", "Request cancelled": "داواکارییەکە هەڵوەشێندرایەوە",
    "Hospital approved": "نەخۆشخانە پەسەندکرا", "Error": "هەڵە", "You are not allowed to open this page": "ڕێگەت پێنەدراوە ئەم پەڕەیە بکەیتەوە",
    "Page not found": "پەڕەکە نەدۆزرایەوە", "Digital donor card": "کارتی دیجیتاڵی بەخشەر", "Download QR": "داگرتنی کۆدی QR",
    "Verified donor": "بەخشەری پشتڕاستکراو", "Donor number": "ژمارەی بەخشەر", "Not recorded": "تۆمار نەکراوە",
    "Recorded donations": "بەخشینە تۆمارکراوەکان",
    "The QR code contains a protected verification link. Staff access is required to view records.": "کۆدی QR بەستەرێکی پارێزراوی پشتڕاستکردنەوەی تێدایە. بۆ بینینی تۆمارەکان دەبێت کارمەند بچێتە ژوورەوە.",
    "Donation helper": "یاریدەدەری بەخشینی خوێن", "Blood donation helper": "یاریدەدەری بەخشینی خوێن",
    "Friendly general information, not a medical diagnosis.": "زانیاریی گشتی و ئاسانە، نەک دەستنیشانکردنی پزیشکی.",
    "Ask about eligibility, preparation, blood types, recovery, or fear of needles.": "دەربارەی مەرجەکانی بەخشین، ئامادەکاری، جۆری خوێن، چاکبوونەوە یان ترسی دەرزی بپرسە.",
    "Question": "پرسیار", "How should I prepare?": "چۆن ئامادەکاری بکەم؟", "Ask": "بپرسە",
    "Donor rewards": "خەڵاتەکانی بەخشەر", "Points are awarded only after staff verify a donation.": "خاڵ تەنها دوای پشتڕاستکردنەوەی بەخشین لەلایەن کارمەندانەوە دەدرێت.",
    "points": "خاڵ", "Redeem": "گۆڕینەوە", "No rewards are currently available.": "لە ئێستادا هیچ خەڵاتێک بەردەست نییە.",
    "Redemption history": "مێژووی گۆڕینەوە", "No redemptions yet.": "هێشتا هیچ گۆڕینەوەیەک نییە.",
    "Manage rewards": "بەڕێوەبردنی خەڵاتەکان", "Reward name": "ناوی خەڵات", "Description": "وەسف", "Points": "خاڵ", "Add": "زیادکردن",
    "Active": "چالاک", "Inactive": "ناچالاک", "Disable": "ناچالاککردن", "Enable": "چالاککردن",
    "Authorized donor verification": "پشتڕاستکردنەوەی بەخشەری ڕێگەپێدراو", "QR token": "کۆدی QR", "Scan QR or paste verification token": "کۆدی QR بسکانە یان کۆدی پشتڕاستکردنەوە لێرە دابنێ",
    "Verify": "پشتڕاستکردنەوە", "This QR code is invalid or expired.": "ئەم کۆدەی QR نادروستە یان ماوەی بەسەرچووە.",
    "Verified donation records": "تۆمارە پشتڕاستکراوەکانی بەخشین", "No records found.": "هیچ تۆمارێک نەدۆزرایەوە.",
    "Last donation:": "دواین بەخشین:", "Recorded donations:": "بەخشینە تۆمارکراوەکان:",
    "Reward requested. Staff will follow up with you.": "داواکاریی خەڵات نێردرا. کارمەندان بەدواداچوونی بۆ دەکەن.",
    "Invalid reward.": "خەڵاتەکە نادروستە.", "You do not have enough points for this reward.": "خاڵی پێویستت بۆ ئەم خەڵاتە نییە.",
    "Reward name and a positive point cost are required.": "ناوی خەڵات و تێچوویەکی خاڵی زیاتر لە سفر پێویستن.",
    "Every donation matters": "هەر بەخشینێک گرنگە", "Your donation could be someone's second chance at life.": "بەخشینی تۆ دەتوانێت ببێتە هیوایەکی نوێ بۆ ژیانی کەسێک.",
    "Feeling nervous is normal. You do not have to pretend otherwise. Tell the donation team, ask questions, and take things one step at a time.": "هەستکردن بە دڵەڕاوکێ شتێکی ئاساییە. پێویست ناکات بیشاریتەوە. بە تیمی بەخشینەکە بڵێ، پرسیار بکە و هەنگاو بە هەنگاو بڕۆ.",
    "Why it matters": "بۆچی گرنگە؟",
    "Donated blood helps hospitals care for people after serious injuries, during surgery and childbirth complications, and throughout some cancer and blood-disorder treatments.": "خوێنی بەخشراو یارمەتی نەخۆشخانەکان دەدات چاودێری کەسانی تووشی برینی قورس، نەشتەرگەری، ئاڵۆزییەکانی منداڵبوون، هەندێک شێرپەنجە و نەخۆشییەکانی خوێن بکەن.",
    "A calm, guided process": "پرۆسەیەکی ئارام بە چاودێریی پسپۆڕان",
    "First, staff ask about your health and check whether donating is suitable. If you qualify, they guide you through the donation while you are seated, then ask you to rest.": "سەرەتا کارمەندان لە تەندروستییەکەت دەپرسن و دەبینن ئایا بەخشین بۆت گونجاوە. ئەگەر شیاو بیت، لە کاتی دانیشتندا ڕێنماییت دەکەن و دوای تەواوبوون داوات لێدەکەن پشووبدەیت.",
    "Small steps that can make it easier": "چەند هەنگاوێکی بچووک بۆ ئاسانکردنی ئەزموونەکە",
    "Eat a normal meal, drink water, sleep well, and wear comfortable clothing. Tell staff if needles make you nervous. You can look away, breathe slowly, and ask to pause.": "خواردنی ئاسایی بخۆ، ئاو بخۆرەوە، باش بخەوە و جلێکی ئاسوودە لەبەر بکە. ئەگەر دەرزیت دەترسێنێت بە کارمەندان بڵێ. دەتوانیت لایەکی تر بڕوانیتەوە، بە هێواشی هەناسە بدەیت و داوای پشوودان بکەیت.",
    "You are in control": "بڕیار لە دەستی خۆتە",
    "You can ask questions before you begin. Screening is private, trained staff supervise the process, and you can tell them if you feel uncomfortable. Never donate when you feel unwell.": "پێش دەستپێکردن دەتوانیت پرسیار بکەیت. پشکنینەکە نهێنییە و کارمەندی ڕاهێنراو چاودێری پرۆسەکە دەکات. ئەگەر ئاسوودە نەبوویت بەوان بڵێ، و کاتێک نەخۆشیت بەخشین مەکە.",
    "One donation is a meaningful act of care.": "یەک جار بەخشین کردارێکی بەهادارە بۆ یارمەتیدانی کەسانی تر.",
    "Thank you for considering it. Donating is voluntary, and your health comes first.": "سوپاس بۆ بیرکردنەوەت لە بەخشین. بەخشین بە ئارەزووی خۆتە و تەندروستیی تۆ لە هەموو شتێک گرنگترە.",
    "Talk to trained staff": "لەگەڵ کارمەندی ڕاهێنراو قسە بکە",
    "Eligibility depends on your health and local blood-service rules. The donation team makes the final decision.": "شیاوی بەخشین بە تەندروستییەکەت و ڕێنمایی خزمەتگوزاریی خوێنی ناوخۆیی پەیوەستە. تیمی بەخشین بڕیاری کۆتایی دەدات.",
    "I feel nervous about needles.": "لە دەرزی دەترسم.",
    "A little fear does not mean you cannot donate. Tell the staff before the process starts. They can explain each step, help you lie back if appropriate, and give you time to feel ready. You can pause or stop at any point.": "ترسێکی کەم واتای ئەوە نییە ناتوانیت خوێن ببەخشیت. پێش دەستپێکردن بە کارمەندان بڵێ. دەتوانن هەر هەنگاوێک ڕوون بکەنەوە، ئەگەر پێویست بوو یارمەتیت بدەن پاڵ بکەویت و کاتت بدەن تا ئامادە بیت. هەر کاتێک دەتوانیت داوای پشوودان یان وەستان بکەیت.",
    "A hospital needs blood type {blood_type} at {hospital}. Can you help?": "نەخۆشخانەی {hospital} پێویستی بە جۆری خوێنی {blood_type} هەیە. دەتوانیت یارمەتی بدەیت؟",
    "A donor accepted the request for blood type {blood_type}.": "بەخشەرێک داواکاریی جۆری خوێنی {blood_type}ی قبووڵ کرد.",
    "Thank you for donating blood. Your kindness matters.": "سوپاس بۆ بەخشینی خوێن. میهرەبانیت گرنگە.",
    "Your response was recorded.": "وەڵامەکەت تۆمارکرا.", "Thank you! The hospital will contact you.": "سوپاس! نەخۆشخانە پەیوەندیت پێوە دەکات.",
    "An error occurred": "هەڵەیەک ڕوویدا", "Invalid action": "کردارێکی نادروست", "Not found": "نەدۆزرایەوە",
    "You cannot respond to this request": "ناتوانیت وەڵامی ئەم داواکارییە بدەیتەوە",
}


# Additional labels and chatbot responses are kept here too, so AJAX and
# template-rendered text use the exact same wording in every language.
EN.update({
    "units": "units",
    "We use your blood type and district to find suitable requests. Your phone number is never shown to a hospital before you accept a request.": "We use your blood type and district to find suitable requests. Your phone number is never shown to a hospital before you accept a request.",
    "Reward added.": "Reward added.",
    "requested": "Requested", "fulfilled": "Fulfilled", "cancelled": "Cancelled",
    "Please ask a blood donation question. For urgent concerns, contact a healthcare professional.": "Please ask a blood donation question. For urgent concerns, contact a healthcare professional.",
    "Eligibility depends on your local blood service. Common requirements include being healthy, meeting the local age and weight limits, and passing a confidential screening. Staff make the final decision; do not donate if you feel unwell. This information is general and does not replace professional medical advice.": "Eligibility depends on your local blood service. Common requirements include being healthy, meeting the local age and weight limits, and passing a confidential screening. Staff make the final decision; do not donate if you feel unwell. This information is general and does not replace professional medical advice.",
    "Before donating, eat a normal meal, drink water, sleep well, and bring identification. Avoid donating when ill and tell staff about medicines or medical conditions. This information is general and does not replace professional medical advice.": "Before donating, eat a normal meal, drink water, sleep well, and bring identification. Avoid donating when ill and tell staff about medicines or medical conditions. This information is general and does not replace professional medical advice.",
    "After donation, rest briefly, drink extra fluids, and keep the bandage on as instructed. Avoid strenuous activity for the period recommended by staff. Seek medical help for severe or persistent symptoms. This information is general and does not replace professional medical advice.": "After donation, rest briefly, drink extra fluids, and keep the bandage on as instructed. Avoid strenuous activity for the period recommended by staff. Seek medical help for severe or persistent symptoms. This information is general and does not replace professional medical advice.",
    "It is normal to feel nervous. The needle prick is brief and the process is supervised. Tell the staff about your fear, breathe slowly, and look away if that helps. You can stop and ask questions at any time. This information is general and does not replace professional medical advice.": "It is normal to feel nervous. The needle prick is brief and the process is supervised. Tell the staff about your fear, breathe slowly, and look away if that helps. You can stop and ask questions at any time. This information is general and does not replace professional medical advice.",
    "Compatibility depends on the blood component and recipient. O negative is commonly used for emergency red-cell transfusion, but hospitals confirm compatibility with testing. Never rely on a chat answer for a transfusion decision. This information is general and does not replace professional medical advice.": "Compatibility depends on the blood component and recipient. O negative is commonly used for emergency red-cell transfusion, but hospitals confirm compatibility with testing. Never rely on a chat answer for a transfusion decision. This information is general and does not replace professional medical advice.",
    "You register, answer a health questionnaire, complete a private screening, donate while seated, and rest afterward. A trained professional supervises each step. This information is general and does not replace professional medical advice.": "You register, answer a health questionnaire, complete a private screening, donate while seated, and rest afterward. A trained professional supervises each step. This information is general and does not replace professional medical advice.",
    "Use the donation-center information provided by your local hospital or blood service. BloodConnect can connect registered donors with matching hospital requests. This information is general and does not replace professional medical advice.": "Use the donation-center information provided by your local hospital or blood service. BloodConnect can connect registered donors with matching hospital requests. This information is general and does not replace professional medical advice.",
    "I can help with eligibility, preparation, the donation process, recovery, blood-type basics, or managing fear. For personal medical advice, please speak with qualified donation staff.": "I can help with eligibility, preparation, the donation process, recovery, blood-type basics, or managing fear. For personal medical advice, please speak with qualified donation staff.",
})
AR.update({
    "units": "وحدات",
    "We use your blood type and district to find suitable requests. Your phone number is never shown to a hospital before you accept a request.": "نستخدم فصيلة دمك ومنطقتك للعثور على الطلبات المناسبة. لا يظهر رقم هاتفك للمستشفى قبل موافقتك على الطلب.",
    "Reward added.": "تمت إضافة المكافأة.",
    "requested": "قيد الطلب", "fulfilled": "مكتمل", "cancelled": "ملغى",
    "Please ask a blood donation question. For urgent concerns, contact a healthcare professional.": "يرجى طرح سؤال عن التبرع بالدم. في الحالات العاجلة، تواصل مع مختص صحي.",
    "Eligibility depends on your local blood service. Common requirements include being healthy, meeting the local age and weight limits, and passing a confidential screening. Staff make the final decision; do not donate if you feel unwell. This information is general and does not replace professional medical advice.": "تعتمد الأهلية على تعليمات خدمة الدم المحلية. وتشمل الشروط الشائعة التمتع بصحة جيدة واستيفاء حدود العمر والوزن واجتياز فحص سري. يحدد الطاقم أهليتك النهائية، ولا تتبرع إذا كنت متوعكًا. هذه معلومات عامة ولا تحل محل المشورة الطبية المتخصصة.",
    "Before donating, eat a normal meal, drink water, sleep well, and bring identification. Avoid donating when ill and tell staff about medicines or medical conditions. This information is general and does not replace professional medical advice.": "قبل التبرع، تناول وجبة معتادة واشرب الماء ونم جيدًا وأحضر إثبات الهوية. تجنب التبرع عندما تكون مريضًا وأخبر الطاقم بالأدوية أو الحالات الصحية التي لديك. هذه معلومات عامة ولا تحل محل المشورة الطبية المتخصصة.",
    "After donation, rest briefly, drink extra fluids, and keep the bandage on as instructed. Avoid strenuous activity for the period recommended by staff. Seek medical help for severe or persistent symptoms. This information is general and does not replace professional medical advice.": "بعد التبرع، استرح قليلًا واشرب سوائل إضافية واترك الضماد حسب تعليمات الطاقم. تجنب النشاط الشاق للمدة التي يوصي بها الموظفون. اطلب المساعدة الطبية عند ظهور أعراض شديدة أو مستمرة. هذه معلومات عامة ولا تحل محل المشورة الطبية المتخصصة.",
    "It is normal to feel nervous. The needle prick is brief and the process is supervised. Tell the staff about your fear, breathe slowly, and look away if that helps. You can stop and ask questions at any time. This information is general and does not replace professional medical advice.": "من الطبيعي الشعور بالتوتر. وخزة الإبرة قصيرة والعملية تحت إشراف المختصين. أخبر الطاقم بمخاوفك، وتنفس ببطء، وانظر إلى جهة أخرى إن كان ذلك يساعدك. يمكنك التوقف وطرح الأسئلة في أي وقت. هذه معلومات عامة ولا تحل محل المشورة الطبية المتخصصة.",
    "Compatibility depends on the blood component and recipient. O negative is commonly used for emergency red-cell transfusion, but hospitals confirm compatibility with testing. Never rely on a chat answer for a transfusion decision. This information is general and does not replace professional medical advice.": "يعتمد توافق الدم على مكوّن الدم وحالة المريض. تُستخدم فصيلة O سالب أحيانًا في نقل كريات الدم الحمراء الطارئ، لكن المستشفى يؤكد التوافق بالفحوصات. لا تعتمد على إجابة محادثة لاتخاذ قرار نقل الدم. هذه معلومات عامة ولا تحل محل المشورة الطبية المتخصصة.",
    "You register, answer a health questionnaire, complete a private screening, donate while seated, and rest afterward. A trained professional supervises each step. This information is general and does not replace professional medical advice.": "تسجل بياناتك، وتجيب عن أسئلة صحية، وتجتاز فحصًا سريًا، ثم تتبرع وأنت جالس وتستريح بعد ذلك. يشرف مختص مدرب على كل خطوة. هذه معلومات عامة ولا تحل محل المشورة الطبية المتخصصة.",
    "Use the donation-center information provided by your local hospital or blood service. BloodConnect can connect registered donors with matching hospital requests. This information is general and does not replace professional medical advice.": "اعتمد على معلومات مركز التبرع التي يقدمها مستشفاك أو خدمة الدم المحلية. تساعد BloodConnect في ربط المتبرعين المسجلين بطلبات المستشفيات المناسبة. هذه معلومات عامة ولا تحل محل المشورة الطبية المتخصصة.",
    "I can help with eligibility, preparation, the donation process, recovery, blood-type basics, or managing fear. For personal medical advice, please speak with qualified donation staff.": "يمكنني مساعدتك بمعلومات عن الأهلية والاستعداد وخطوات التبرع والتعافي وفصائل الدم والتعامل مع الخوف. للاستشارة الطبية الشخصية، تحدث مع طاقم التبرع المختص.",
})
KU.update({
    "units": "یەکە",
    "We use your blood type and district to find suitable requests. Your phone number is never shown to a hospital before you accept a request.": "جۆری خوێن و ناوچەکەت بەکاردەهێنین بۆ دۆزینەوەی داواکاریی گونجاو. ژمارەی تەلەفۆنت پێش قبووڵکردنی داواکارییەکە بۆ نەخۆشخانە نیشان نادرێت.",
    "Reward added.": "خەڵاتەکە زیادکرا.",
    "requested": "داواکراوە", "fulfilled": "تەواوبووە", "cancelled": "هەڵوەشێندراوەتەوە",
    "Please ask a blood donation question. For urgent concerns, contact a healthcare professional.": "تکایە پرسیارێک دەربارەی بەخشینی خوێن بکە. بۆ کێشەی فۆری پەیوەندی بە پسپۆڕێکی تەندروستییەوە بکە.",
    "Eligibility depends on your local blood service. Common requirements include being healthy, meeting the local age and weight limits, and passing a confidential screening. Staff make the final decision; do not donate if you feel unwell. This information is general and does not replace professional medical advice.": "شیاوی بەخشین بە ڕێنمایی خزمەتگوزاریی خوێنی ناوخۆیی پەیوەستە. مەرجە باوەکان تەندروستیی باش، گونجانی تەمەن و کێش و تێپەڕاندنی پشکنینی نهێنین. کارمەندان بڕیاری کۆتایی دەدەن؛ ئەگەر هەست بە نەخۆشی دەکەیت خوێن مەبەخشە. ئەم زانیارییانە گشتین و جێگەی ڕاوێژی پزیشکی ناگرنەوە.",
    "Before donating, eat a normal meal, drink water, sleep well, and bring identification. Avoid donating when ill and tell staff about medicines or medical conditions. This information is general and does not replace professional medical advice.": "پێش بەخشین خواردنێکی ئاسایی بخۆ، ئاو بخۆرەوە، باش بخەوە و ناسنامە لەگەڵ خۆت بهێنە. کاتێک نەخۆشیت بەخشین مەکە و دەربارەی دەرمان و نەخۆشییەکانت بە کارمەندان بڵێ. ئەم زانیارییانە گشتین و جێگەی ڕاوێژی پزیشکی ناگرنەوە.",
    "After donation, rest briefly, drink extra fluids, and keep the bandage on as instructed. Avoid strenuous activity for the period recommended by staff. Seek medical help for severe or persistent symptoms. This information is general and does not replace professional medical advice.": "دوای بەخشین کەمێک پشووبدە، شلەی زیاتر بخۆرەوە و پانسمانەکە بەپێی ڕێنمایی کارمەندان بهێڵەوە. بۆ ئەو ماوەیەی کارمەندان دیاری دەکەن لە چاڵاکیی قورس خۆت بپارێزە. ئەگەر نیشانەی توند یان بەردەوامت هەبوو یارمەتیی پزیشکی وەربگرە. ئەم زانیارییانە گشتین و جێگەی ڕاوێژی پزیشکی ناگرنەوە.",
    "It is normal to feel nervous. The needle prick is brief and the process is supervised. Tell the staff about your fear, breathe slowly, and look away if that helps. You can stop and ask questions at any time. This information is general and does not replace professional medical advice.": "هەستکردن بە دڵەڕاوکێ ئاساییە. چوونەژووری دەرزییەکە کورتە و پرۆسەکە چاودێری دەکرێت. لە ترسەکەت بە کارمەندان بڵێ، بە هێواشی هەناسە بدە و ئەگەر یارمەتیت دەدات لایەکی تر بڕوانە. هەر کاتێک دەتوانیت بوەستیت و پرسیار بکەیت. ئەم زانیارییانە گشتین و جێگەی ڕاوێژی پزیشکی ناگرنەوە.",
    "Compatibility depends on the blood component and recipient. O negative is commonly used for emergency red-cell transfusion, but hospitals confirm compatibility with testing. Never rely on a chat answer for a transfusion decision. This information is general and does not replace professional medical advice.": "گونجانی خوێن بە پێکهاتەی خوێن و نەخۆشەکەوە پەیوەستە. O نێگەتیڤ لە هەندێک بارودۆخی فریاکەوتندا بۆ گواستنەوەی خانە سوورەکان بەکاردێت، بەڵام نەخۆشخانە بە پشکنین گونجانەکە پشتڕاست دەکاتەوە. بۆ بڕیاری گواستنەوەی خوێن پشت بە وەڵامی چاتبۆت مەبەستە. ئەم زانیارییانە گشتین و جێگەی ڕاوێژی پزیشکی ناگرنەوە.",
    "You register, answer a health questionnaire, complete a private screening, donate while seated, and rest afterward. A trained professional supervises each step. This information is general and does not replace professional medical advice.": "تۆمار دەبیت، پرسیارنامەی تەندروستی پڕ دەکەیتەوە، پشکنینێکی نهێنی ئەنجام دەدەیت، لە کاتی دانیشتندا خوێن دەبەخشیت و پاشان پشوودەدەیت. کەسێکی ڕاهێنراو چاودێری هەر هەنگاوێک دەکات. ئەم زانیارییانە گشتین و جێگەی ڕاوێژی پزیشکی ناگرنەوە.",
    "Use the donation-center information provided by your local hospital or blood service. BloodConnect can connect registered donors with matching hospital requests. This information is general and does not replace professional medical advice.": "زانیاریی ناوەندی بەخشین کە لەلایەن نەخۆشخانە یان خزمەتگوزاریی خوێنی ناوخۆییەوە پێشکەش دەکرێت بەکاربهێنە. BloodConnect دەتوانێت بەخشەرە تۆمارکراوەکان بە داواکاریی گونجاوی نەخۆشخانەکانەوە ببەستێتەوە. ئەم زانیارییانە گشتین و جێگەی ڕاوێژی پزیشکی ناگرنەوە.",
    "I can help with eligibility, preparation, the donation process, recovery, blood-type basics, or managing fear. For personal medical advice, please speak with qualified donation staff.": "دەتوانم یارمەتیت بدەم لەبارەی شیاوی بەخشین، ئامادەکاری، پرۆسەی بەخشین، چاکبوونەوە، بنەماکانی جۆری خوێن و چۆنیەتی کەمکردنەوەی ترس. بۆ ڕاوێژی پزیشکی تایبەتی، لەگەڵ کارمەندی پسپۆڕ قسە بکە.",
})


# Public project trailer and creator credits.
EN.update({
    "BloodConnect": "BloodConnect",
    "A community-powered blood donation project": "A community-powered blood donation project",
    "Every drop can make a difference.": "Every drop can make a difference.",
    "BloodConnect connects communities with the idea of voluntary blood donation and helps people understand how hospitals and donors can work together.": "BloodConnect connects communities with the idea of voluntary blood donation and helps people understand how hospitals and donors can work together.",
    "Explore the demo": "Explore the demo",
    "How it works": "How it works",
    "Hospital": "Hospital", "Donor": "Donor", "Administrator": "Administrator",
    "Create a blood request": "Create a blood request",
    "Review matching requests and respond": "Review matching requests and respond",
    "Approve hospitals and oversee activity": "Approve hospitals and oversee activity",
    "Be part of the change": "Be part of the change",
    "Learn about blood donation, share the message, and encourage safe voluntary donation in your community.": "Learn about blood donation, share the message, and encourage safe voluntary donation in your community.",
    "Created by": "Created by",
    "The team behind BloodConnect": "The team behind BloodConnect",
    "Try the live demonstration": "Try the live demonstration",
    "This is a demonstration project. Use the sample accounts to explore the workflow. Do not enter real donor or patient information.": "This is a demonstration project. Use the sample accounts to explore the workflow. Do not enter real donor or patient information.",
})
AR.update({
    "A community-powered blood donation project": "مشروع مجتمعي للتوعية بالتبرع بالدم",
    "Every drop can make a difference.": "كل قطرة دم يمكن أن تصنع فرقاً.",
    "BloodConnect connects communities with the idea of voluntary blood donation and helps people understand how hospitals and donors can work together.": "يربط BloodConnect المجتمع بفكرة التبرع الطوعي بالدم، ويساعد الناس على فهم كيفية تعاون المستشفيات والمتبرعين.",
    "Explore the demo": "استكشف النسخة التجريبية",
    "How it works": "كيف يعمل",
    "Hospital": "المستشفى", "Donor": "المتبرع", "Administrator": "المدير",
    "Create a blood request": "إنشاء طلب دم",
    "Review matching requests and respond": "مراجعة الطلبات المطابقة والرد عليها",
    "Approve hospitals and oversee activity": "الموافقة على المستشفيات ومتابعة النشاط",
    "Be part of the change": "كن جزءاً من التغيير",
    "Learn about blood donation, share the message, and encourage safe voluntary donation in your community.": "تعرّف على التبرع بالدم، وشارك الرسالة، وشجّع التبرع الطوعي الآمن في مجتمعك.",
    "Created by": "إعداد",
    "The team behind BloodConnect": "الفريق الذي يقف وراء BloodConnect",
    "Try the live demonstration": "جرّب العرض التفاعلي",
    "This is a demonstration project. Use the sample accounts to explore the workflow. Do not enter real donor or patient information.": "هذا مشروع تجريبي. استخدم الحسابات النموذجية لاستكشاف طريقة العمل. لا تدخل بيانات حقيقية للمتبرعين أو المرضى.",
})
KU.update({
    "A community-powered blood donation project": "پڕۆژەیەکی کۆمەڵایەتی بۆ هۆشیاری بەخشینی خوێن",
    "Every drop can make a difference.": "هەر دڵۆپێک دەتوانێت جیاوازی دروست بکات.",
    "BloodConnect connects communities with the idea of voluntary blood donation and helps people understand how hospitals and donors can work together.": "BloodConnect کۆمەڵگا بە بیرۆکەی بەخشینی ئارەزوومەندانەی خوێنەوە دەبەستێتەوە و یارمەتی خەڵک دەدات تێبگەن نەخۆشخانە و بەخشەران چۆن پێکەوە کار دەکەن.",
    "Explore the demo": "نموونەکە بپشکنە",
    "How it works": "چۆن کار دەکات",
    "Hospital": "نەخۆشخانە", "Donor": "بەخشەر", "Administrator": "بەڕێوەبەر",
    "Create a blood request": "داواکاریی خوێن دروست بکە",
    "Review matching requests and respond": "داواکارییە گونجاوەکان ببینە و وەڵام بدەرەوە",
    "Approve hospitals and oversee activity": "پەسەندکردنی نەخۆشخانەکان و چاودێریکردنی چالاکی",
    "Be part of the change": "بەشداربە لە گۆڕانکارییەکە",
    "Learn about blood donation, share the message, and encourage safe voluntary donation in your community.": "دەربارەی بەخشینی خوێن فێربە، پەیامەکە بڵاو بکەرەوە و بەخشینی ئارەزوومەندانەی سەلامەت لە کۆمەڵگاکەتدا هان بدە.",
    "Created by": "دروستکراوە لەلایەن",
    "The team behind BloodConnect": "تیمی پشت BloodConnect",
    "Try the live demonstration": "نموونەی کارلێککار تاقی بکەرەوە",
    "This is a demonstration project. Use the sample accounts to explore the workflow. Do not enter real donor or patient information.": "ئەمە پڕۆژەیەکی تاقیکردنەوەیە. هەژمارە نموونەییەکان بەکاربهێنە بۆ تاقیکردنەوەی کارکردن. زانیاریی ڕاستەقینەی بەخشەر یان نەخۆش مەنووسە.",
})


EN.update({
    "Scan to explore BloodConnect": "Scan to explore BloodConnect",
    "Scan this QR code with your phone camera to open the BloodConnect demo.": "Scan this QR code with your phone camera to open the BloodConnect demo.",
    "Open BloodConnect demo": "Open BloodConnect demo",
})
AR.update({
    "Scan to explore BloodConnect": "امسح الرمز لاستكشاف BloodConnect",
    "Scan this QR code with your phone camera to open the BloodConnect demo.": "امسح رمز QR بكاميرا هاتفك لفتح النسخة التجريبية من BloodConnect.",
    "Open BloodConnect demo": "افتح النسخة التجريبية من BloodConnect",
})
KU.update({
    "Scan to explore BloodConnect": "QR کۆدەکە بسکەنە بۆ ناسینی BloodConnect",
    "Scan this QR code with your phone camera to open the BloodConnect demo.": "بە کامێرای مۆبایلەکەت ئەم QR کۆدە بسکەنە بۆ کردنەوەی نموونەی BloodConnect.",
    "Open BloodConnect demo": "نموونەی BloodConnect بکەرەوە",
})

TRANSLATIONS = {"ar": AR, "ku": KU, "en": EN}

DISTRICTS = {
    "وسط كركوك": {"en": "Kirkuk Center", "ku": "ناوەندی کەرکووک"},
    "رحيم آوه": {"en": "Rahimawa", "ku": "ڕەحیم ئاوا"},
    "واسطي": {"en": "Wasiti", "ku": "واسیتی"},
    "عرفة": {"en": "Arafa", "ku": "عەڕەفە"},
    "شورجة": {"en": "Shorja", "ku": "شۆڕجە"},
    "الحويجة": {"en": "Hawija", "ku": "حەویجە"},
    "داقوق": {"en": "Daquq", "ku": "داقووق"},
    "الدبس": {"en": "Dibis", "ku": "دەبس"},
}


def current_language():
    language = session.get("language", "ar")
    return language if language in TRANSLATIONS else "ar"


def translate(text):
    """Translate a canonical English interface string for the active session."""
    language = current_language()
    return TRANSLATIONS[language].get(text, EN.get(text, text))


def district_label(arabic_name):
    """Return a district name in the active interface language."""
    if not arabic_name:
        return ""
    if current_language() == "ar":
        return arabic_name
    return DISTRICTS.get(arabic_name, {}).get(current_language(), arabic_name)


def translate_notification(message):
    """Translate legacy notification rows that were stored in Arabic."""
    if not message:
        return message
    lang = current_language()
    if lang == "ar":
        return message

    request_match = re.match(r"طلب دم عاجل لفصيلة (.+?) في (.+?)\. هل تستطيع التبرع؟", message)
    if request_match:
        blood_type, hospital = request_match.groups()
        return translate("A hospital needs blood type {blood_type} at {hospital}. Can you help?").format(
            blood_type=blood_type, hospital=hospital
        )

    donor_match = re.match(r"متبرع جديد وافق على طلب فصيلة (.+)", message)
    if donor_match:
        return translate("A donor accepted the request for blood type {blood_type}.").format(
            blood_type=donor_match.group(1)
        )

    if message == "شكرًا لتبرعك بالدم! أنقذت حياة بإذن الله":
        return translate("Thank you for donating blood. Your kindness matters.")
    if message == "Invalid reward.":
        return translate("Invalid reward.")
    return message


# ---- security hardening strings (review the Kurdish text with a native speaker) ----
EN.update({
    "Password (at least 6 characters)": "Password (at least 8 characters, letters and numbers)",
    "Password must be at least 8 characters and include letters and numbers":
        "Password must be at least 8 characters and include letters and numbers",
    "Too many attempts. Please try again later.": "Too many attempts. Please try again later.",
    "Invalid request. Please reload the page and try again.": "Invalid request. Please reload the page and try again.",
    "Something went wrong. Please try again.": "Something went wrong. Please try again.",
    "Please check the data you entered": "Please check the data you entered",
    "Delete my account": "Delete my account",
    "This permanently removes your personal data. Enter your password to confirm.":
        "This permanently removes your personal data. Enter your password to confirm.",
    "Your account and personal data were deleted.": "Your account and personal data were deleted.",
    "Incorrect password": "Incorrect password",
    "Generate a new card (the old QR stops working)": "Generate a new card (the old QR stops working)",
    "Card renewed. The previous QR code no longer works.": "Card renewed. The previous QR code no longer works.",
})
AR.update({
    "Password (at least 6 characters)": "كلمة المرور (8 أحرف على الأقل، حروف وأرقام)",
    "Password must be at least 8 characters and include letters and numbers":
        "يجب ألا تقل كلمة المرور عن 8 أحرف وأن تحتوي على حروف وأرقام",
    "Too many attempts. Please try again later.": "محاولات كثيرة جدًا. حاول مجددًا لاحقًا.",
    "Invalid request. Please reload the page and try again.": "طلب غير صالح. أعد تحميل الصفحة وحاول مرة أخرى.",
    "Something went wrong. Please try again.": "حدث خطأ ما. حاول مرة أخرى.",
    "Please check the data you entered": "يرجى التحقق من البيانات المدخلة",
    "Delete my account": "حذف حسابي",
    "This permanently removes your personal data. Enter your password to confirm.":
        "سيؤدي هذا إلى حذف بياناتك الشخصية نهائيًا. أدخل كلمة المرور للتأكيد.",
    "Your account and personal data were deleted.": "تم حذف حسابك وبياناتك الشخصية.",
    "Incorrect password": "كلمة المرور غير صحيحة",
    "Generate a new card (the old QR stops working)": "إنشاء بطاقة جديدة (يتوقف رمز QR القديم)",
    "Card renewed. The previous QR code no longer works.": "تم تجديد البطاقة. لم يعد رمز QR السابق يعمل.",
})
KU.update({
    "Password (at least 6 characters)": "وشەی نهێنی (لانیکەم ٨ پیت، پیت و ژمارە)",
    "Password must be at least 8 characters and include letters and numbers":
        "وشەی نهێنی دەبێت لانیکەم ٨ پیت بێت و پیت و ژمارەی تێدا بێت",
    "Too many attempts. Please try again later.": "هەوڵی زۆر دراوە. تکایە دواتر دووبارە هەوڵ بدەرەوە.",
    "Invalid request. Please reload the page and try again.": "داواکارییەکە دروست نییە. لاپەڕەکە نوێ بکەرەوە و دووبارە هەوڵ بدەرەوە.",
    "Something went wrong. Please try again.": "هەڵەیەک ڕوویدا. تکایە دووبارە هەوڵ بدەرەوە.",
    "Please check the data you entered": "تکایە ئەو زانیارییانەی نووسیوتە بپشکنە",
    "Delete my account": "سڕینەوەی هەژمارەکەم",
    "This permanently removes your personal data. Enter your password to confirm.":
        "ئەمە زانیارییە کەسییەکانت بۆ هەمیشە دەسڕێتەوە. بۆ دڵنیابوونەوە وشەی نهێنی بنووسە.",
    "Your account and personal data were deleted.": "هەژمارەکەت و زانیارییە کەسییەکانت سڕانەوە.",
    "Incorrect password": "وشەی نهێنی هەڵەیە",
    "Generate a new card (the old QR stops working)": "دروستکردنی کارتی نوێ (QRی کۆن کار ناکات)",
    "Card renewed. The previous QR code no longer works.": "کارتەکە نوێکرایەوە. QRی پێشوو چیتر کار ناکات.",
})
