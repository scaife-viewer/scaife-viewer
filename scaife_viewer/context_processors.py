def google_analytics(request):
    ga_code = None
    if request.site.id == 2:
        ga_code = "UA-107671034-1"
    elif request.site.id == 3:
        ga_code = "UA-107671034-4"
    return {
        "ga_code": ga_code,
    }
