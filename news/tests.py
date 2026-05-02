from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from recipes.models import Profile

from .models import Comment, Post


class NewsCommentTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='pass12345')
        self.commenter = User.objects.create_user(username='commenter', password='pass12345')
        Profile.objects.create(user=self.commenter, phone='+48123456789')
        self.post = Post.objects.create(
            title='Healthy Eating',
            slug='healthy-eating',
            body='Eat vegetables',
            author=self.author,
        )

    def test_post_detail_is_public(self):
        response = self.client.get(reverse('news:post-detail', args=[self.post.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Healthy Eating')

    def test_root_redirects_to_news(self):
        response = self.client.get('/', follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('news:main'))

    def test_anonymous_comment_post_redirects_to_login(self):
        response = self.client.post(
            reverse('news:post-detail', args=[self.post.slug]),
            {'body': 'Nice'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])
        self.assertEqual(Comment.objects.count(), 0)

    def test_authenticated_user_can_comment(self):
        self.client.login(username='commenter', password='pass12345')

        response = self.client.post(
            reverse('news:post-detail', args=[self.post.slug]),
            {'body': 'Nice'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(owner=self.commenter, body='Nice').exists())
