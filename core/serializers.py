# core/serializers.py
from rest_framework import serializers
from .models import (
    Participants, TariffPlans, Subscriptions, Payments,
    TrainingSessions, TrainingAttendance, Equipment, EquipmentRentals,
    Events, EventParticipants, Positions, SystemUsers, ChangeLogs,
    Lockers, LockerRentals
)

# === УЧАСТНИКИ ===
class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participants
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# === ТАРИФЫ ===
class TariffPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TariffPlans
        fields = '__all__'
        read_only_fields = ['created_at']


# === АБОНЕМЕНТЫ ===
class SubscriptionSerializer(serializers.ModelSerializer):
    participant = serializers.PrimaryKeyRelatedField(queryset=Participants.objects.all())
    tariff_plan = serializers.PrimaryKeyRelatedField(queryset=TariffPlans.objects.all())

    class Meta:
        model = Subscriptions
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# === ПЛАТЕЖИ ===
class PaymentSerializer(serializers.ModelSerializer):
    participant = serializers.PrimaryKeyRelatedField(queryset=Participants.objects.all())
    subscription = serializers.PrimaryKeyRelatedField(queryset=Subscriptions.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Payments
        fields = '__all__'
        read_only_fields = ['created_at']


# === ТРЕНИРОВКИ ===
class TrainingSessionSerializer(serializers.ModelSerializer):
    trainer = serializers.PrimaryKeyRelatedField(queryset=Participants.objects.all())

    class Meta:
        model = TrainingSessions
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# === ПОСЕЩАЕМОСТЬ ===
class TrainingAttendanceSerializer(serializers.ModelSerializer):
    participant = serializers.PrimaryKeyRelatedField(queryset=Participants.objects.all())
    session = serializers.PrimaryKeyRelatedField(queryset=TrainingSessions.objects.all())

    class Meta:
        model = TrainingAttendance
        fields = '__all__'
        read_only_fields = ['created_at']


# === ИНВЕНТАРЬ ===
class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# === АРЕНДА ИНВЕНТАРЯ ===
class EquipmentRentalSerializer(serializers.ModelSerializer):
    participant = serializers.PrimaryKeyRelatedField(queryset=Participants.objects.all())
    equipment = serializers.PrimaryKeyRelatedField(queryset=Equipment.objects.all())

    class Meta:
        model = EquipmentRentals
        fields = '__all__'
        read_only_fields = ['created_at']


# === МЕРОПРИЯТИЯ ===
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# === УЧАСТНИКИ МЕРОПРИЯТИЙ ===
class EventParticipantSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Events.objects.all())
    participant = serializers.PrimaryKeyRelatedField(queryset=Participants.objects.all())
    payment = serializers.PrimaryKeyRelatedField(queryset=Payments.objects.all(), required=False, allow_null=True)

    class Meta:
        model = EventParticipants
        fields = '__all__'


# === ДОЛЖНОСТИ ===
class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Positions
        fields = '__all__'
        read_only_fields = ['created_at']


# === СИСТЕМНЫЕ ПОЛЬЗОВАТЕЛИ ===
class SystemUserSerializer(serializers.ModelSerializer):
    member = serializers.PrimaryKeyRelatedField(queryset=Participants.objects.all(), required=False, allow_null=True)

    class Meta:
        model = SystemUsers
        fields = '__all__'
        extra_kwargs = {'password_hash': {'write_only': True}}


# === ЛОГИ ИЗМЕНЕНИЙ ===
class ChangeLogSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=SystemUsers.objects.all(), required=False, allow_null=True)

    class Meta:
        model = ChangeLogs
        fields = '__all__'


# === ШКАФЫ ===
class LockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lockers
        fields = '__all__'


# === АРЕНДА ШКАФОВ ===
class LockerRentalSerializer(serializers.ModelSerializer):
    locker = serializers.PrimaryKeyRelatedField(queryset=Lockers.objects.all())
    participant = serializers.PrimaryKeyRelatedField(queryset=Participants.objects.all())
    payment = serializers.PrimaryKeyRelatedField(queryset=Payments.objects.all(), required=False, allow_null=True)

    class Meta:
        model = LockerRentals
        fields = '__all__'