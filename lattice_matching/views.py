from django.shortcuts import render
from lattice_matching.eg_Ima import  StructureMatcher
from django.core.files.storage import FileSystemStorage
# Create your views here.
def lattice_matching_view(request, *args,**kwargs):
    context = {}
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context.update({"is_signed_in": is_signed_in})

    if request.method == 'POST':
        user_input_1 = request.FILES.get('user_input_1', None)
        user_input_2 = request.FILES.get('user_input_2', None)
        user_input_1 = user_input_1.read().decode("utf-8")
        user_input_2 = user_input_2.read().decode("utf-8")
        a= StructureMatcher(user_input_1,user_input_2,20, 5)
        print(a)


    return render(request, 'lattice.html', context)