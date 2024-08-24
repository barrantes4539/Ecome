from django import template
from ..models import Profile

register = template.Library()

@register.filter
def get_profile(profiles, user_id):
    return profiles.filter(user_id=user_id).first()