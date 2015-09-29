
from django.views.generic import ListView, DetailView
from articles.models import Article


class ArticlesView(ListView):
    model = Article
    template_name = 'articles.html'
    context_object_name = 'articles'


class ArticleView(DetailView):
    model = Article
    template_name = 'article.html'
