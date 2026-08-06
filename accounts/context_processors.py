def notifications_context(request):
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False)
        all_notifications = request.user.notifications.all()[:10]
        return {
            'unread_notifications_count': unread_notifications.count(),
            'unread_notifications': unread_notifications,
            'all_notifications': all_notifications,
        }
    return {
        'unread_notifications_count': 0,
        'unread_notifications': [],
        'all_notifications': [],
    }
