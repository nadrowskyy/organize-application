from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        # extra funkcjonalności przed wywołaniem oryginalnej funkcji
        # sprawdza czy użytkownik jest zalogowany, jeśli tak to przekierowuje do strony głównej
        # bo zalogowany użytkownik nie powinien móc przejść ponownie na stronę logowania czy rejestracji
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, *kwargs)
    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            # sprawdza czy użytkownik jest przypisany do jakiejs grupy
            if request.user.groups.exists():
                print('allowed users wrapper', request.user.groups.all())
                group = request.user.groups.all()[0].name
            # jeśli jest w grupie podanej przy wywołaniu dekoratora to może wejść na daną stronę
            # np. nie chcemy żeby zwykły użytkownik wszedł na stronę dostępną dla admina jak create_event
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            # jeśli nie jest przypisany do podanej wcześniej grupy to dostaje poniższy komunikat
            else:
                return HttpResponse('You are not authorized to view this page')
        return wrapper_func
    return decorator
