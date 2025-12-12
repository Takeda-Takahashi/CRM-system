from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.shortcuts import render
from django.core.paginator import Paginator
from rest_framework.response import Response

from .models import (
    Participants, TariffPlans, Subscriptions, Payments,
    TrainingSessions, TrainingAttendance, Equipment, EquipmentRentals,
    Events, EventParticipants, Positions, SystemUsers, ChangeLogs,
    Lockers, LockerRentals
)
from .serializers import (
    ParticipantSerializer, TariffPlanSerializer, SubscriptionSerializer,
    PaymentSerializer, TrainingSessionSerializer, TrainingAttendanceSerializer,
    EquipmentSerializer, EquipmentRentalSerializer, EventSerializer,
    EventParticipantSerializer, PositionSerializer, SystemUserSerializer,
    ChangeLogSerializer, LockerSerializer, LockerRentalSerializer
)


# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
def get_tokens_for_user(user):
    """Генерирует JWT токены"""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# === УЧАСТНИКИ ===
@extend_schema_view(
    list=extend_schema(summary="Список всех участников"),
    retrieve=extend_schema(summary="Участник по ID"),
    create=extend_schema(summary="Создать участника"),
    update=extend_schema(summary="Обновить участника"),
    partial_update=extend_schema(summary="Частичное обновление"),
    destroy=extend_schema(summary="Удалить участника"),
)
class ParticipantsViewSet(viewsets.ModelViewSet):
    queryset = Participants.objects.all()
    serializer_class = ParticipantSerializer
    permission_classes = [AllowAny]


# НОВАЯ view для HTML страницы
def students_list_view(request):
    """Отображение списка учеников в HTML"""
    # Получаем всех участников из базы
    participants_list = Participants.objects.all().order_by('last_name', 'first_name')

    # Пагинация
    paginator = Paginator(participants_list, 20)  # 20 участников на страницу
    page_number = request.GET.get('page')
    participants = paginator.get_page(page_number)

    # Подготавливаем данные для шаблона
    context = {
        'students': participants,  # Переименовываем для шаблона
        'page_obj': participants,  # Для пагинации
    }

    return render(request, 'students_list.html', context)


# === ТАРИФНЫЕ ПЛАНЫ ===
@extend_schema_view(
    list=extend_schema(summary="Список тарифов"),
    retrieve=extend_schema(summary="Тариф по ID"),
    create=extend_schema(summary="Создать тариф"),
)
class TariffPlansViewSet(viewsets.ModelViewSet):
    queryset = TariffPlans.objects.all()
    serializer_class = TariffPlanSerializer
    permission_classes = [AllowAny]


# === АБОНЕМЕНТЫ ===
class SubscriptionsViewSet(viewsets.ModelViewSet):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [AllowAny]


# === ПЛАТЕЖИ ===
class PaymentsViewSet(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]


# === ТРЕНИРОВКИ ===
class TrainingSessionsViewSet(viewsets.ModelViewSet):
    queryset = TrainingSessions.objects.all()
    serializer_class = TrainingSessionSerializer
    permission_classes = [AllowAny]


# === ПОСЕЩАЕМОСТЬ ===
class TrainingAttendanceViewSet(viewsets.ModelViewSet):
    queryset = TrainingAttendance.objects.all()
    serializer_class = TrainingAttendanceSerializer
    permission_classes = [AllowAny]


# === ИНВЕНТАРЬ ===
class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [AllowAny]


# === АРЕНДА ИНВЕНТАРЯ ===
class EquipmentRentalsViewSet(viewsets.ModelViewSet):
    queryset = EquipmentRentals.objects.all()
    serializer_class = EquipmentRentalSerializer
    permission_classes = [AllowAny]


# === МЕРОПРИЯТИЯ ===
class EventsViewSet(viewsets.ModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]


# === УЧАСТНИКИ МЕРОПРИЯТИЙ ===
class EventParticipantsViewSet(viewsets.ModelViewSet):
    queryset = EventParticipants.objects.all()
    serializer_class = EventParticipantSerializer
    permission_classes = [AllowAny]


# === ДОЛЖНОСТИ ===
class PositionsViewSet(viewsets.ModelViewSet):
    queryset = Positions.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [AllowAny]


# === СИСТЕМНЫЕ ПОЛЬЗОВАТЕЛИ ===
class SystemUsersViewSet(viewsets.ModelViewSet):
    queryset = SystemUsers.objects.all()
    serializer_class = SystemUserSerializer
    permission_classes = [AllowAny]


# === ЛОГИ ИЗМЕНЕНИЙ (только чтение) ===
class ChangeLogsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChangeLogs.objects.all().order_by('-change_time')
    serializer_class = ChangeLogSerializer
    permission_classes = [AllowAny]


# === ШКАФЫ ===
class LockersViewSet(viewsets.ModelViewSet):
    queryset = Lockers.objects.all()
    serializer_class = LockerSerializer
    permission_classes = [AllowAny]


