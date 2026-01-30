from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.conf import settings
import requests
import secrets
from .models import User, Category, Reward, LeaderboardEntry, RedemptionLog
from .utils import send_redemption_notification_to_admin


def landing_page(request):
    """Landing page with Discord login"""
    leaderboard = LeaderboardEntry.objects.filter(is_active=True)[:10]
    return render(request, 'rewards/landing.html', {'leaderboard': leaderboard})


def discord_oauth_login(request):
    """Initiate Discord OAuth flow"""
    if not settings.DISCORD_CLIENT_ID:
        messages.error(request, 'Discord OAuth not configured. Please set DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET.')
        return redirect('landing')
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    # Build Discord OAuth URL
    redirect_uri = settings.DISCORD_REDIRECT_URI
    scope = 'identify'
    discord_oauth_url = (
        f"{settings.DISCORD_API_BASE_URL}/oauth2/authorize"
        f"?client_id={settings.DISCORD_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&state={state}"
    )
    
    return redirect(discord_oauth_url)


def discord_oauth_callback(request):
    """Handle Discord OAuth callback"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    stored_state = request.session.get('oauth_state')
    
    # Verify state
    if not state or state != stored_state:
        messages.error(request, 'Invalid OAuth state. Please try again.')
        return redirect('landing')
    
    # Clear state from session
    request.session.pop('oauth_state', None)
    
    if not code:
        messages.error(request, 'Authorization failed. Please try again.')
        return redirect('landing')
    
    # Exchange code for access token
    token_data = {
        'client_id': settings.DISCORD_CLIENT_ID,
        'client_secret': settings.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.DISCORD_REDIRECT_URI,
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        token_response = requests.post(
            f"{settings.DISCORD_API_BASE_URL}/oauth2/token",
            data=token_data,
            headers=headers
        )
        token_response.raise_for_status()
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        if not access_token:
            messages.error(request, 'Failed to get access token.')
            return redirect('landing')
        
        # Get user info from Discord
        user_headers = {
            'Authorization': f'Bearer {access_token}'
        }
        user_response = requests.get(
            f"{settings.DISCORD_API_BASE_URL}/users/@me",
            headers=user_headers
        )
        user_response.raise_for_status()
        discord_user = user_response.json()
        
        # Get or create user
        discord_id = str(discord_user.get('id'))
        username = discord_user.get('username', 'Unknown')
        avatar_id = discord_user.get('avatar')
        
        # Build avatar URL
        if avatar_id:
            avatar_url = f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_id}.png"
        else:
            avatar_url = None
        
        user, created = User.objects.get_or_create(
            discord_id=discord_id,
            defaults={
                'username': username,
                'avatar': avatar_url,
                'key_balance': 0
            }
        )
        
        # Update user info if not new
        if not created:
            user.username = username
            user.avatar = avatar_url
            user.save()
        
        # Store user ID in session
        request.session['user_id'] = user.id
        request.session['discord_id'] = user.discord_id
        
        return redirect('dashboard')
        
    except requests.RequestException as e:
        messages.error(request, f'Discord authentication failed: {str(e)}')
        return redirect('landing')


def dashboard(request):
    """User dashboard"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return redirect('landing')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        request.session.flush()
        return redirect('landing')
    
    # Get categories that have active rewards
    categories = Category.objects.filter(
        rewards__is_active=True
    ).distinct().order_by('order', 'name')
    
    # Get active rewards (optionally filter by category)
    rewards = Reward.objects.filter(is_active=True).select_related('category')
    
    category_filter = request.GET.get('category')
    selected_category = None
    if category_filter:
        try:
            # Support filter by id or slug
            if category_filter.isdigit():
                selected_category = Category.objects.get(id=category_filter)
            else:
                selected_category = Category.objects.get(slug=category_filter)
            rewards = rewards.filter(category=selected_category)
        except Category.DoesNotExist:
            pass
    
    # Get list of reward IDs that user has already redeemed
    redeemed_reward_ids = set(
        RedemptionLog.objects.filter(user=user)
        .values_list('reward_id', flat=True)
    )
    
    # Get leaderboard winners
    leaderboard = LeaderboardEntry.objects.filter(is_active=True)[:10]
    
    context = {
        'user': user,
        'categories': categories,
        'selected_category': selected_category,
        'rewards': rewards,
        'redeemed_reward_ids': redeemed_reward_ids,
        'leaderboard': leaderboard,
    }
    
    return render(request, 'rewards/dashboard.html', context)


def logout(request):
    """Logout user"""
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('landing')


@require_http_methods(["POST"])
def redeem_reward(request, reward_id):
    """Redeem a reward"""
    user_id = request.session.get('user_id')
    
    if not user_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    try:
        user = User.objects.get(id=user_id)
        reward = Reward.objects.get(id=reward_id, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Reward.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Reward not found'}, status=404)
    
    # Check if user has already redeemed this reward
    if RedemptionLog.objects.filter(user=user, reward=reward).exists():
        return JsonResponse({
            'success': False,
            'error': 'You have already redeemed this reward. Each reward can only be redeemed once.'
        }, status=400)
    
    # Check if user has enough keys
    if user.key_balance < reward.key_cost:
        return JsonResponse({
            'success': False,
            'error': f'Insufficient keys. You need {reward.key_cost} keys but have {user.key_balance}.'
        }, status=400)
    
    # Atomic transaction to deduct keys and log redemption
    try:
        with transaction.atomic():
            # Deduct keys
            user.key_balance -= reward.key_cost
            user.save()
            
            # Log redemption
            RedemptionLog.objects.create(
                user=user,
                reward=reward
            )
        
        # Send email notification to admin
        send_redemption_notification_to_admin(user=user, reward=reward)
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully redeemed {reward.name}!',
            'new_balance': user.key_balance
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Redemption failed: {str(e)}'
        }, status=500)
