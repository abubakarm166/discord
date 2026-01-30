"""Utility functions for the rewards app."""

import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_redemption_notification_to_admin(user, reward):
    """
    Send an email notification to the admin when a user redeems a product.

    Args:
        user: The User model instance who redeemed.
        reward: The Reward model instance that was redeemed.
    """
    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    if not admin_email:
        logger.warning('ADMIN_EMAIL not configured. Skipping redemption notification email.')
        return

    subject = f'[Discord Rewards] New Redemption: {user.username} redeemed {reward.name}'
    message = (
        f'A user has redeemed a product.\n\n'
        f'User: {user.username} (Discord ID: {user.discord_id})\n'
        f'Product: {reward.name}\n'
        f'Key Cost: {reward.key_cost} keys\n'
        f'Remaining Balance: {user.key_balance} keys\n'
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=True,  # Don't break redemption if email fails
        )
    except Exception as e:
        logger.exception('Failed to send redemption notification email: %s', e)
