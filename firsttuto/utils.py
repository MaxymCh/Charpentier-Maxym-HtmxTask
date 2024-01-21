from django.db.models import Max

from firsttuto.models import Task, UserTask

def get_max_order(user):
    max_order = UserTask.objects.filter(user=user).aggregate(Max('order'))['order__max']
    if max_order is None:
        return 1
    return max_order+1

def reorder(user):
    usertasks = UserTask.objects.filter(user=user)
    if not usertasks.exists():
        return
    nbtasks = usertasks.count()
    new_ordering = range(1, nbtasks+1)
    for order, usertask in zip(new_ordering, usertasks):
        usertask.order = order
        usertask.save()
