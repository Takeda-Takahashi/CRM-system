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


from django.shortcuts import render, get_object_or_404
from .models import Participants, Subscriptions, Payments, Lockers

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Participants, Subscriptions, Payments, TrainingSessions, TrainingAttendance, LockerRentals, \
    SystemUsers, EventParticipants, Events


def participant_card_view(request, participant_id):
    # Получаем участника из базы данных
    participant = get_object_or_404(Participants, id=participant_id)

    # Получаем связанные данные
    # Абонементы
    subscriptions = Subscriptions.objects.filter(participant=participant)

    # Платежи - ДВА ОТДЕЛЬНЫХ QUERYSET
    payments_all = Payments.objects.filter(participant=participant)
    payments = payments_all.order_by('-payment_date')[:10]  # Только для отображения

    # Тренировки (группы)
    training_sessions = TrainingSessions.objects.filter(
        trainingattendance__participant=participant
    ).distinct().order_by('-datetime')

    # Посещаемость тренировок
    attendance_records = TrainingAttendance.objects.filter(
        participant=participant
    ).order_by('-session__datetime')

    # Шкафчики
    locker_rentals = LockerRentals.objects.filter(
        participant=participant
    ).order_by('-start_date')

    # Мероприятия
    event_participations = EventParticipants.objects.filter(
        participant=participant
    ).order_by('-registration_date')

    # Тренер (если участник является тренером)
    is_trainer = False
    if participant.participant_type == 'trainer':
        is_trainer = True
        # Получаем тренировки, которые ведет этот тренер
        training_sessions_led = TrainingSessions.objects.filter(
            trainer=participant
        ).order_by('-datetime')

    # Рассчитываем статистику
    active_subscriptions = subscriptions.filter(status='active')
    total_cost = sum(sub.tariff_plan.price for sub in active_subscriptions if sub.tariff_plan and sub.tariff_plan.price)

    # Посещаемость
    total_attended = attendance_records.filter(attended=True).count()
    total_sessions = attendance_records.count()
    attendance_percentage = (total_attended / total_sessions * 100) if total_sessions > 0 else 0

    # Средняя оценка
    avg_rating = attendance_records.filter(rating__isnull=False).aggregate(avg=Avg('rating'))['avg']

    # Активные аренды
    active_locker_rentals = locker_rentals.filter(status='active')

    # Рассчитываем возраст
    age = None
    if participant.birth_date:
        today = timezone.now().date()
        age = today.year - participant.birth_date.year - (
                (today.month, today.day) < (participant.birth_date.month, participant.birth_date.day)
        )

    # Получаем системного пользователя (если есть)
    system_user = SystemUsers.objects.filter(member=participant).first()

    # шкафы
    locker_rental = locker_rentals.first() if locker_rentals.exists() else None
    locker_obj = locker_rental.locker if locker_rental else None

    # Формируем контекст для шаблона
    context = {
        'student': participant,
        'subscriptions': subscriptions,
        'payments': payments,
        'training_sessions': training_sessions,
        'attendance_records': attendance_records,
        'locker_rentals': locker_rentals,
        'locker_rental': locker_rental,  # объект LockerRentals
        'locker': locker_obj,  # объект Lockers (сам шкаф)
        'event_participations': event_participations,
        'active_subscriptions_count': active_subscriptions.count(),
        'total_cost': total_cost,
        'total_sessions': total_sessions,
        'total_attended': total_attended,
        'attendance_percentage': round(attendance_percentage, 1),
        'avg_rating': round(avg_rating, 1) if avg_rating else None,
        'active_locker_rentals_count': active_locker_rentals.count(),
        'age': age,
        'system_user': system_user,
        'is_trainer': is_trainer,
    }

    # Добавляем данные о тренировках тренера, если участник - тренер
    if is_trainer:
        context['training_sessions_led'] = training_sessions_led
        context['trainer_sessions_count'] = training_sessions_led.count()
        context['trainer_upcoming_sessions'] = training_sessions_led.filter(
            datetime__gte=timezone.now()
        ).count()

    # Группируем абонементы по статусам для шаблона
    subscription_statuses = {
        'active': subscriptions.filter(status='active'),
        'pending': subscriptions.filter(status='pending'),
        'expired': subscriptions.filter(status='expired'),
        'cancelled': subscriptions.filter(status='cancelled'),
    }
    context['subscription_statuses'] = subscription_statuses

    # Получаем последние заметки из разных источников
    notes_list = []

    # Заметки из модели Participants
    if participant.notes:
        notes_list.append({
            'date': participant.updated_at,
            'content': participant.notes,
            'source': 'Профиль',
            'type': 'general'
        })

    # Заметки из посещаемости
    for attendance in attendance_records.filter(notes__isnull=False):
        notes_list.append({
            'date': attendance.created_at,
            'content': attendance.notes,
            'source': f'Тренировка: {attendance.session.topic}',
            'type': 'attendance'
        })

    # Заметки из платежей
    for payment in payments_all.filter(notes__isnull=False):
        notes_list.append({
            'date': payment.created_at,
            'content': payment.notes,
            'source': f'Платёж: {payment.amount} руб.',
            'type': 'payment'
        })

    # Сортируем заметки по дате
    notes_list.sort(key=lambda x: x['date'], reverse=True)
    context['all_notes'] = notes_list[:20]  # Ограничиваем 20 заметками

    # Подготавливаем данные для графиков (если нужно)
    # Последние 30 дней посещаемости
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_attendance = attendance_records.filter(
        session__datetime__gte=thirty_days_ago
    ).order_by('session__datetime')

    attendance_by_date = {}
    for record in recent_attendance:
        date_str = record.session.datetime.date().isoformat()
        if date_str not in attendance_by_date:
            attendance_by_date[date_str] = {'attended': 0, 'total': 0}
        attendance_by_date[date_str]['total'] += 1
        if record.attended:
            attendance_by_date[date_str]['attended'] += 1

    context['attendance_chart_data'] = {
        'dates': list(attendance_by_date.keys()),
        'attended': [data['attended'] for data in attendance_by_date.values()],
        'total': [data['total'] for data in attendance_by_date.values()]
    }

    return render(request, 'card.html', context)


