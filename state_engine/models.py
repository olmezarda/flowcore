from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string

class Organization(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kurum Adı")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100, verbose_name="Rol Adı")
    prefix = models.CharField(max_length=10, verbose_name="Kod Ön Eki")

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

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

class Workflow(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="İş Akışı Adı")
    description = models.TextField(blank=True, null=True)
    allowed_roles = models.ManyToManyField(Role, blank=True, verbose_name="Yetkili Roller")

    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    def __str__(self):
        return self.name
    
    @property
    def compiler_errors(self):
        errors = []
        states = self.state_set.all()
        
        if not states.exists():
            return ["Süreçte henüz hiçbir aşama tanımlanmamış."]
            
        for state in states:
            has_incoming = state.incoming_transitions.exists()
            has_outgoing = state.outgoing_transitions.exists()
            
            if not has_incoming and not has_outgoing:
                errors.append(f"Kopuk Aşama: '{state.name}' aşamasına gelen veya giden hiçbir ok yok.")
            
            if has_incoming and not has_outgoing and not state.is_final:
                errors.append(f"Derleyici Hatası: '{state.name}' ara aşamasına giriş var ama çıkış yok! Süreç burada tıkanır. (Eğer bu bir son aşamaysa 'Bitiş Durumu' olarak işaretleyin).")
                
        return errors
    
    @property
    def has_active_entities(self):
        return self.entity_set.exclude(current_state__is_final=True).exists()
    
    def get_initial_state(self):
        return self.state_set.filter(incoming_transitions__isnull=True).first()
    
    @property
    def is_executable(self):
        return len(self.compiler_errors) == 0

class State(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_final = models.BooleanField(default=False, verbose_name="Bitiş Durumu mu?")
    color_class = models.CharField(max_length=20, default='primary')
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"

class Transition(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    from_state = models.ForeignKey(State, related_name='outgoing_transitions', on_delete=models.CASCADE)
    to_state = models.ForeignKey(State, related_name='incoming_transitions', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    allowed_roles = models.ManyToManyField(Role, blank=True, verbose_name="Yetkili Roller")
    
    def __str__(self):
        return f"{self.from_state.name} -> {self.to_state.name}"

class Entity(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    workflow = models.ForeignKey(Workflow, on_delete=models.PROTECT)
    current_state = models.ForeignKey(State, on_delete=models.PROTECT)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    assigned_user = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_entities',
        verbose_name="Atanan Sorumlu"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        assigned = self.assigned_user.username if self.assigned_user else "Atanmadı"
        return f"{self.title} (Sorumlu: {assigned})"

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

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.name}"