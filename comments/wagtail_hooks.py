from django.contrib.admin.views.main import ChangeList
from django.contrib.contenttypes.models import ContentType
from django.templatetags.static import static
from django.urls import path, reverse
from django.utils.html import format_html
from django_comments.models import CommentFlag
from threadedcomments.models import ThreadedComment
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .views import AdminCommentReplyView


class CommentAdmin(ModelAdmin):
    model = ThreadedComment
    menu_label = "Comments"
    menu_order = 200
    add_to_settings_menu = False
    index_view_extra_js = [
        "js/admin.js",
    ]
    exclude_from_explorer = False
    list_display = (
        "user_name",
        "site",
        "comment",
        "parent_comment",
        "moderator_reply",
        "submit_date",
        "is_public",
        "is_removed",
        "flags",
    )
    list_export = (
        "user_name",
        "site",
        "comment",
        "parent_comment",
        "moderator_reply",
        "submit_date",
        "is_public",
        "is_removed",
        "flags",
    )
    list_filter = ("site", "submit_date", "is_public", "is_removed")
    search_fields = ("user", "comment")
    export_filename = "comments"

    def flags(self, obj):
        return CommentFlag.objects.filter(comment=obj).count()

    def moderator_reply(self, obj):
        # We only want to reply to root comments
        if obj.parent is None:
            reply_url = reverse("comments-admin-reply", args=(obj.id,))
            return '<a href="%s"><i class="icon icon-fa-plus"></i>Add reply</a>' % (
                reply_url,
            )
        else:
            return ""

    moderator_reply.allow_tags = True

    def parent_comment(self, obj):
        if obj.parent:
            return format_html(
                '<a href="{}">{}</a>',
                "?tree_path={}".format(obj.tree_path),
                obj.parent.comment,
            )
        else:
            return format_html(
                (
                    '<a href="{}">'
                    "<img "
                    'src = "/static/admin/img/icon-yes.svg" '
                    'alt = "True" >'
                    "</a>"
                ),
                "?tree_path={}".format(obj.tree_path),
            )

    parent_comment.allow_tags = True

    def get_changelist(self, request):
        class ModeratorChangeList(ChangeList):
            def get_queryset(self, request):
                """
                Used by AdminModeratorMixin.moderate_view to somewhat hackishly
                limit comments to only those for the object under review, but
                only if an obj attribute is found on request (which means the
                mixin is being applied and we are not on the standard
                changelist_view).
                """
                qs = super(ModeratorChangeList, self).get_queryset(request)
                obj = getattr(request, "obj", None)
                if obj:
                    ct = ContentType.objects.get_for_model(obj)
                    qs = qs.filter(content_type=ct, object_pk=obj.pk)
                return qs

            def get_results(self, request):
                """
                Create a content_type map to individual objects through their
                id's to avoid additional per object queries for generic
                relation lookup (used in CommentAdmin.content method).
                Also create a comment_reply map to avoid additional reply
                lookups per comment object
                (used in CommentAdmin.moderator_reply method)
                """
                super(ModeratorChangeList, self).get_results(request)
                comment_ids = []
                object_pks = []

                results = list(self.result_list)
                for obj in results:
                    comment_ids.append(obj.id)
                    object_pks.append(obj.object_pk)

                ct_map = {}
                for obj in results:
                    if obj.content_type not in ct_map:
                        ct_map.setdefault(obj.content_type, {})
                        for (
                            content_obj
                        ) in obj.content_type.model_class()._default_manager.filter(
                            pk__in=object_pks
                        ):
                            ct_map[obj.content_type][content_obj.id] = content_obj
                self.model_admin.ct_map = ct_map

        return ModeratorChangeList


modeladmin_register(CommentAdmin)


@hooks.register("register_admin_urls")
def register_comments_admin_reply_url():
    return [
        path(
            "comment/(<int:parent>)/reply/",
            AdminCommentReplyView.as_view(extra_context={"parent": "<int:parent>"}),
            name="comments-admin-reply",
        ),
    ]