def calculate_participant_statistics(participant):
    """Рассчитывает статистику по участнику"""
    stats = {
        'total_spent': 0,
        'subscriptions_history': [],
        'equipment_rentals': [],
        'event_history': []
    }

    # Общая сумма потраченных денег
    payments_total = Payments.objects.filter(
        participant=participant,
        status='completed'
    ).aggregate(total=Sum('amount'))['total']

    stats['total_spent'] = payments_total or 0

    # История абонементов
    subscriptions = Subscriptions.objects.filter(
        participant=participant
    ).select_related('tariff_plan').order_by('-start_date')

    for sub in subscriptions:
        stats['subscriptions_history'].append({
            'id': sub.id,
            'name': sub.tariff_plan.name,
            'start_date': sub.start_date,
            'end_date': sub.end_date,
            'status': sub.status,
            'price': sub.tariff_plan.price,
            'auto_renew': sub.auto_renew
        })

    return stats


def get_participant_contacts(participant):
    """Получает контактную информацию участника"""
    contacts = {
        'primary': {
            'phone': participant.phone,
            'email': participant.email,
            'address': participant.address
        },
        'emergency': {
            'contact': participant.emergency_contact,
            'phone': participant.emergency_phone
        }
    }

    # Если есть системный пользователь, добавляем его данные
    system_user = SystemUsers.objects.filter(member=participant).first()
    if system_user:
        contacts['system'] = {
            'username': system_user.username,
            'email': system_user.email,
            'role': system_user.role
        }

    return contacts


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


