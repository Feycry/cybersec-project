from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db import connection
from .models import Note

@login_required
def notesView(request):
    search_query = request.GET.get('search', '').strip()
    
    #FLAW 3 (A03 - Injection): SQL injection vulnerability in search
    #For example, type the following into the search field to see every users notes:
    #%' OR '1'='1' --
    #You can also visit http://127.0.0.1:8000/notes/?search=%25%27+OR+%271%27%3D%271%27+--
    #It should also be possible to get user information and to drop tables from the database
    if search_query:
        try:
            with connection.cursor() as cursor:
                sql = f"SELECT id, content, created_at FROM pages_note WHERE owner_id = {request.user.id} AND content LIKE '%{search_query}%' ORDER BY created_at DESC"
                cursor.execute(sql)
                
                notes = []
                for row in cursor.fetchall():
                    note = Note(id=row[0], content=row[1], created_at=row[2])
                    note.owner = request.user
                    notes.append(note)
        except Exception as e:
            notes = Note.objects.filter(owner=request.user).order_by('-created_at')
    else:
        notes = Note.objects.filter(owner=request.user).order_by('-created_at')
    #FIX: Use filter instead of SQL
    #(This means commenting out the above if-else-statement and enabling the code below instead)
    #if search_query:
    #   notes = Note.objects.filter(owner=request.user, content__icontains=search_query).order_by('-created_at')
    #else:
    #   notes = Note.objects.filter(owner=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if content:
            Note.objects.create(
                owner=request.user,
                content=content
            )
            return redirect('/notes/')
    
    return render(request, 'pages/notes.html', {'notes': notes, 'search_query': search_query})


@login_required
def deleteNoteView(request, note_id):
    #FLAW 1 (A01 - Broken Access Control): 
    #Any logged in user can delete any note by typing in the correct url
    #Even if the note does not belong to them
    #Example: http://127.0.0.1:8000/notes/1/delete/
    note = get_object_or_404(Note, id=note_id)
    #FIX: Check that the owner matches the user
    #note = get_object_or_404(Note, id=note_id, owner=request.user)
    
    if request.method == 'POST':
        note.delete()
        return redirect('/notes/')
    
    return render(request, 'pages/delete_note.html', {'note': note})


def mainPageView(request):
    if request.user.is_authenticated:
        return redirect('/notes/')
    return render(request, 'pages/main.html')


def debugView(request):
    #FLAW 5 (A05 - Security Misconfiguration):
    #Debug endpoint that exposes sensitive system and user information
    #Visit http://127.0.0.1:8000/debug
    
    from django.conf import settings
    
    all_users = User.objects.all()
    all_notes = Note.objects.all()
    
    debug_info = {
        'secret_key': settings.SECRET_KEY,
        'debug_mode': settings.DEBUG,
        'all_users': all_users,
        'all_notes': all_notes,
    }
    
    return render(request, 'pages/debug.html', {'debug_info': debug_info})
    
    #FIX: Remove this function or just comment out from urls.py