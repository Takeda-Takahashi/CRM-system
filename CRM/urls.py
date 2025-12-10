# CRM/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static

from core.views import (
    ParticipantsViewSet, TariffPlansViewSet, SubscriptionsViewSet,
    PaymentsViewSet, TrainingSessionsViewSet, TrainingAttendanceViewSet,
    EquipmentViewSet, EquipmentRentalsViewSet, EventsViewSet,
    EventParticipantsViewSet, PositionsViewSet, SystemUsersViewSet,
    ChangeLogsViewSet, LockersViewSet, LockerRentalsViewSet,
    CurrentUserProfile, CustomLoginView
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
    path('api/profile/', CurrentUserProfile.as_view(), name='profile'),  # ← ИЗМЕНИТЕ НА profile/

    # HTML страницы
    path('login/', login_page, name='login'),
    path('dashboard/', dashboard_page, name='dashboard'),
    path('profile/', profile_page, name='profile-page'),
    path('api/me/', CurrentUserProfile.as_view(), name='current-user'),
    path('api/profile/', CurrentUserProfile.as_view(), name='profile'),
    path('lessons/', lessons_page, name='lessons'),
    # Главная → логин
    path('', login_page),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)