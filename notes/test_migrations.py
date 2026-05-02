from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class NoteRenameMigrationTests(TransactionTestCase):
    migrate_from = [('notes', '0009_auto_20200611_2107')]
    migrate_to = [('notes', '0010_rename_notes_to_note')]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        old_apps = self.executor.loader.project_state(self.migrate_from).apps
        self._prepare_old_state(old_apps)

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        self.apps = self.executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def _prepare_old_state(self, apps):
        User = apps.get_model('auth', 'User')
        Notes = apps.get_model('notes', 'Notes')
        self.user = User.objects.create(username='note-migration-user')
        self.note = Notes.objects.create(owner=self.user, title='Private', body='Secret')

    def test_notes_model_is_renamed_and_keeps_data(self):
        Note = self.apps.get_model('notes', 'Note')

        note = Note.objects.get(pk=self.note.pk)

        self.assertEqual(note.title, 'Private')
        self.assertEqual(note.owner_id, self.user.pk)
