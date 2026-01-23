# 📦 Odoo Training Repository

Repositori ini berisi latihan, eksperimen, dan contoh modul Odoo untuk membantu proses belajar dan pengembangan. Cocok digunakan sebagai referensi pribadi maupun bahan pembelajaran tim.

---

## 🚀 Tujuan
- Memahami dasar-dasar pengembangan modul Odoo.
- Melatih penggunaan ORM (Object Relational Mapping).
- Membiasakan diri dengan struktur direktori dan workflow Odoo.
- Menyediakan dokumentasi dan contoh kode yang mudah dipahami.

---

## 📂 Struktur Direktori
odoo-learning-repository/
├── addons/
│   ├── basic_module/
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── basic_model.py
│   │   ├── views/
│   │   │   └── basic_view.xml
│   │   ├── security/
│   │   │   └── ir.model.access.csv
│   │   └── data/
│   │       └── sample_data.xml
│   │
│   ├── intermediate_module/
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── models/
│   │   ├── views/
│   │   ├── wizard/
│   │   ├── reports/
│   │   └── security/
│   │
│   └── advanced_module/
│       ├── __init__.py
│       ├── __manifest__.py
│       ├── models/
│       ├── controllers/
│       ├── views/
│       ├── reports/
│       ├── security/
│       └── tests/
│
├── docs/
│   ├── installation.md
│   ├── odoo_module_structure.md
│   ├── orm_basics.md
│   └── best_practices.md
│
├── scripts/
│   ├── setup_odoo.sh
│   └── reset_database.sh
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .gitignore
├── README.md
└── requirements.txt
