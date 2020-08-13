from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
# Create your views here.
def lattice_matching_view(request, *args,**kwargs):
    context = {}
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context.update({"is_signed_in": is_signed_in})

    if request.method == 'POST':
        user_input_1 = request.FILES['user_input_1']
        print(str(user_input_1.read()))
        fs = FileSystemStorage()
        fs.save(user_input_1.name, user_input_1)

    return render(request, 'lattice.html', context)