from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
from django.db.models import Count

def post_list_view(request):
    """Liste tous les articles publiés."""
    posts = Post.objects.filter(status='PUBLISHED')
    categories = Category.objects.annotate(posts_count=Count('posts')).filter(posts_count__gt=0)
    
    # Filtre par catégorie si présent
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
        
    # Filtre par mot-clé si présent
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
        
    recent_posts = Post.objects.filter(status='PUBLISHED').order_by('-created_at')[:5]
    
    context = {
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/post_list.html', context)

def post_detail_view(request, slug):
    """Affiche un article spécifique."""
    post = get_object_or_404(Post, slug=slug, status='PUBLISHED')
    post.views_count += 1
    post.save()
    
    related_posts = Post.objects.filter(category=post.category, status='PUBLISHED').exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)
