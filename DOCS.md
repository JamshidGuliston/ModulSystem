# ModulSystem — Loyiha Hujjati

> Versiya: 2026-03-09
> Mualliflar: Jamshid Guliston + Claude AI

---

## 1. Loyiha haqida

**ModulSystem** — o'qituvchilar o'z talabalarini onlayn o'qitishi uchun yaratilgan platforma.
Har bir o'qituvchi o'z domeniga ega bo'lib, alohida Angular frontend orqali ishlaydi.
Backend — yagona Django REST API, barcha frontendlarga xizmat qiladi.

### Asosiy g'oya

```
O'qituvchi (Teacher)
  ├── O'z Angular fronti (har teacher uchun alohida deploy)
  ├── O'z talabalari (Student — faqat shu teacherga ko'rinadi)
  └── O'z kurslari (Module → Lesson → Assignment → Question)
```

---

## 2. Texnologiyalar

| Qism | Stack |
|---|---|
| Backend | Django 6.0, Django REST Framework 3.16 |
| Ma'lumotlar bazasi | PostgreSQL (production), SQLite (development) |
| Frontend | Angular 19 (standalone components, signals) |
| Autentifikatsiya | Custom Token (Django User ishlatilmaydi) |
| Admin panel | Django Admin (django-jazzmin) |
| Fayl import | python-docx |
| Deploy | Gunicorn + WhiteNoise |

---

## 3. Papkalar tuzilmasi

### Backend (`d:\Proekt\Django\modulsystem\`)

```
modulsystem/
├── config/               # Django sozlamalari
│   ├── settings.py
│   ├── urls.py           # Asosiy URL router
│   └── wsgi.py / asgi.py
├── accounts/             # Teacher va Student modellari
├── courses/              # Module, Lesson modellari
├── assignments/          # AssignmentType, Assignment, AssignmentPart, Question
├── progress/             # StudentModuleEnrollment, AssignmentAttempt, QuestionAnswer
├── requirements.txt
├── manage.py
└── DOCS.md               # Bu fayl
```

### Frontendlar (`d:\Proekt\Angular\TeacherModuls\`)

```
TeacherModuls/
├── NilufarModul/app/     # Nilufar teacher uchun frontend
├── AzizaModul/           # Aziza teacher uchun frontend
├── LatifModulFront/      # Latif teacher uchun frontend
└── InformatikaMock/      # Informatika kursi fronti
```

---

## 4. Ma'lumotlar modellari

### 4.1 accounts app

#### `Teacher`
```
id            UUID (PK)
email         unique
password      CharField (hashed)
full_name     CharField
avatar        URL (nullable)
bio           TextField (nullable)
settings      JSONField (nullable)
domain        unique CharField — teacher.example.com
api_token     64 belgi, avtomatik yaratiladi
is_active     Boolean
created_at / updated_at
```

#### `Student`
```
id            UUID (PK)
teacher       FK → Teacher (CASCADE) — talaba faqat bitta teacherga tegishli
email         CharField
password      CharField
full_name     CharField
avatar        URL (nullable)
is_active     Boolean
created_at / updated_at
```

> ⚠️ Student emaili global unique emas — har teacher o'z student bazasiga ega.

---

### 4.2 courses app

#### `Module`
```
id              UUID (PK)
teacher         FK → Teacher (CASCADE)
title           CharField(255)
description     TextField (nullable)
thumbnail       URL (nullable)
order_index     Integer
is_sequential   Boolean — darslar tartibda o'tilishi shart
is_published    Boolean
created_at / updated_at
```

#### `Lesson` — Daraxt tuzilmasi
```
id                          UUID (PK)
module                      FK → Module (nullable) — faqat root lessonlarda
parent                      FK → self (nullable) — child lesson (bosqich/stage)
title                       CharField(255)
description                 TextField (nullable)
order_index                 Integer
is_sequential               Boolean
required_completion_percent Integer (default: 80)
is_published                Boolean
created_at / updated_at
```

**Lesson daraxt qoidasi:**
- `parent=null, module=modul` → **Root lesson** (oddiy dars yoki mavzu)
- `parent=lesson, module=null` → **Child lesson** (bosqich/stage)

```
Module
  └── Lesson (root, parent=null)          ← Mavzu
        └── Lesson (child, parent=mavzu)  ← Bosqich/Stage
              └── Assignment
```

