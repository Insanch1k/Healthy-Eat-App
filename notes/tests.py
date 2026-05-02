from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Note


class NotesAuthorizationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass12345')
        self.other = User.objects.create_user(username='other', password='pass12345')
        self.note = Note.objects.create(owner=self.owner, title='Private', body='Secret')

    def test_user_cannot_edit_another_users_note(self):
        self.client.login(username='other', password='pass12345')

        response = self.client.post(
            reverse('notes:update', args=[self.note.id]),
            {'title': 'Changed', 'body': 'Leaked'},
        )

        self.assertEqual(response.status_code, 404)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Private')

    def test_user_cannot_delete_another_users_note(self):
        self.client.login(username='other', password='pass12345')

        response = self.client.post(reverse('notes:delete', args=[self.note.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())

    def test_owner_can_create_note(self):
        self.client.login(username='owner', password='pass12345')

        response = self.client.post(
            reverse('notes:home_notes'),
            {'title': 'Meal prep', 'body': 'Cook rice'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(owner=self.owner, title='Meal prep').exists())

    def test_user_notes_related_name_returns_owned_notes(self):
        self.assertEqual(list(self.owner.notes.all()), [self.note])

    def test_legacy_note_urls_redirect_to_canonical_urls(self):
        self.client.login(username='owner', password='pass12345')

        self.assertEqual(
            self.client.get(f'/notes/update/{self.note.id}/', follow=False)['Location'],
            reverse('notes:update', args=[self.note.id]),
        )
        self.assertEqual(
            self.client.get(f'/notes/delete/{self.note.id}', follow=False)['Location'],
            reverse('notes:delete', args=[self.note.id]),
        )
