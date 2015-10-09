from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView

from .models import Article


class ArticlesView(ListView):
    model = Article
    template_name = 'articles.html'
    context_object_name = 'articles'
    queryset = Article.objects.filter(published=True)


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article.html'

    def get_object(self, queryset=None):
        article = super(ArticleDetailView, self).get_object(queryset)
        if not article.published and article.owner != self.request.user:
            raise Http404()
        return article


class ArticleCreateView(CreateView):
    model = Article
    fields = ('headline', 'description')
    template_name = 'article_form.html'


