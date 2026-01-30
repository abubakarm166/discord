from django.db import models
from django.utils import timezone


class User(models.Model):
    """Discord user model"""
    discord_id = models.CharField(max_length=20, unique=True, db_index=True)
    username = models.CharField(max_length=100)
    avatar = models.URLField(max_length=500, blank=True, null=True)
    key_balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.discord_id})"


class Category(models.Model):
    """Category for grouping rewards"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order (lower = first)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Reward(models.Model):
    """Reward model"""
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rewards'
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='rewards/', blank=True, null=True)
    key_cost = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['key_cost', 'name']

    def __str__(self):
        return f"{self.name} ({self.key_cost} keys)"


class RedemptionLog(models.Model):
    """Log of reward redemptions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='redemptions')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        unique_together = [['user', 'reward']]  # Prevent duplicate redemptions

    def __str__(self):
        return f"{self.user.username} redeemed {self.reward.name} at {self.timestamp}"