# === АРЕНДА ШКАФОВ ===
class LockerRentalsViewSet(viewsets.ModelViewSet):
    queryset = LockerRentals.objects.all()
    serializer_class = LockerRentalSerializer
    permission_classes = [AllowAny]


# === ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ ===
# core/views.py
# core/views.py
class CurrentUserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Получаем user_id из токена
        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return Response(
                {"detail": "Токен не предоставлен"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        import jwt
        token = auth_header.split(' ')[1]

        try:
            # Декодируем токен
            decoded = jwt.decode(token, options={"verify_signature": False})
            user_id = decoded.get('user_id')
            print(f"DEBUG: User ID from token: {user_id}")

            # Получаем пользователя
            try:
                user = SystemUsers.objects.get(id=user_id)
                print(f"DEBUG: Found user: {user.email}")

                # Инициализируем данные
                profile_data = {
                    'email': user.email or "",
                    'role': user.role or "user",
                    'first_name': "",
                    'last_name': "",
                    'phone': "",
                    'birth_date': "",
                    'join_date': "",
                    'emergency_contact': "",
                    'address': "",
                }

                # Если есть связанный участник, берем все данные оттуда
                if user.member:
                    try:
                        member = Participants.objects.get(id=user.member_id)
                        print(f"DEBUG: Found member: {member.first_name} {member.last_name}")

                        # Форматируем даты в строку (если они не None)
                        birth_date_str = ""
                        join_date_str = ""

                        if member.birth_date:
                            birth_date_str = member.birth_date.strftime('%Y-%m-%d')

                        if member.join_date:
                            join_date_str = member.join_date.strftime('%Y-%m-%d')

                        # Заполняем данные из participants
                        profile_data.update({
                            'first_name': member.first_name or "",
                            'last_name': member.last_name or "",
                            'phone': member.phone or "",
                            'birth_date': birth_date_str,
                            'join_date': join_date_str,
                            'emergency_contact': member.emergency_contact or "",
                            'address': member.address or "",
                        })

                    except Participants.DoesNotExist:
                        print("DEBUG: Member not found")

                # Если какие-то поля пустые, ставим заглушки
                if not profile_data['phone']:
                    profile_data['phone'] = '+7 (999) 000-00-00'
                if not profile_data['birth_date']:
                    profile_data['birth_date'] = '1990-01-01'
                if not profile_data['join_date']:
                    profile_data['join_date'] = '2024-01-01'
                if not profile_data['emergency_contact']:
                    profile_data['emergency_contact'] = 'Не указан'
                if not profile_data['address']:
                    profile_data['address'] = 'Не указан'

                return Response(profile_data)

            except SystemUsers.DoesNotExist:
                print(f"DEBUG: User with ID {user_id} not found in DB")
                return Response(
                    {"detail": "Пользователь не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            print(f"DEBUG: Error: {e}")
            return Response(
                {"detail": "Ошибка обработки токена"},
                status=status.HTTP_400_BAD_REQUEST
            )

# === ВХОД (исправленная версия) ===
@extend_schema(
    summary="Вход в систему",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "password": {"type": "string"}
            },
            "required": ["email", "password"]
        }
    },
    responses={
        200: {"type": "object", "properties": {
            "access": {"type": "string"},
            "refresh": {"type": "string"},
            "user": {"type": "object"}
        }},
        400: {"detail": "Email и пароль обязательны"},
        401: {"detail": "Неверный email или пароль"}
    }
)
class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"detail": "Email и пароль обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = SystemUsers.objects.get(email=email)
        except SystemUsers.DoesNotExist:
            return Response(
                {"detail": "Неверный email или пароль"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # === ПРОВЕРКА ПАРОЛЯ (как строка в password_hash) ===
        if user.password_hash != password:
            return Response(
                {"detail": "Неверный email или пароль"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # JWT-токены
        try:
            tokens = get_tokens_for_user(user)
        except Exception as e:
            print(f"Ошибка генерации токенов: {e}")
            # Если не работает стандартный способ, создаем токены вручную
            refresh = RefreshToken()
            refresh['user_id'] = user.id
            tokens = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }

        # Получаем полные данные пользователя
        first_name = ''
        last_name = ''
        phone = ''
        birth_date = ''
        join_date = ''
        emergency_contact = ''
        address = ''

        if user.member:
            try:
                member = Participants.objects.get(id=user.member_id)
                first_name = member.first_name or ''
                last_name = member.last_name or ''
                phone = member.phone or ''
                birth_date = member.birth_date.strftime('%Y-%m-%d') if member.birth_date else ''
                join_date = member.join_date.strftime('%Y-%m-%d') if member.join_date else ''
                emergency_contact = member.emergency_contact or ''
                address = member.address or ''
            except Participants.DoesNotExist:
                pass

        return Response({
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "birth_date": birth_date,
                "join_date": join_date,
                "emergency_contact": emergency_contact,
                "address": address,
            }
        })