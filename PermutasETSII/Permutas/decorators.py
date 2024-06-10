from django.shortcuts import redirect
from django.contrib import messages


def logout_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Ya has iniciado sesión, no puedes volver a iniciar sesión o registrarte.')
            return redirect('home')  # Redirige a la página de inicio o donde desees
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func
