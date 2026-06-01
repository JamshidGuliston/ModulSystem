# Modul turi (ModuleType) + Module teachers M2M — Dizayn

**Sana:** 2026-06-01
**Status:** Tasdiqlash kutilmoqda

## Maqsad

Har bir teacher o'ziga tegishli "modul turlari"ni (ModuleType) yaratishi va modul yaratayotganda
shu turlardan birini biriktirishi mumkin bo'lsin. Shuningdek, bitta modul bir nechta teacherga
tegishli bo'la olishi uchun `Module` ga teachers many-to-many qo'shiladi.

## Qarorlar (brainstorm natijasi)

| Savol | Qaror |
|-------|-------|
| M2M aloqasi | Teacher ↔ Module (literal): `Module` ga `teachers` M2M qo'shiladi |
| Bitta modul nechta turga ega? | Bitta tur (`module_type` ForeignKey) |
| `module_type` majburiymi? | Ixtiyoriy (`null=True, blank=True`) |
| ModuleType API | Ha — to'liq CRUD viewset |
| M2M migratsiya strategiyasi | Faqat M2M qo'shish; mavjud `teacher` FK saqlanadi |
| Scoping (M2M qo'shilgach) | Faqat egasi (`teacher` FK bo'yicha, eski mantiq o'zgarmaydi) |
| `module_type` validatsiyasi | Ha — teacher faqat O'ZI yaratgan turini biriktira oladi |
| Data migratsiya (teacher → teachers) | Yo'q — `teachers` M2M bo'sh qoladi, qo'lda to'ldiriladi |

## Arxitektura

`ModuleType` modeli `accounts.Level` patterniga aynan ergashadi (teacher-scoped resurs):
teacherga `ForeignKey`, `unique_together=(teacher, name)`, `order_index` bilan tartiblanadi,
o'z CRUD viewseti `request.teacher` bo'yicha scope qilinadi.

`teacher` FK = modul **egasi** (yaratuvchi, scoping shu bo'yicha ishlaydi).
`teachers` M2M = modul ulashilgan qo'shimcha teacherlar (hozircha faqat ma'lumot, ko'rinishga
ta'sir qilmaydi).

## Komponentlar

### 1. `ModuleType` modeli — `courses/models.py`

```python
class ModuleType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        'accounts.Teacher', on_delete=models.CASCADE, related_name='module_types',
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'module_type'
        ordering = ['order_index']
        unique_together = [('teacher', 'name')]

    def __str__(self):
        return self.name
```

### 2. `Module` modeliga o'zgartirishlar — `courses/models.py`

- `teacher` FK **saqlanadi** (egasi, scoping).
- Yangi maydonlar:

```python
    module_type = models.ForeignKey(
        'ModuleType', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='modules',
    )
    teachers = models.ManyToManyField(
        'accounts.Teacher', related_name='shared_modules', blank=True,
    )
```

`SET_NULL` — tur o'chirilsa modul o'chmaydi. `related_name='shared_modules'` — `Teacher.modules`
(mavjud FK reverse) bilan to'qnashmaslik uchun.

### 3. Serializerlar — `courses/serializers.py`

**`ModuleTypeSerializer`** (`LevelSerializer` patterni):
- `fields = ['id', 'teacher', 'name', 'description', 'order_index', 'created_at']`
- `read_only_fields = ['id', 'teacher', 'created_at']`
- `get_validators()` da `UniqueTogetherValidator` olib tashlanadi.
- `validate()` da teacher ichida `name` takrorlanmasligini tekshirish (`LevelSerializer` kabi).

**`ModuleSerializer` va `ModuleDetailSerializer`** ga qo'shiladi:
- `module_type` (yoziladigan FK) — fields ro'yxatiga.
- `module_type_name = serializers.CharField(source='module_type.name', read_only=True)`.
- `teachers` (M2M, PK ro'yxati) — fields ro'yxatiga.
- `validate()`: agar `module_type` berilsa va `request.teacher` mavjud bo'lsa,
  `module_type.teacher_id == request.teacher.id` ekanini tekshirish; aks holda
  `ValidationError({'module_type': "Bu modul turi sizga tegishli emas."})`.

### 4. ViewSetlar — `courses/views.py`

**`ModuleTypeViewSet`** (`LevelViewSet` patterni):
```python
class ModuleTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleTypeSerializer
    pagination_class = None

    def get_queryset(self):
        if hasattr(self.request, 'teacher') and self.request.teacher:
            return ModuleType.objects.filter(teacher=self.request.teacher)
        return ModuleType.objects.none()

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.teacher)
```

`ModuleViewSet` scoping **o'zgarmaydi** (`filter(teacher=self.request.teacher)`).

### 5. URL — `courses/urls.py`

```python
router.register(r'module-types', ModuleTypeViewSet)
```
Natija: `/api/module-types/` CRUD endpointlari.

### 6. Admin — `courses/admin.py`

- `@admin.register(ModuleType)` → `ModuleTypeAdmin` (list_display: name, teacher, order_index).
- `ModuleAdmin`: `module_type` ni fieldlarga, `filter_horizontal = ['teachers']` qo'shish,
  `list_filter` ga `module_type` qo'shish.

### 7. Migratsiya — `courses/migrations/0005_*.py`

`python manage.py makemigrations courses` orqali avtomatik yaratiladi:
- `ModuleType` modelini yaratish.
- `Module.module_type` (nullable FK) qo'shish.
- `Module.teachers` (M2M) qo'shish.

**Data migratsiya yo'q** — `teachers` M2M bo'sh qoladi.

## Ma'lumot oqimi

1. Teacher `POST /api/module-types/` → o'z turini yaratadi (`teacher` avtomatik tokendan).
2. Teacher `POST /api/modules/` (yoki `PATCH`) → `module_type` sifatida o'z turining id sini
   yuboradi. Serializer turning egasi == request.teacher ekanini tekshiradi.
3. `teachers` M2M qiymatlari modul `POST/PATCH` da PK ro'yxati sifatida yuboriladi (ixtiyoriy).
4. `GET /api/modules/` — teacher faqat o'zi egasi bo'lgan (`teacher` FK) modullarni ko'radi;
   javobda `module_type`, `module_type_name`, `teachers` ham qaytadi.

## Xatoliklarni boshqarish

- Tur nomi takrorlansa: `400 {'name': 'Bu modul turi nomi allaqachon mavjud.'}`.
- Begona teacher turini biriktirsa: `400 {'module_type': "Bu modul turi sizga tegishli emas."}`.
- Token bo'lmasa: mavjud `IsTeacher` permission/authentication mantig'i ishlaydi (o'zgarmaydi).

## Test rejasi — `courses/tests.py`

`APIClient` + `HTTP_AUTHORIZATION=f'Token {teacher.api_token}'` patterni bilan:

1. **ModuleType CRUD scoped:** teacher o'z turini yaratadi (201), ro'yxatda faqat o'ziniki
   ko'rinadi; boshqa teacher turi ko'rinmaydi.
2. **Unique nom:** bir teacher ichida bir xil nomli ikkinchi tur → 400.
3. **module_type biriktirish (ijobiy):** teacher o'z turini modulga biriktiradi → 200/201,
   `module_type` saqlanadi.
4. **module_type biriktirish (begona, salbiy):** boshqa teacher turini biriktirsa → 400.
5. **teachers M2M:** modulga `teachers` ro'yxatini yuborib, javobda qaytishini tekshirish.
6. **module_type ixtiyoriy:** turi bermay modul yaratish ishlaydi (`module_type=None`).

## YAGNI / qamrov chegaralari

- `teachers` M2M scopingga ta'sir qilmaydi (kelajakda kerak bo'lsa qo'shiladi).
- `teacher` FK ni M2M ga to'liq ko'chirish / olib tashlash bu ishda yo'q.
- ModuleType uchun qo'shimcha ranglar/ikonkalar kabi maydonlar yo'q (kerak bo'lsa keyin).
