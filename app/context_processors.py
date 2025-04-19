from askme_novitski.settings import CENTRIFUGO_SECRET_KEY, CENTRIFUGO_WS_URL
import jwt
import time
from .models import Tag
from .models import Profile
from django.core.cache import cache

def get_centrifugo_info(user_id):
    secret = CENTRIFUGO_SECRET_KEY
    claims = {"sub": str(user_id), "exp": int(time.time()) + 5*60}
    token = jwt.encode(claims, secret, algorithm="HS256")
    return {"token": token, "ws_url": CENTRIFUGO_WS_URL}

def popular_tags(request):
    tags_with_colors = cache.get('popular_tags')
    if not tags_with_colors:
        tags = Tag.objects.get_popular()
        colors = ['black', '#cd1714', 'black', '#cd1714', '#54b250', 'black', 'black', '#ff9f23', 'black', 'black']
        tags_with_colors = list(zip(tags, colors))
        cache.set('popular_tags', tags_with_colors, timeout=61)
    return {'popular_tags': tags_with_colors}

def best_members(request):
    users = cache.get('best_members')
    if not users:
        users = Profile.objects.get_best()
        cache.set('best_members', users, timeout=3800)

    print(users) 
    return {'best_members': users}