from .models import Collaborator


def invitations_context(request):
    if request.user.is_authenticated:
        invitations = Collaborator.objects.filter(user=request.user, is_accepted=False)
        invitations_count = invitations.count()
        return {
            "invitations_count": invitations_count, "user": request.user,
        }
    return {}