#### `ContentType`
```
id          UUID
name        CharField(50)
icon        CharField (nullable)
description CharField (nullable)
```

#### `ModuleContent` / `LessonContent`
```
id            UUID
module/lesson FK
content_type  FK → ContentType
title         CharField(255)
content       TextField (matn uchun)
file_url      CharField
video_url     CharField
order_index   Integer
```

---

### 4.3 assignments app

#### `AssignmentType`
```
id              UUID (PK)
teacher         FK → Teacher (nullable) — null=barcha teacherlar uchun global
name            CharField(50)
description     CharField(255, nullable)
config_schema   JSONField (nullable)
grader_type     CharField: auto | ai | teacher | peer | self | none
```

**Standart (global) turlar — 15 ta:**

| name | grader_type | Tavsif |
|---|---|---|
| `multiple_choice` | auto | Ko'p tanlovli savol |
| `true_false` | auto | Ha/Yo'q savol |
| `matching` | auto | Juftlash |
| `fill_blank` | auto | Bo'sh joy to'ldirish |
| `ordering` | auto | Tartibga keltirish |
| `short_answer` | ai | Qisqa javob (AI tekshiradi) |
| `essay` | ai | Insho (AI tekshiradi) |
| `swot` | ai | SWOT tahlil (AI tekshiradi) |
| `discussion` | none | Munozara (baholanmaydi) |
| `file_upload` | teacher | Fayl yuklash (teacher tekshiradi) |
| `goal_setting` | teacher | Maqsad qo'yish (teacher tekshiradi) |
| `peer_assessment` | peer | Tengdoshlar baholaydi |
| `self_evaluation` | self | O'z-o'zini baholash |
| `video_watch` | none | Video ko'rish |
| `reading` | none | Matn o'qish |

#### `Assignment`
```
id                UUID (PK)
lesson            FK → Lesson (CASCADE)
assignment_type   FK → AssignmentType (PROTECT)
title             CharField(255)
description       TextField (nullable)
total_points      Integer (qo'lda kiritiladi)
time_limit        Integer — daqiqalarda (nullable)
attempts_allowed  Integer (default: 1)
order_index       Integer
is_published      Boolean
created_at / updated_at
```

#### `AssignmentPart` ← yangi (2026-03-09)
```
id               UUID (PK)
assignment       FK → Assignment (CASCADE)
title            CharField(200)
instructions     TextField (nullable)
order_index      Integer
assignment_type  FK → AssignmentType (PROTECT, nullable)
                 — null bo'lsa assignment turi ishlatiladi
```

> Assignment ichida bir nechta qism bo'lishi mumkin.
> Masalan: "Part 1: Listening", "Part 2: Reading", "Part 3: Grammar"

#### `Question`
```
id             UUID (PK)
assignment     FK → Assignment (CASCADE)
part           FK → AssignmentPart (CASCADE, nullable)
               — null bo'lsa savol partga biriktirilmagan
question_text  TextField
question_data  JSONField — variantlar, juftliklar va boshqalar
correct_answer JSONField (nullable) — AI/teacher grader uchun null
points         Integer (default: 1)
order_index    Integer
explanation    TextField (nullable) — to'g'ri javob izohi
```

**`question_data` misollari (grader_type ga qarab):**

```json
// multiple_choice
{ "options": ["A", "B", "C", "D"] }

// matching
{ "pairs": [{"left": "Cat", "right": "Mushuk"}] }

// fill_blank
{ "template": "Men ___ o'qitaman." }

// video_watch
{ "video_url": "https://youtube.com/...", "duration_minutes": 10 }

// reading
{ "content": "<p>Matn...</p>", "word_count": 350 }

// essay
{
  "min_words": 100,
  "max_words": 500,
  "rubric": [
    {"criterion": "Kontent", "max_points": 10},
    {"criterion": "Grammatika", "max_points": 5}
  ]
}

// self_evaluation
{
  "scale": "likert",
  "options": [
    {"value": 1, "label": "Hech qachon"},
    {"value": 4, "label": "Har doim"}
  ]
}
```

---

### 4.4 progress app

#### `StudentModuleEnrollment`
```
id               UUID (PK)
student          FK → Student
module           FK → Module
enrolled_at      DateTime
completed_at     DateTime (nullable)
progress_percent Integer
```

