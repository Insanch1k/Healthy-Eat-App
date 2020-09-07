from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from .models import Post, Comment
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .forms import CommentForm



class MainView(ListView):
    
    '''Functipn for showing list of posts'''
    
    template_name = 'barbershop/home.html'
    paginate_by = 2
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['most_populars'] = Post.objects.annotate(count=Count('comments')).order_by('-count')[:3]
        return context


def post_detail(request, slug):
    
    '''Function for showing detail information about posts'''
    
    post = get_object_or_404(Post, slug=slug)

    comments = post.comments.all()

    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.owner = request.user
            new_comment.save()
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'new_comment': new_comment,
    }
    return render(request, 'posts/post_detail.html', context)







