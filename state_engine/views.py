from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Organization, Role, InviteCode, CustomUser, Workflow, State, Transition, Entity, ActionLog, ContactMessage

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

def logout_view(request):
    logout(request)
    return redirect('login')

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

@login_required
def dashboard(request):
    if request.user.is_staff:
        all_entities = Entity.objects.filter(workflow__organization=request.user.organization).order_by('-updated_at')
        return render(request, 'dashboard.html', {
            'is_manager': True,
            'all_entities': all_entities
        })
    else:
        my_requests = Entity.objects.filter(creator=request.user).order_by('-updated_at')
        
        my_tasks = Entity.objects.filter(assigned_user=request.user).order_by('-updated_at')
        
        department_pool = Entity.objects.filter(
            workflow__organization=request.user.organization,
            current_state__outgoing_transitions__allowed_roles=request.user.role,
            assigned_user__isnull=True
        ).distinct().order_by('-updated_at')

        return render(request, 'dashboard.html', {
            'is_manager': False,
            'my_requests': my_requests,
            'my_tasks': my_tasks,
            'department_pool': department_pool
        })

@login_required
def workflow_list(request):
    workflows = Workflow.objects.filter(organization=request.user.organization, is_active=True)
    return render(request, 'workflow_list.html', {'workflows': workflows})

@login_required
def workflow_detail(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk, organization=request.user.organization)
    states = workflow.state_set.all()
    return render(request, 'workflow_detail.html', {'workflow': workflow, 'states': states})

@login_required
def entity_detail(request, pk):
    entity = get_object_or_404(Entity, pk=pk, workflow__organization=request.user.organization)
    logs = entity.actionlog_set.all().order_by('-timestamp')
    
    all_possible_transitions = Transition.objects.filter(
        workflow=entity.workflow, 
        from_state=entity.current_state
    ).distinct()

    if request.user.is_staff:
        available_transitions = all_possible_transitions
    else:
        available_transitions = all_possible_transitions.filter(
            allowed_roles=request.user.role
        )

    org_users = CustomUser.objects.filter(organization=request.user.organization)

    context = {
        'entity': entity,
        'logs': logs,
        'transitions': available_transitions,
        'all_possible_transitions': all_possible_transitions,
        'org_users': org_users
    }
    return render(request, 'entity_detail.html', context)

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