#### `StudentLessonProgress`
```
id                  UUID (PK)
student             FK → Student
lesson              FK → Lesson
is_unlocked         Boolean
started_at          DateTime (nullable)
completed_at        DateTime (nullable)
completion_percent  Integer
```

#### `AssignmentAttempt`
```
id              UUID (PK)
student         FK → Student
assignment      FK → Assignment
attempt_number  Integer
started_at      DateTime
submitted_at    DateTime (nullable)
score           Integer (nullable)
max_score       Integer
percentage      Decimal(5,2) (nullable)
is_passed       Boolean (nullable)
```

#### `QuestionAnswer`
```
id              UUID (PK)
attempt         FK → AssignmentAttempt
question        FK → Question
answer_data     JSONField — talaba javobi
is_correct      Boolean (nullable)
points_earned   Integer
score_breakdown JSONField (nullable) — {"content": 8, "grammar": 5}
feedback        TextField (nullable) — AI izohi
answered_at     DateTime
```

---

## 5. API Endpointlar

**Base URL:** `http://localhost:8000/api/` (development)

**Autentifikatsiya:** `Authorization: Token <api_token>` headeri barcha requestlarda kerak.

### accounts

| Method | URL | Tavsif |
|---|---|---|
| POST | `/api/login/` | Teacher login → `{token, teacher}` |
| GET | `/api/me/` | Joriy teacher ma'lumoti |
| PUT | `/api/me/` | Teacher profilini yangilash |
| GET | `/api/students/` | Teacherning talabalari |
| POST | `/api/students/` | Yangi talaba qo'shish |
| GET/PUT/DELETE | `/api/students/{id}/` | Talaba CRUD |

### courses

| Method | URL | Tavsif |
|---|---|---|
| GET | `/api/modules/` | Modullar ro'yxati |
| POST | `/api/modules/` | Yangi modul |
| GET/PUT/DELETE | `/api/modules/{id}/` | Modul CRUD |
| GET | `/api/lessons/?module_id=&root=true` | Root darslar |
| GET | `/api/lessons/?parent_id=` | Child darslar (bosqichlar) |
| POST | `/api/lessons/` | Yangi dars |
| GET/PUT/DELETE | `/api/lessons/{id}/` | Dars CRUD |

### assignments

