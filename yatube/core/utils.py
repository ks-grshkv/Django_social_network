from django.core.paginator import Paginator


def paginate(request, post_list, num):
    paginator = Paginator(post_list, num)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
