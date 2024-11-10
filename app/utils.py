from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def paginate(objects_list, request, per_page=5):
    try:
        page_num = int(request.GET.get('page', 1))
    except ValueError:
        page_num = 1

    paginator = Paginator(objects_list, per_page)

    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        if (page_num < 1):
            page = paginator.page(1)
        else:
            page = paginator.page(paginator.num_pages)

    return page