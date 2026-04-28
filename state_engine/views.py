from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Organization, Role, InviteCode, CustomUser, Workflow, State, Transition, Entity, ActionLog, ContactMessage

# A. KULLANICI İŞLEMLERİ (AUTH VIEWS)

# 1. Kullanıcı Giriş API/View'ı
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    error_message = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        else:
            error_message = "Kullanıcı adı veya şifre hatalı. Lütfen tekrar deneyin."

    return render(request, 'login.html', {'error': error_message})

# 2. Kullanıcı Çıkış API/View'ı
def logout_view(request):
    logout(request)
    return redirect('login')

# 3. Yeni Kullanıcı Kayıt API/View'ı
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_message = None
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if CustomUser.objects.filter(username=username).exists():
            error_message = "Bu kullanıcı adı zaten sistemde kayıtlı."
        else:
            if user_type == 'kurumsal_admin':
                company_name = request.POST.get('company_name')
                if not company_name:
                    error_message = "Lütfen kurum adını girin."
                else:
                    org = Organization.objects.create(name=company_name)
                    user = CustomUser.objects.create_user(
                        username=username,
                        password=password,
                        user_type='kurumsal_admin',
                        organization=org,
                        is_staff=True
                    )
                    login(request, user)
                    return redirect('manager_dashboard')

            elif user_type == 'kurum_uyesi':
                invite_code_str = request.POST.get('invite_code')
                try:
                    invite = InviteCode.objects.get(code=invite_code_str, is_used=False)
                    user = CustomUser.objects.create_user(
                        username=username,
                        password=password,
                        user_type='kurum_uyesi',
                        organization=invite.role.organization,
                        role=invite.role
                    )
                    invite.is_used = True
                    invite.save()
                    login(request, user)
                    return redirect('dashboard')
                except InviteCode.DoesNotExist:
                    error_message = "Geçersiz veya daha önce kullanılmış bir davet kodu girdiniz."

    return render(request, 'register.html', {'error': error_message})

# B. ANA PANO VE LİSTELEMELER (READ VIEWS)

# 4. Ana Pano (Dashboard) API/View'ı
@login_required
def dashboard(request):
    if request.user.is_staff:
        entities = Entity.objects.filter(workflow__organization=request.user.organization).order_by('-updated_at')
    else:
        entities = Entity.objects.filter(creator=request.user).order_by('-updated_at')
    return render(request, 'dashboard.html', {'entities': entities})

# 5. İş Akışları Listeleme API/View'ı
@login_required
def workflow_list(request):
    workflows = Workflow.objects.filter(organization=request.user.organization)
    return render(request, 'workflow_list.html', {'workflows': workflows})

# 6. İş Akışı Detay API/View'ı
@login_required
def workflow_detail(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk, organization=request.user.organization)
    states = workflow.state_set.all()
    return render(request, 'workflow_detail.html', {'workflow': workflow, 'states': states})

# 7. Talep/Varlık (Entity) Detay API/View'ı
@login_required
def entity_detail(request, pk):
    entity = get_object_or_404(Entity, pk=pk, workflow__organization=request.user.organization)
    logs = entity.actionlog_set.all().order_by('-timestamp')
    available_transitions = Transition.objects.filter(workflow=entity.workflow, from_state=entity.current_state)

    context = {
        'entity': entity,
        'logs': logs,
        'transitions': available_transitions.distinct()
    }
    return render(request, 'entity_detail.html', context)

# C. YENİ KAYIT OLUŞTURMA (CREATE VIEWS)

# 8. Yeni İş Akışı Oluşturma API/View'ı
@login_required
def workflow_create(request):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        Workflow.objects.create(organization=request.user.organization, name=name, description=description)
        return redirect('workflow_list')
    return render(request, 'workflow_form.html')