# views.py
# views.py
def lockers_list_view(request):
    """Страница со списком шкафчиков"""
    from django.core.paginator import Paginator
    from django.db.models import Q

    # Получаем все шкафчики с предзагрузкой связанных данных
    lockers_list = Lockers.objects.all().order_by('zone', 'number')

    # Получаем активные аренды
    active_rentals = LockerRentals.objects.filter(
        Q(status='active') | Q(status='occupied')
    ).select_related('participant', 'locker')

    # Создаем словарь для быстрого доступа к активным арендам
    active_rental_dict = {}
    for rental in active_rentals:
        active_rental_dict[rental.locker_id] = {
            'rental': rental,
            'participant': rental.participant
        }

    # Добавляем вычисляемые поля к каждому шкафчику
    for locker in lockers_list:
        if locker.id in active_rental_dict:
            locker.status = 'occupied'
            locker.current_rental = active_rental_dict[locker.id]['rental']
            locker.current_participant = active_rental_dict[locker.id]['participant']
        else:
            # Проверяем, есть ли другие статусы в самой модели Lockers
            locker.status = 'available'  # По умолчанию свободен
            locker.current_rental = None
            locker.current_participant = None

    # Фильтрация
    zone = request.GET.get('zone')
    status_filter = request.GET.get('status')
    condition = request.GET.get('condition')

    if zone:
        lockers_list = lockers_list.filter(zone=zone)

    # Применяем фильтр по статусу
    if status_filter:
        if status_filter == 'occupied':
            # Оставляем только занятые шкафчики
            occupied_ids = list(active_rental_dict.keys())
            lockers_list = [l for l in lockers_list if l.id in occupied_ids]
        elif status_filter == 'available':
            # Оставляем только свободные шкафчики
            occupied_ids = list(active_rental_dict.keys())
            lockers_list = [l for l in lockers_list if l.id not in occupied_ids]
        # Для других статусов (reserved, maintenance) нужно добавить поле в модель

    if condition:
        lockers_list = lockers_list.filter(condition=condition)

    # Получаем список уникальных зон для фильтра
    zones = Lockers.objects.exclude(
        Q(zone__isnull=True) | Q(zone='')
    ).values_list('zone', flat=True).distinct().order_by('zone')

    # Статистика
    total_count = len(lockers_list)
    occupied_ids = list(active_rental_dict.keys())
    occupied_count = len(occupied_ids)
    available_count = total_count - occupied_count
    maintenance_count = 0  # Можно добавить поле maintenance в модель

    # Пагинация
    paginator = Paginator(lockers_list, 20)
    page_number = request.GET.get('page')
    lockers_page = paginator.get_page(page_number)

    context = {
        'lockers': lockers_page,
        'total_count': total_count,
        'available_count': available_count,
        'occupied_count': occupied_count,
        'maintenance_count': maintenance_count,
        'zones': zones,
        'selected_zone': zone,
        'selected_status': status_filter,
        'selected_condition': condition,
    }

    return render(request, 'lockers_list.html', context)


# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
import json


@api_view(['PATCH'])
@csrf_exempt
def update_locker_view(request, locker_id):
    """Обновление информации о шкафчике"""
    try:
        locker = Lockers.objects.get(id=locker_id)
        data = request.data

        # Обновляем разрешенные поля
        allowed_fields = ['number', 'zone', 'condition', 'monthly_rental_cost', 'notes']
        for field in allowed_fields:
            if field in data:
                setattr(locker, field, data[field] if data[field] != '' else None)

        locker.save()

        return Response({
            'success': True,
            'data': {
                'id': locker.id,
                'number': locker.number,
                'zone': locker.zone,
                'condition': locker.condition,
                'monthly_rental_cost': str(locker.monthly_rental_cost) if locker.monthly_rental_cost else None,
                'notes': locker.notes
            }
        })

    except Lockers.DoesNotExist:
        return Response({'success': False, 'error': 'Шкафчик не найден'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)


@api_view(['POST'])
@csrf_exempt
def create_locker_view(request):
    """Создание нового шкафчика"""
    try:
        data = request.data

        # Проверяем обязательные поля
        if 'number' not in data or not data['number']:
            return Response({'success': False, 'error': 'Номер шкафчика обязателен'}, status=400)

        # Проверяем уникальность номера
        if Lockers.objects.filter(number=data['number']).exists():
            return Response({'success': False, 'error': 'Шкафчик с таким номером уже существует'}, status=400)

        locker = Lockers.objects.create(
            number=data['number'],
            zone=data.get('zone'),
            condition=data.get('condition', 'good'),
            monthly_rental_cost=data.get('monthly_rental_cost'),
            notes=data.get('notes')
        )

        return Response({
            'success': True,
            'data': {
                'id': locker.id,
                'number': locker.number,
                'zone': locker.zone,
                'condition': locker.condition
            }
        })

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)
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