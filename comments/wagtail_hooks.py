from django.urls import path, reverse
from django.utils.html import format_html
from django_comments.models import CommentFlag
from threadedcomments.models import ThreadedComment
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks

from .views import AdminCommentReplyView


class CommentAdmin(ModelAdmin):
    model = ThreadedComment
    menu_label = "Comments"
    menu_order = 200
    add_to_settings_menu = False
    index_view_extra_js = [
        "js/admin/comments_index.js",
    ]
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
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("is_public"),
                FieldPanel("is_removed"),
            ]
        )
    ]

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


modeladmin_register(CommentAdmin)


@hooks.register("register_admin_urls")
def register_comments_admin_reply_url():
    return [
        path(
            "comment/<int:parent>/reply/",
            AdminCommentReplyView.as_view(extra_context={"parent": "<int:parent>"}),
            name="comments-admin-reply",
        ),
    ]