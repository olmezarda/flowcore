# FlowCore: Dinamik Süreç ve Durum Makinesi Motoru

FlowCore, kurum içi iş akışlarının (workflow) esnek, rol bazlı ve dinamik olarak yönetilmesini sağlayan merkezi bir Durum Makinesi (State Machine) platformudur.

## Geliştirme Ortamı Kurulum Yönergesi

Projenin yerel ortamda çalıştırılabilmesi ve geliştirme yapılabilmesi için aşağıdaki adımları sırasıyla izleyebilirsiniz:

**1. Projenin Klonlanması:**
```bash
git clone [https://github.com/olmezarda/flowcore](https://github.com/olmezarda/flowcore)
cd flowcore
```

**2. Sanal Ortamın (Virtual Environment) Oluşturulması ve Etkinleştirilmesi:**
```bash
python -m venv venv
```
*Windows için:* `venv\Scripts\activate`
*macOS/Linux için:* `source venv/bin/activate`

**3. Gerekli Bağımlılıkların Kurulması:**
```bash
pip install -r requirements.txt
```

**4. Veritabanı Göçlerinin (Migrations) Uygulanması:**
```bash
python manage.py migrate
```

**5. Yönetici (Superuser) Hesabının Oluşturulması:**
*(Sistem yönetim paneline erişim için gereklidir)*
```bash
python manage.py createsuperuser
```

## İletişim

**E-posta:** olm.zarda@gmail.com
**LinkedIn:** [Arda Ölmez](https://www.linkedin.com/in/olmezarda/)