@login_required
def entity_create(request):
    if request.method == 'POST':
        workflow_id = request.POST.get('workflow_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        workflow = get_object_or_404(Workflow, pk=workflow_id, organization=request.user.organization)
        
        if not workflow.is_executable:
            messages.error(request, "Bu iş akışında yapısal hatalar bulunduğu için talep açılamaz.")
            return redirect('entity_create')
            
        initial_state = workflow.get_initial_state()
        
        if initial_state:
            Entity.objects.create(
                workflow=workflow,
                current_state=initial_state,
                creator=request.user,
                title=title,
                content=content
            )
            messages.success(request, "Talep başarıyla oluşturuldu.")
        else:
            messages.error(request, "Bu akışın bir başlangıç durumu yok!")
            
        return redirect('dashboard')
        
    if request.user.is_staff:
        active_workflows = Workflow.objects.filter(organization=request.user.organization, is_active=True)
    else:
        active_workflows = Workflow.objects.filter(organization=request.user.organization, allowed_roles=request.user.role, is_active=True)
        
    executable_workflows = [wf for wf in active_workflows if wf.is_executable]
        
    return render(request, 'entity_form.html', {'workflows': executable_workflows})

@login_required
def execute_transition(request, entity_id, transition_id):
    if request.method == 'POST':
        entity = get_object_or_404(Entity, pk=entity_id, workflow__organization=request.user.organization)
        transition = get_object_or_404(Transition, pk=transition_id)
        
        if request.user.is_staff or request.user.role in transition.allowed_roles.all():
            if entity.current_state == transition.from_state:
                entity.current_state = transition.to_state
                entity.save()
                
                ActionLog.objects.create(
                    entity=entity,
                    user=request.user,
                    transition=transition
                )
            
    return redirect('entity_detail', pk=entity_id)

@login_required
def entity_delete(request, pk):
    entity = get_object_or_404(Entity, pk=pk, workflow__organization=request.user.organization)
    
    can_delete = False
    if request.user.is_staff:
        can_delete = True
    elif request.user == entity.creator and entity.current_state.is_initial:
        can_delete = True
        
    if can_delete:
        entity.delete()
        
    return redirect('dashboard')

@login_required
def assign_entity(request, pk):
    if request.method == 'POST':
        entity = get_object_or_404(Entity, pk=pk, workflow__organization=request.user.organization)

        user_id = request.POST.get('assigned_user_id')
        
        if user_id:
            assigned_user = get_object_or_404(CustomUser, id=user_id, organization=request.user.organization)
            entity.assigned_user = assigned_user
        else:
            entity.assigned_user = None 
            
        entity.save()
        
    return redirect('entity_detail', pk=pk)

def index_view(request):
    return render(request, 'index.html')

def privacy_view(request):
    return render(request, 'privacy.html')

def terms_view(request):
    return render(request, 'terms.html')

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
            is_final = request.POST.get('is_final') == 'on' 
            
            color_class = request.POST.get('color_class')
            
            if workflow_id and state_name:
                workflow = Workflow.objects.get(id=workflow_id, organization=org)
                
                State.objects.create(
                    workflow=workflow, 
                    name=state_name,
                    is_final=is_final,
                    color_class=color_class
                )

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
        
        elif action == "delete_workflow":
            workflow_id = request.POST.get("workflow_id")

            workflow = Workflow.objects.get(
                id=workflow_id,
                organization=request.user.organization
            )

            has_entities = Entity.objects.filter(workflow=workflow).exists()

            if has_entities:
                messages.error(
                    request,
                    "Bu iş akışı silinemez çünkü ona bağlı talepler bulunmaktadır."
                )
            else:
                workflow.delete()
                messages.success(request, "İş akışı başarıyla silindi.")

            return redirect("manager_dashboard")
            
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
                
        elif action == 'create_transition':
            workflow_id = request.POST.get('workflow_id')
            transition_name = request.POST.get('transition_name')
            from_state_id = request.POST.get('from_state_id')
            to_state_id = request.POST.get('to_state_id')
            role_ids = request.POST.getlist('transition_roles')
            
            if workflow_id and transition_name and from_state_id and to_state_id:
                workflow = Workflow.objects.filter(id=workflow_id, organization=org).first()
                if workflow:
                    from_state = State.objects.filter(id=from_state_id, workflow=workflow).first()
                    to_state = State.objects.filter(id=to_state_id, workflow=workflow).first()
                    if from_state and to_state:
                        transition = Transition.objects.create(
                            workflow=workflow,
                            name=transition_name,
                            from_state=from_state,
                            to_state=to_state
                        )
                        if role_ids:
                            transition.allowed_roles.set(role_ids)

        elif action == 'delete_transition':
            transition_id = request.POST.get('transition_id')
            if transition_id:
                Transition.objects.filter(id=transition_id, workflow__organization=org).delete()
                
        elif action == 'assign_entity':
            entity_id = request.POST.get('entity_id')
            user_id = request.POST.get('assigned_user_id')
            if entity_id:
                entity = Entity.objects.filter(id=entity_id, workflow__organization=org).first()
                if entity:
                    if user_id:
                        assigned_user = CustomUser.objects.filter(id=user_id, organization=org).first()
                        entity.assigned_user = assigned_user
                    else:
                        entity.assigned_user = None
                    entity.save()

    workflows = Workflow.objects.filter(organization=org, is_active=True)
    roles = Role.objects.filter(organization=org)
    invite_codes = InviteCode.objects.filter(role__organization=org).order_by('-created_at')
    
    entities = Entity.objects.filter(workflow__organization=org).order_by('-created_at')
    org_users = CustomUser.objects.filter(organization=org)
    
    context = {
        'workflows': workflows,
        'roles': roles,
        'invite_codes': invite_codes,
        'entities': entities,      
        'org_users': org_users     
    }
    return render(request, 'manager_dashboard.html', context)