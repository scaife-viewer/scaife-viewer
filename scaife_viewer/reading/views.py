from django.shortcuts import render

from account.decorators import login_required

from .models import recent


@login_required
def logs(request):
    reading_logs = request.user.readinglog_set.order_by("-timestamp")

    return render(request, "reading/logs.html", {
        "logs": reading_logs,
        "recent": recent(request.user),
    })
