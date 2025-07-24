from django.urls import path

from .views import mainPageView, notesView, deleteNoteView, debugView

urlpatterns = [
    path('', mainPageView, name='home'),
    path('notes/', notesView, name='notes'),
    path('notes/<int:note_id>/delete/', deleteNoteView, name='delete_note'),
    path('debug/', debugView, name='debug'),  #FLAW 5: Exposed debug endpoint
]