# 9. Yeni Talep/Varlık Oluşturma API/View'ı
@login_required
def entity_create(request):
    if request.method == 'POST':
        workflow_id = request.POST.get('workflow_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        workflow = get_object_or_404(Workflow, pk=workflow_id, organization=request.user.organization)
        initial_state = workflow.state_set.filter(is_initial=True).first()
        
        if initial_state:
            Entity.objects.create(
                workflow=workflow,
                current_state=initial_state,
                creator=request.user,
                title=title,
                content=content
            )
        return redirect('dashboard')
        
    if request.user.is_staff:
        workflows = Workflow.objects.filter(organization=request.user.organization)
    else:
        workflows = Workflow.objects.filter(organization=request.user.organization, allowed_roles=request.user.role)
        
    return render(request, 'entity_form.html', {'workflows': workflows})

# D. DURUM MAKİNESİ MOTORU (ACTION VIEWS)

# 10. Durum Değiştirme (Transition) API/View'ı
@login_required
def execute_transition(request, entity_id, transition_id):
    if request.method == 'POST':
        entity = get_object_or_404(Entity, pk=entity_id, workflow__organization=request.user.organization)
        transition = get_object_or_404(Transition, pk=transition_id)
        
        if entity.current_state == transition.from_state:
            entity.current_state = transition.to_state
            entity.save()
            
            ActionLog.objects.create(
                entity=entity,
                user=request.user,
                transition=transition
            )
            
    return redirect('entity_detail', pk=entity_id)

# 11. Talep/Varlık Silme API/View'ı
@login_required
def entity_delete(request, pk):
    entity = get_object_or_404(Entity, pk=pk, workflow__organization=request.user.organization)
    if request.user == entity.creator or request.user.is_staff:
        entity.delete()
    return redirect('dashboard')

# E. STATİK SAYFALAR (LANDING VE BİLGİ)

# 12. Ana Sayfa (Index) API/View'ı
def index_view(request):
    return render(request, 'index.html')

# 13. Gizlilik Politikası API/View'ı
def privacy_view(request):
    return render(request, 'privacy.html')

# 14. Kullanım Şartları API/View'ı
def terms_view(request):
    return render(request, 'terms.html')

# 15. İletişim Formu API/View'ı
def contact_view(request):
    success = False
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
        success = True
    return render(request, 'contact.html', {'success': success})

# F. KURUMSAL YÖNETİCİ PANELİ (MANAGER DASHBOARD)

# 16. Yönetici Paneli API/View'ı
@login_required
def manager_dashboard_view(request):
    if not request.user.is_staff or not request.user.organization:
        return redirect('dashboard')
        
    org = request.user.organization
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_workflow':
            name = request.POST.get('workflow_name')
            role_ids = request.POST.getlist('allowed_roles') 
            if name:
                wf = Workflow.objects.create(organization=org, name=name)
                if role_ids:
                    wf.allowed_roles.set(role_ids) 
                
        elif action == 'create_state':
            workflow_id = request.POST.get('workflow_id')
            state_name = request.POST.get('state_name')
            is_initial = request.POST.get('is_initial') == 'on'
            color_class = request.POST.get('color_class')
            
            if workflow_id and state_name:
                workflow = Workflow.objects.get(id=workflow_id, organization=org)
                State.objects.create(workflow=workflow, name=state_name, is_initial=is_initial, color_class=color_class)

        elif action == 'create_role':
            role_name = request.POST.get('role_name')
            prefix = request.POST.get('prefix')
            if role_name and prefix:
                Role.objects.create(organization=org, name=role_name, prefix=prefix.upper())

        elif action == 'delete_role':
            role_id = request.POST.get('role_id')
            if role_id:
                Role.objects.filter(id=role_id, organization=org).delete()

        elif action == 'create_invite':
            role_id = request.POST.get('role_id')
            quantity = int(request.POST.get('quantity', 1))
            quantity = min(max(quantity, 1), 50) 
            
            if role_id:
                role = Role.objects.get(id=role_id, organization=org)
                for _ in range(quantity):
                    InviteCode.objects.create(role=role)

        elif action == 'delete_invite':
            invite_id = request.POST.get('invite_id')
            if invite_id:
                InviteCode.objects.filter(id=invite_id, role__organization=org, is_used=False).delete()
        
        elif action == 'delete_workflow':
            wf_id = request.POST.get('workflow_id')
            if wf_id:
                Workflow.objects.filter(id=wf_id, organization=org).delete()
                
        elif action == 'edit_workflow':
            wf_id = request.POST.get('workflow_id')
            new_name = request.POST.get('new_name')
            role_ids = request.POST.getlist('allowed_roles')
            
            if wf_id and new_name:
                wf = Workflow.objects.filter(id=wf_id, organization=org).first()
                if wf:
                    wf.name = new_name
                    wf.save()
                    wf.allowed_roles.set(role_ids)
                    
        elif action == 'delete_state':
            state_id = request.POST.get('state_id')
            if state_id:
                State.objects.filter(id=state_id, workflow__organization=org).delete()
        
    workflows = Workflow.objects.filter(organization=org)
    roles = Role.objects.filter(organization=org)
    invite_codes = InviteCode.objects.filter(role__organization=org).order_by('-created_at')
    
    context = {
        'workflows': workflows,
        'roles': roles,
        'invite_codes': invite_codes
    }
    return render(request, 'manager_dashboard.html', context)