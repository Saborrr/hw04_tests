from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user


NUMBER_OF_POST = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUMBER_OF_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, NUMBER_OF_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    posts_number = posts.count()
    paginator = Paginator(posts, NUMBER_OF_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'post_num': posts_number,
        'page_obj': page_obj,
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    posts = Post.objects.get(id=post_id)
    title = posts.text[:30]
    posts_number = Post.objects.filter(author=posts.author).count()
    context = {
        'post_num': posts_number,
        'post': posts,
        'title': title,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    user = get_user(request)
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            frm = form.save(commit=False)
            frm.author = user
            frm.save()
            return redirect(f'/profile/{user.username}/')
    form = PostForm(files=request.FILES or None)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    template = 'posts/create_post.html'

    if request.method == 'POST':
        if request.user != post.author:
            return redirect('posts:post_detail', post_id=post.id)
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}/')
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, template, context)
