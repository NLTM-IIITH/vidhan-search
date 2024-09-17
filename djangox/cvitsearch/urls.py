from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from home import views
from home.admin import admin_site
from home.views import LineSegmentImageView

router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'pages', views.PageViewSet)

urlpatterns = [
    path('search/api/', include(router.urls)),
    path('search/api/search/', views.search, name='search'),
    path('search/api/book/<int:book_id>/pages/', views.book_pages, name='book_pages'),
    path('search/api/line_segment/', views.line_segment, name='line_segment'),
    path('search/api/matched_images/', LineSegmentImageView.as_view(), name='matched_images'),
    path('search/api/fuzzy_search/', views.fuzzy_search_view, name='fuzzy_search'),
    path('search/admin/', admin_site.urls)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
