# FlowCore

Bu proje, kurum içi iş akışlarını dinamik olarak yöneten merkezi bir State Machine (Durum Makinesi) motorudur.

## Ekip İçin Kurulum Rehberi

### İlk Kurulum (Bir Kez Yapılacak)

1. Projeyi İndirin:
- `git clone https://github.com/olmezarda/flowcore`
- `cd flowcore`

2. Sanal Ortam Oluşturun ve Aktif Edin:
- `python -m venv venv`
- `venv\Scripts\activate` (Windows)
- `source venv/bin/activate` (Mac/Linux)

3. Kütüphaneleri Kurun:
- `pip install -r requirements.txt`

4. Veritabanını Hazırlayın:
- `python manage.py migrate`

5. Admin Paneli İçin Kullanıcı Oluşturun:
- (Bu adım admin paneline girebilmeniz için şarttır)
- `python manage.py createsuperuser`

## Günlük Çalışma Döngüsü

Kod yazmaya başlamadan önce daima güncel hali çekin:
- `git pull`

Değişikliklerinizi iletmek için şu komutları sırasıyla uygulayın:
- `git add .`
- `git commit -m "Yapılan değişikliğin kısa özeti"`
- `git push`

## Eksik Listesi ve Geliştirilecek Özellikler

Projenin tam kapasiteyle çalışması için geliştirilmesi gereken kritik özellikler şunlardır:

1. Sorumlu ve Atama Sistemi
- Şu anki yapıda talepler (Entity) için bir sorumlu alanı bulunmamaktadır. Taleplerin her aşamasında, o aşamadan sorumlu olan görevlinin (User/Role) kim olduğu tabloda tutulmalı ve ilgili kişinin panelinde listelenmelidir.

2. Çok Aşamalı ve Role Bağlı Onay Mekanizması
- Bir sürecin farklı aşamaları, farklı yetkili roller tarafından onaylanabilmelidir. Örneğin, bir staj başvurusunda ilk aşamada İK onayı gerekirken, son aşamada yönetici onayı şart koşulabilmelidir. Durumlar (State) bazında yetki kontrolü geliştirilmelidir.

3. Dinamik Dallanma
- Mevcut yapıda onay ve red seçenekleri doğrusal bir akış gibi görünmektedir. Bir durumun (State) birden fazla yola ayrılabilmesi sağlanmalıdır. Bir aşamadan sonra çıkacak farklı seçenekler (Onay/Red/Revize vb.) talebi tamamen farklı durumlara yönlendirebilmelidir.

4. Gelişmiş Geçiş Mantığı
- Süreçler sadece ileri gitmekle sınırlı kalmamalıdır. Gerektiğinde birkaç adım ileriye atlama veya sürecin başına dönme opsiyonları yönetici paneli üzerinden esnekçe tanımlanabilmelidir.

5. Yönetici Paneli Geliştirmeleri
- Süreç tasarlayan yöneticinin, tüm bu dallanmaları, sorumlu atamalarını ve karmaşık yol haritalarını kod yazmaya gerek duymadan arayüz üzerinden kolayca ayarlayabileceği bir yapı kurulmalıdır.