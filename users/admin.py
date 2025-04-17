from django.contrib import admin
from .models import UserProfile, SignalProviderProfile, SingnalProviderPost, \
SignalProviderPostItem, LikeSingalProviderPost,ComentSignalProviderPost, \
LikeCommentSignalProviderPost, UserFollewRequest, BlockUser, ReportCommentAbuse, PhoneModel, EmailModel

# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'mobile', 'is_suspended')
    search_fields = ('email',)
    list_filter = ('email', 'mobile', 'is_suspended')
    ordering = ('user',)
    list_per_page = 500

class SingnalProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'mobile', 'is_approved')
    search_fields = ('email',)
    list_filter = ('email', 'mobile', 'is_approved')
    ordering = ('user',)
    list_per_page = 500

class SingnalProviderPostAdmin(admin.ModelAdmin):
    list_display = ('caption', 'is_premium', 'is_approved', 'created_at')
    search_fields = ('caption',)
    list_filter = ('is_approved',)
    ordering = ('created_at',)
    list_per_page = 500

class SignalProviderPostItemAdmin(admin.ModelAdmin):
    list_display = ('caption', 'is_premium', 'is_approved', 'created_at')
    search_fields = ('caption',)
    list_filter = ('is_approved',)
    ordering = ('created_at',)
    list_per_page = 500

class SignalProviderPostItemAdmin(admin.ModelAdmin):
    list_display = ('post', 'created_at')
    search_fields = ('post',)
    list_filter = ('post',)
    ordering = ('post',)
    list_per_page = 500

class LikeSignalProviderPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user',)
    list_filter = ('post',)
    ordering = ('user',)
    list_per_page = 500

class ComentSignalProviderPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'comment', 'created_at')
    search_fields = ('user',)
    list_filter = ('post',)
    ordering = ('user',)
    list_per_page = 500

class LikeCommentSignalProviderPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')
    search_fields = ('user',)
    list_filter = ('comment',)
    ordering = ('user',)
    list_per_page = 500

class UserFollewRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'signal_provider', 'created_at')
    search_fields = ('user',)
    list_filter = ('signal_provider',)
    ordering = ('user',)
    list_per_page = 500


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(SignalProviderProfile, SingnalProviderProfileAdmin)
admin.site.register(SingnalProviderPost, SingnalProviderPostAdmin)
admin.site.register(SignalProviderPostItem, SignalProviderPostItemAdmin)
admin.site.register(LikeSingalProviderPost, LikeSignalProviderPostAdmin)
admin.site.register(ComentSignalProviderPost, ComentSignalProviderPostAdmin)
admin.site.register(LikeCommentSignalProviderPost, LikeCommentSignalProviderPostAdmin)
admin.site.register(UserFollewRequest, UserFollewRequestAdmin)
admin.site.register(BlockUser)
admin.site.register(ReportCommentAbuse)
admin.site.register(PhoneModel)
admin.site.register(EmailModel)