| Method | URL | Tavsif |
|---|---|---|
| GET | `/api/assignment-types/` | Barcha turlar (o'zniki + global) |
| POST | `/api/assignment-types/` | Yangi teacher-specific tur |
| GET | `/api/assignments/?lesson_id=` | Dars topshiriqlari |
| POST | `/api/assignments/` | Yangi topshiriq |
| GET | `/api/assignments/{id}/` | Topshiriq + parts + questions |
| PUT/DELETE | `/api/assignments/{id}/` | Topshiriq CRUD |
| GET | `/api/assignment-parts/?assignment_id=` | Part ro'yxati |
| POST | `/api/assignment-parts/` | Yangi part |
| GET/PUT/DELETE | `/api/assignment-parts/{id}/` | Part CRUD |
| GET | `/api/questions/?assignment_id=` | Savollar |
| POST | `/api/questions/` | Yangi savol |
| PUT/DELETE | `/api/questions/{id}/` | Savol CRUD |
| POST | `/api/questions/import-docx/` | .docx dan savollar import |

### progress

| Method | URL | Tavsif |
|---|---|---|
| GET | `/api/enrollments/` | Talabalar ro'yxati/modullarda |
| POST | `/api/attempts/` | Yangi urinish boshlash |
| GET/PUT | `/api/attempts/{id}/` | Urinish CRUD |
| POST | `/api/answers/` | Savol javobi yuborish |
| GET/PATCH | `/api/answers/{id}/` | Javob CRUD (ball qo'yish) |

---

## 6. Autentifikatsiya arxitekturasi

### Teacher token auth

```
Frontend → Authorization: Token abc123...
Backend  → TeacherTokenAuthentication.authenticate()
         → Teacher.objects.get(api_token="abc123...")
         → request.teacher = teacher_instance
```

- Django `User` modeli ishlatilmaydi
- `Teacher.api_token` — 64 belgili random hex
- Barcha view larda `request.teacher` orqali kimligini bilamiz

### Scope qoidalari (data isolation)

- Teacher faqat o'z `Module`, `Lesson`, `Assignment` larini ko'radi
- Teacher faqat o'z `Student` larini ko'radi
- `AssignmentType`: o'ziga tegishli (`teacher=self`) + global (`teacher=null`) lar

---

## 7. Frontendlar

### NilufarModul (`d:\Proekt\Angular\TeacherModuls\NilufarModul\app\`)

Angular 19, standalone components, Signals.

**LocalStorage:**
- `teacher_token` — plain string (API token)
- `teacher_profile` — JSON (teacher ma'lumotlari)

**Sahifalar:**

| Route | Component | Tavsif |
|---|---|---|
| `/` | LandingPageComponent | Bosh sahifa |
| `/teacher` | TeacherLoginComponent | Login |
| `/teacher/dashboard` | ModulesListComponent | Modullar ro'yxati |
| `/teacher/modules/:id/lessons` | LessonsPageComponent | Darslar (drag-drop) |
| `/teacher/lessons/:id` | LessonDetailComponent | Dars + topshiriqlar |
| `/teacher/assignments/:id` | AssignmentBuilderComponent | Savol yaratish |
| `/teacher/students` | StudentsPageComponent | Talabalar |
| `/teacher/settings` | TeacherSettingsComponent | Sozlamalar |
| `/student/login` | StudentLoginComponent | Talaba login |
| `/student/dashboard` | StudentDashboardComponent | Talaba paneli |

**Servislar:**
- `AssignmentService` — assignment CRUD + `getDetail()` (parts embedded)
- `AssignmentPartService` — part CRUD
- `QuestionService` — savol CRUD
- `LessonService` — dars CRUD + tree filters
- `ModuleService` — modul CRUD
- `AuthService` — teacher auth (signals)
- `StudentAuthService` — talaba auth

**`AssignmentBuilderComponent` — Part tizimi:**

```
Assignment sahifasi
  ├── [Part 1: Listening]  ← AssignmentPart
  │     ├── Q1, Q2, Q3
  │     └── [+ Bu partga savol qo'shish]
  ├── [Part 2: Reading]
  │     └── Q4, Q5
  ├── [+ Part qo'shish]
  └── [Partga biriktirilmagan savollar]
        └── Q6, Q7
```

### AzizaModul
**LocalStorage:** `teacher` JSON → `teacher.api_token`

### LatifModulFront
**LocalStorage:** `teacher` JSON → `teacher.api_token`

### InformatikaMock
**LocalStorage:** `im_student` JSON → `im_student.api_token`

---

## 8. Grader type tizimi

| grader_type | Kim tekshiradi | Frontend | Backend | Status |
|---|---|---|---|---|
| `auto` | Tizim | Darhol natija | `check_answer()` logikasi | ⚠️ Hali yozilmagan |
| `ai` | Angular (Claude API) | AI chaqiruv + natija yuborish | Faqat saqlash | ⚠️ Hali yozilmagan |
| `teacher` | O'qituvchi | Grading UI | `PATCH points_earned` | ⚠️ UI hali yo'q |
| `peer` | Boshqa talaba | Peer review UI | PeerReview modeli | ⚠️ Model yo'q |
| `self` | Talabaning o'zi | Likert/checkbox | points = self-value | ⚠️ Hali yozilmagan |
| `none` | Hech kim | "Bajarildim" tugma | progress yozish | ⚠️ Hali yozilmagan |

---

## 9. Migratsiyalar tarixi

```
accounts/
  0001_initial              — Teacher, Student

courses/
  0001_initial              — Module, Lesson, ContentType, ModuleContent, LessonContent
  0002_lesson_parent_...    — Lesson.parent (self FK), Lesson.module nullable

assignments/
  0001_initial              — AssignmentType (is_auto_graded), Assignment, Question
  0002_remove_..._grader... — is_auto_graded → grader_type
  0003_add_assignment_types — 15 ta standart AssignmentType recordlari (data migration)
  0004_add_teacher_to_...   — AssignmentType.teacher FK (nullable)
  0005_add_assignment_part  — AssignmentPart modeli, Question.part FK

progress/
  0001_initial              — StudentModuleEnrollment, StudentLessonProgress,
                              AssignmentAttempt, QuestionAnswer
  0002_questionanswer_...   — QuestionAnswer.score_breakdown JSONField
```

---

## 10. Muhim arxitektura qarorlari

### Tree Lesson (daraxt darslari)
- `Lesson.parent` — self FK, null=True
- Root lesson: `parent=null, module=modul`
- Child (stage): `parent=lesson, module=null`
- Oddiy teacher: `Lesson → Assignment`
- Linguaskill: `Lesson (mavzu) → Lesson (bosqich) → Assignment`

**Qachon `module` null bo'ladi?**
Child lessonlarda modul bevosita biriktirilmaydi — u `parent.module` orqali topiladi.

### AssignmentPart — ixtiyoriy qismlar
- Part qo'shmasa ham ishlaydi (partlarsiz assignment)
- Har partning o'z `assignment_type` si bo'lishi mumkin (yoki assignment turidan foydalaniladi)
- `Question.part = null` → partga biriktirilmagan

### AI grading — frontend javobgarligi
- Backend AI chaqirmaydi, faqat natijani saqlaydi
- Angular frontend Claude API ni to'g'ridan-to'g'ri chaqiradi
- Natija backend ga `score_breakdown` + `feedback` sifatida yuboriladi

### Teacher data isolation
- Har bir teacher faqat o'z ma'lumotlarini ko'radi (view larning `get_queryset()` metodida)
- `AssignmentType`: global (teacher=null) va teacher-specific (teacher=self) lar birlashtiriladi

---

## 11. Kelajakdagi vazifalar (TODO)

### Backend
- [ ] `auto` grader: `check_answer()` logikasi (progress app)
- [ ] `teacher` grader: grading endpoint (`PATCH /api/answers/{id}/`)
- [ ] `peer` grader: `PeerReview` modeli va endpointlari
- [ ] `StudentLessonProgress.completion_percent` avtomatik hisoblash
- [ ] `AssignmentAttempt.score` avtomatik hisoblash
- [ ] Talaba uchun dars qulflash/ochish logikasi
- [ ] File upload endpoint (fayl saqlash uchun)

### Frontend (NilufarModul)
- [ ] `ai` grader: Claude API integratsiyasi (essay, short_answer)
- [ ] `self` grader: Likert shkala UI
- [ ] `none` grader: "Bajarildim" tugmasi va progress yozish
- [ ] Teacher grading paneli (teacher grader uchun)
- [ ] Talaba dashboardi — darslar va progressni ko'rish
- [ ] Assignment attempt oqimi (boshlash → javob berish → yuborish)

### Infratuzilma
- [ ] Production PostgreSQL konfiguratsiyasi
- [ ] Media fayllar uchun storage (S3 yoki lokal)
- [ ] Har bir teacher fronti uchun deploy pipeline

---

## 12. Muhitni sozlash (Development)

```bash
# 1. Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Dependencylar
pip install -r requirements.txt

# 3. SQLite bilan ishlatish (PostgreSQL o'rniga)
# settings.py da DATABASE_URL muhit o'zgaruvchisi bo'lmasa SQLite ishlatiladi

# 4. Migratsiyalar
python manage.py migrate

# 5. Superuser
python manage.py createsuperuser

# 6. Server
python manage.py runserver
```

```bash
# Angular (NilufarModul)
cd d:\Proekt\Angular\TeacherModuls\NilufarModul\app
npm install
ng serve
```

---

## 13. O'zgarishlar jurnali

| Sana | O'zgarish |
|---|---|
| 2026-02-01 | Dastlabki loyiha — Teacher, Student, Module, Lesson, Assignment, Question |
| 2026-02-xx | Progress app — StudentModuleEnrollment, AssignmentAttempt, QuestionAnswer |
| 2026-03-xx | `is_auto_graded` → `grader_type` (6 tur); 15 ta standart AssignmentType |
| 2026-03-xx | `QuestionAnswer.score_breakdown` — AI rubric baholash uchun |
| 2026-03-xx | `Lesson.parent` — daraxt tuzilmasi (Linguaskill uchun) |
| 2026-03-xx | `Lesson.module` nullable — child lessonlar uchun |
| 2026-03-xx | Angular interceptorlar tuzatildi (4 ta frontend) |
| 2026-03-xx | `AssignmentType.teacher` FK — teacher-specific turlar |
| 2026-03-09 | `AssignmentPart` modeli — assignment ichida qismlar |
| 2026-03-09 | `Question.part` FK — savol qaysi partga tegishli |
| 2026-03-09 | `AssignmentBuilderComponent` — part UI (Angular, NilufarModul) |
