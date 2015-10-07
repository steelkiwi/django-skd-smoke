
from django.views.generic import ListView, DetailView, CreateView
from .models import Article


class ArticlesView(ListView):
    model = Article
    template_name = 'articles.html'
    context_object_name = 'articles'


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article.html'


class ArticleCreateView(CreateView):
    model = Article
    fields = ('headline', 'description')
    template_name = 'article_form.html'


