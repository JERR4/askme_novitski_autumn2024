def popular_tags(request):
    from .models import Tag
    tags = Tag.objects.get_popular()[:8]
    colors = ['black', '#cd1714', 'black', '#cd1714', '#54b250', 'black', 'black', '#ff9f23']
    tags_with_colors = list(zip(tags, colors))
    return {'popular_tags': tags_with_colors}

def best_members(request):
    from .models import Profile
    users = Profile.objects.get_best()[:5]
    return {'best_members': users}