from django.shortcuts import render

# Create your views here.
def lattice_matching_view(request, *args,**kwargs):
    context = {}
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context.update({"is_signed_in": is_signed_in})
    return render(request, 'lattice.html', context)