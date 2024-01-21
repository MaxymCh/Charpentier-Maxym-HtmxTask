from django.shortcuts import render
from django.views.generic import TemplateView, FormView, ListView
from django.contrib.auth.views import LoginView
from firsttuto.forms import RegisterForm
from django.urls import reverse_lazy
from django.db.models.functions import Lower

from firsttuto.utils import get_max_order, reorder
from firsttuto.models import Task, UserTask
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Create your views here.

class IndexView(TemplateView):
    template_name = 'index.html'

class LoginView(LoginView):
    template_name = 'registration/login.html'

    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('index')
class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.http.response import HttpResponse


def custom_logout(request):
    logout(request)
    # Redirigez vers la page souhaitée après la déconnexion
    return redirect('index')

def check_username(request):
    username = request.POST.get('username')
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse("<div id='username-error' class='error'> This username already exists. </div>")
    return HttpResponse("<div id='username-error' style='color:green'> This username is free </div>")


class TasksList(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Task
    template_name = 'tasks/tasks.html'
    context_object_name = 'tasks'
    paginate_by = 5

    def get_queryset(self):
        return UserTask.objects.prefetch_related('task').filter(user=self.request.user) 
    
    
from django.contrib import messages
@login_required    
def add_task(request):
    description = request.POST.get('taskdescription')
    task = Task.objects.get_or_create(description=description)[0]
    
    #request.user.tasks.add(task)
    #tasks = request.user.tasks.all()
    
    if(not UserTask.objects.filter(user=request.user, task=task).exists()):
        UserTask.objects.create(user=request.user, task=task, order=get_max_order(request.user))
    
    messages.success(request, 'Task added successfully')
    return render(request, 'tasks/task-list.html', {'tasks': UserTask.objects.filter(user=request.user)})    

@login_required    
@require_http_methods(['DELETE'])
def delete_task(request, task_id):
    UserTask.objects.get(pk=task_id).delete()
    tasks = UserTask.objects.filter(user=request.user)
    reorder(request.user)
    return render(request, 'tasks/task-list.html', {'tasks': tasks})

from django.http import QueryDict

@login_required    
def get_task(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task:     
        # Si la requête est de type PUT, on met à jour la description de la tâche
        if request.method == 'PUT':
            # On récupère la description envoyée par le client
            put = QueryDict(request.body)
            description = put.get('taskdescription')
            task.description = description
            task.save()
            return render(request, 'tasks/task-form.html', {'task': task})
        # Si la requête est de type GET, on renvoie le template avec la tâche
        usertasks = UserTask.objects.filter(task=task).prefetch_related('user').order_by(Lower('user__username'))
        # On récupère le nombre d'utilisateurs inscrits à la tâche
        is_user_subscribed = UserTask.objects.filter(user=request.user, task=task).exists()
        return render(request, 'tasks/task.html', {'task': task, 'usertasks': usertasks, 'nb_users': len(usertasks), 'is_user_subscribed': is_user_subscribed})
    return HttpResponse('Task not found')

@login_required    
def edit_task(request, task_id):
    task = Task.objects.get(pk=task_id)
    if task:
        return render(request, 'tasks/task_edit_form.html', {'task': task})
    return HttpResponse('Task not found')

def search_task(request):
    search_text = request.POST.get('search')
    user_tasks = UserTask.objects.filter(user=request.user)
    results = Task.objects.filter(description__icontains=search_text).exclude(description__icontains=user_tasks.values_list('task__description', flat=True))[:10]
    print(results)
    return render(request, 'tasks/search-result.html', {'results': results})


def clear(request):
    return HttpResponse('')

"""def sort(request):
    res = request.POST.getlist('task_order')
    tasks = []
    for count, task_id in enumerate(res, start=1):
        usertask = UserTask.objects.get(pk=task_id)
        usertask.order = count
        usertask.save()
        tasks.append(usertask)
    return render(request, 'tasks/task-list.html', {'tasks': tasks})"""

def sort(request):
    """
    Cette vue est appelée lorsque l'utilisateur trie les tâches.
    C'est une version amélioré de la vue précédente.
    """
    res = request.POST.getlist('task_order')
    # Créez un dictionnaire pour associer l'ID de task à son nouvel ordre
    new_order = {str(id): index for index, id in enumerate(res, start=1)}
    
    # Récupérez tous les UserTasks concernés en une seule requête
    user_tasks = UserTask.objects.filter(pk__in=res)

    # Mettez à jour les objets en mémoire
    for user_task in user_tasks:
        user_task.order = new_order[str(user_task.id)]

    # Utilisez bulk_update pour enregistrer toutes les modifications
    UserTask.objects.bulk_update(user_tasks, ['order'])

    # Le template peut être mis à jour avec la liste triée
    sorted_tasks = sorted(user_tasks, key=lambda x: x.order)
    return render(request, 'tasks/task-list.html', {'tasks': sorted_tasks})


class AllTasksList(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Task
    template_name = 'tasks/all-tasks.html'
    context_object_name = 'tasks'
    paginate_by = 5

    def get_queryset(self):
        return Task.objects.all()
    
    
@login_required
def load_more_tasks(request):
    tasks_list = Task.objects.all()
    paginator = Paginator(tasks_list, 5)  # Afficher 5 task par page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "tasks/display-tasks.html", {"page_obj": page_obj})

@login_required
def inscription_task(request, task_id):
    user = request.user
    # Récupérer la tâche
    task = Task.objects.get(pk=task_id)
    
    # On récupère l'objet UserTask associé à l'utilisateur et à la tâche
    user_task, created = UserTask.objects.get_or_create(user=user, task=task,
                                                        defaults={'order': get_max_order(user)})
    # Si l'objet existe déjà, on le supprime, sinon on le crée
    if not created:
        user_task.delete()
        reorder(user)  # On réordonne les tâches
        is_user_subscribed = False
    else:
        is_user_subscribed = True

    # On récupère les UserTask associés à la tâche
    usertasks = UserTask.objects.filter(task=task).order_by(Lower('user__username'))

    # On récupère le nombre d'utilisateurs inscrits à la tâche
    nb_users = usertasks.count()
    # On renvoie le template avec les données
    return render(request, "tasks/task.html", {"usertasks": usertasks, "nb_users": nb_users, "hx_swap_oob": True, "task": task, 'is_user_subscribed': is_user_subscribed})
