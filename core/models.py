# core/models.py

from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class ChangeLogs(models.Model):
    user = models.ForeignKey('SystemUsers', on_delete=models.CASCADE, blank=True, null=True)
    table_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    action_type = models.CharField(max_length=20, blank=True, null=True)
    changed_data = models.JSONField(blank=True, null=True)
    change_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'change_logs'
        verbose_name = 'Лог изменений'
        verbose_name_plural = 'Логи изменений'

    def __str__(self):
        return f"{self.table_name} #{self.record_id} — {self.action_type}"


class Equipment(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    size = models.CharField(max_length=50, blank=True, null=True)
    condition = models.CharField(max_length=20, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    last_maintenance_date = models.DateField(blank=True, null=True)
    next_maintenance_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'equipment'
        verbose_name = 'Инвентарь'
        verbose_name_plural = 'Инвентарь'

    def __str__(self):
        return self.name


class EquipmentRentals(models.Model):
    participant = models.ForeignKey('Participants', on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    rental_date = models.DateField()
    return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'equipment_rentals'
        verbose_name = 'Аренда инвентаря'
        verbose_name_plural = 'Аренда инвентаря'

    def __str__(self):
        return f"{self.participant} → {self.equipment}"


class EventParticipants(models.Model):
    event = models.ForeignKey('Events', on_delete=models.CASCADE)
    participant = models.ForeignKey('Participants', on_delete=models.CASCADE)
    registration_date = models.DateTimeField(default=timezone.now)
    paid = models.BooleanField(default=False)
    payment = models.ForeignKey('Payments', on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'event_participants'
        unique_together = (('event', 'participant'),)
        verbose_name = 'Участник мероприятия'
        verbose_name_plural = 'Участники мероприятий'

    def __str__(self):
        return f"{self.participant} → {self.event}"


class Events(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField()
    location = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_participants = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    registration_deadline = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return self.name


class LockerRentals(models.Model):
    locker = models.ForeignKey('Lockers', on_delete=models.CASCADE)
    participant = models.ForeignKey('Participants', on_delete=models.CASCADE)
    start_date = models.DateField()
    actual_end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    rental_cost = models.DecimalField(max_digits=8, decimal_places=2)
    payment_period = models.CharField(max_length=20, blank=True, null=True)
    auto_renew = models.BooleanField(default=False)
    key_issued = models.BooleanField(default=False)
    key_issue_date = models.DateField(blank=True, null=True)
    key_return_date = models.DateField(blank=True, null=True)
    payment = models.ForeignKey('Payments', on_delete=models.SET_NULL, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'locker_rentals'
        verbose_name = 'Аренда шкафа'
        verbose_name_plural = 'Аренда шкафов'

    def __str__(self):
        return f"Шкаф {self.locker} → {self.participant}"


class Lockers(models.Model):
    number = models.CharField(unique=True, max_length=20)
    zone = models.CharField(max_length=50, blank=True, null=True)
    condition = models.CharField(max_length=20, blank=True, null=True)
    monthly_rental_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'lockers'
        verbose_name = 'Шкаф'
        verbose_name_plural = 'Шкафы'

    def __str__(self):
        return f"Шкаф №{self.number}"


class Participants(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField()
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    join_date = models.DateField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    participant_type = models.CharField(max_length=20, blank=True, null=True)
    position = models.ForeignKey('Positions', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'participants'
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Payments(models.Model):
    participant = models.ForeignKey(Participants, on_delete=models.CASCADE)
    subscription = models.ForeignKey('Subscriptions', on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20)
    purpose = models.CharField(max_length=50)
    status = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f"{self.amount} руб. — {self.participant}"


class Positions(models.Model):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'positions'
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name


class Subscriptions(models.Model):
    participant = models.ForeignKey(Participants, on_delete=models.CASCADE)
    tariff_plan = models.ForeignKey('TariffPlans', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, blank=True, null=True)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементы'

    def __str__(self):
        return f"{self.participant} — {self.tariff_plan}"


# === СИСТЕМНЫЕ ПОЛЬЗОВАТЕЛИ (с паролем) ===
# core/models.py
class SystemUsers(models.Model):
    username = models.CharField(unique=True, max_length=50)
    password_hash = models.CharField(max_length=255)  # хэш пароля
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=30, blank=True, null=True)
    member = models.ForeignKey(Participants, on_delete=models.SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ДОБАВЬТЕ ЭТИ АТРИБУТЫ ДЛЯ СОВМЕСТИМОСТИ С DJANGO AUTH
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Добавьте эти методы для совместимости
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_staff(self):
        return self.role == 'admin'

    @property
    def is_superuser(self):
        return self.role == 'admin'

    def has_perm(self, perm, obj=None):
        return self.role == 'admin'

    def has_module_perms(self, app_label):
        return self.role == 'admin'

    # Методы для пароля (используем существующие поля)
    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)
        self.save(update_fields=['password_hash'])

    def check_password(self, raw_password):
        # Сначала проверяем через check_password (если пароль хэширован)
        if check_password(raw_password, self.password_hash):
            return True
        # Затем проверяем как обычную строку
        return self.password_hash == raw_password

    # Метод для аутентификации
    def get_username(self):
        return self.username

    class Meta:
        db_table = 'system_users'
        verbose_name = 'Системный пользователь'
        verbose_name_plural = 'Системные пользователи'

    def __str__(self):
        return self.username


class TariffPlans(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    workouts_per_week = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tariff_plans'
        verbose_name = 'Тарифный план'
        verbose_name_plural = 'Тарифные планы'

    def __str__(self):
        return self.name


class TrainingAttendance(models.Model):
    participant = models.ForeignKey(Participants, on_delete=models.CASCADE)
    session = models.ForeignKey('TrainingSessions', on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    rating = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'training_attendance'
        unique_together = (('participant', 'session'),)
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'

    def __str__(self):
        return f"{self.participant} → {self.session}"


class TrainingSessions(models.Model):
    trainer = models.ForeignKey(Participants, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    duration_minutes = models.IntegerField()
    topic = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    max_participants = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'training_sessions'
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'

    def __str__(self):
        return f"{self.topic} — {self.datetime.strftime('%d.%m %H:%M')}"