from django.shortcuts import render, get_object_or_404, redirect
from .models import Follow, Group, Post, User
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user


NUMBER_OF_POST = 10
SYMBOLS_TEXT = 30


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, NUMBER_OF_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    template = 'posts/index.html'
    return render(request, template, context)


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
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    posts_number = posts.count()
    paginator = Paginator(posts, NUMBER_OF_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    follow = (request.user.is_authenticated and author != request.user
              and Follow.objects.filter(
                  author=author,
                  user=request.user).exists())
    context = {
        'author': author,
        'post_num': posts_number,
        'page_obj': page_obj,
        'following': follow,
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    posts = get_object_or_404(Post, pk=post_id)
    title = posts.text[:SYMBOLS_TEXT]
    posts_number = Post.objects.filter(author=posts.author).count()
    comments = posts.comments.all()
    form = CommentForm()
    author = posts.author
    context = {
        'post_num': posts_number,
        'post': posts,
        'title': title,
        'comments': comments,
        'author': author,
        'form': form,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    user = get_user(request)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
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
    template = 'posts/create_post.html'
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}/')
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    template = 'posts/create_post.html'
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, NUMBER_OF_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    template = 'posts/follow.html'
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (author != request.user
        and not Follow.objects.filter(user=request.user,
                                      author=author).exists()):
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(Follow,
                      user=request.user,
                      author__username=username).delete()
    return redirect('posts:profile', username=username)
