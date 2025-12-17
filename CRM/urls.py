# CRM/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static

from core import views
from core.views import (
    ParticipantsViewSet, TariffPlansViewSet, SubscriptionsViewSet,
    PaymentsViewSet, TrainingSessionsViewSet, TrainingAttendanceViewSet,
    EquipmentViewSet, EquipmentRentalsViewSet, EventsViewSet,
    EventParticipantsViewSet, PositionsViewSet, SystemUsersViewSet,
    ChangeLogsViewSet, LockersViewSet, LockerRentalsViewSet,
    CurrentUserProfile, CustomLoginView, participant_card_view, update_locker_view, create_locker_view
)

# === Роутер DRF ===
router = DefaultRouter()
router.register(r'participants', ParticipantsViewSet)
router.register(r'tariff-plans', TariffPlansViewSet)
router.register(r'subscriptions', SubscriptionsViewSet)
router.register(r'payments', PaymentsViewSet)
router.register(r'training-sessions', TrainingSessionsViewSet)
router.register(r'training-attendance', TrainingAttendanceViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'equipment-rentals', EquipmentRentalsViewSet)
router.register(r'events', EventsViewSet)
router.register(r'event-participants', EventParticipantsViewSet)
router.register(r'positions', PositionsViewSet)
router.register(r'system-users', SystemUsersViewSet)
router.register(r'change-logs', ChangeLogsViewSet, basename='changelogs')
router.register(r'lockers', LockersViewSet)
router.register(r'locker-rentals', LockerRentalsViewSet)

# === HTML страницы ===
def login_page(request):
    return render(request, 'login.html')

def dashboard_page(request):
    return render(request, 'ParticipantCard.html')

def profile_page(request):
    return render(request, 'profile.html')

def lessons_page(request):
    return render(request, 'lessons_calendar.html')

def student_card_page(request, student_id):
    context = {
        'student_id': student_id,
    }
    return render(request, 'card.html', context)


def clients_page(request):
    """Страница со списком учеников"""
    from core.models import Participants  # Импортируем модель
    from django.core.paginator import Paginator

    # Получаем всех участников (учеников)
    participants_list = Participants.objects.all().order_by('last_name', 'first_name')

    # Пагинация
    paginator = Paginator(participants_list, 20)  # 20 на страницу
    page_number = request.GET.get('page')
    participants = paginator.get_page(page_number)

    # Передаем данные в шаблон
    context = {
        'students': participants,  # Для шаблона используем переменную 'students'
    }

    return render(request, 'students_list.html', context)

# === Основные маршруты ===
urlpatterns = [
    path('admin/', admin.site.urls),

    # Документация API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API через роутер
    path('api/', include(router.urls)),

    # === НАШ ВХОД (БЕЗ ХЭША) ===
    path('api/login/', CustomLoginView.as_view(), name='custom_login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Профиль текущего пользователя - ВАЖНО: фронтенд ожидает /api/profile/
    path('api/profile/', CurrentUserProfile.as_view(), name='profile'),

    # HTML страницы
    path('login/', login_page, name='login'),
    path('dashboard/', dashboard_page, name='dashboard'),
    path('profile/', profile_page, name='profile-page'),
    path('api/me/', CurrentUserProfile.as_view(), name='current-user'),
    path('api/profile/', CurrentUserProfile.as_view(), name='profile'),
    path('lessons/', lessons_page, name='lessons'),
    path('clients/', clients_page, name='clients'),
    path('students/<int:participant_id>/', participant_card_view, name='participant_card'),
    path('lockers/', views.lockers_list_view, name='lockers_list'),
    path('api/lockers/<int:locker_id>/update/', update_locker_view, name='update_locker'),
    path('api/lockers/', create_locker_view, name='create_locker'),
    path('api/participants/available/', views.get_available_participants, name='available_participants'),
    path('api/lockers/<int:locker_id>/delete/', views.delete_locker, name='delete_locker'),
    # Главная → логин
    path('', login_page),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)