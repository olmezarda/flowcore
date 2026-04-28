from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string

# 1. KURUM (ORGANIZATION) MODELİ
class Organization(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kurum Adı")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. ROL MODELİ
class Role(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100, verbose_name="Rol Adı")
    prefix = models.CharField(max_length=10, verbose_name="Kod Ön Eki")

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

# 3. DAVET KODU (INVITE CODE) MODELİ
class InviteCode(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='invite_codes')
    code = models.CharField(max_length=20, unique=True, verbose_name="Davet Kodu")
    is_used = models.BooleanField(default=False, verbose_name="Kullanıldı mı?")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.code = f"{self.role.prefix}-{random_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

# 4. KULLANICI MODELİ
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('bireysel', 'Bireysel Kullanıcı'),
        ('kurumsal_admin', 'Kurumsal Yönetici'),
        ('kurum_uyesi', 'Kurum Personeli / Öğrenci'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='bireysel')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

# 5. İŞ AKIŞI (WORKFLOW) MODELİ
class Workflow(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="İş Akışı Adı")
    description = models.TextField(blank=True, null=True)
    allowed_roles = models.ManyToManyField(Role, blank=True, verbose_name="Yetkili Roller")

    def __str__(self):
        return self.name

# 6. DURUM (STATE) MODELİ
class State(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_initial = models.BooleanField(default=False)
    color_class = models.CharField(max_length=20, default='primary')

    def __str__(self):
        return f"{self.workflow.name} - {self.name}"

# 7. GEÇİŞ (TRANSITION) MODELİ
class Transition(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    from_state = models.ForeignKey(State, related_name='outgoing_transitions', on_delete=models.CASCADE)
    to_state = models.ForeignKey(State, related_name='incoming_transitions', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.from_state.name} -> {self.to_state.name}"

# 8. TALEP (ENTITY) MODELİ
class Entity(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    workflow = models.ForeignKey(Workflow, on_delete=models.PROTECT)
    current_state = models.ForeignKey(State, on_delete=models.PROTECT)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 9. İŞLEM GEÇMİŞİ (ACTION LOG) MODELİ
class ActionLog(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    transition = models.ForeignKey(Transition, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"{self.entity.title} - {self.user.username}"
        return self.entity.title

# 10. İLETİŞİM MESAJLARI MODELİ
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.name}"