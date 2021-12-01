from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.views.generic import FormView, TemplateView

import django_comments
from django_comments.views.moderation import perform_flag
from django_comments.views.comments import post_comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from threadedcomments.forms import ThreadedCommentForm


class AdminCommentReplyView(FormView):
    form_class = ThreadedCommentForm
    template_name = "admin/reply.html"
    success_url = reverse_lazy("admin:commenting_molocomment_changelist")

    def get_form_kwargs(self):
        kwargs = super(AdminCommentReplyView, self).get_form_kwargs()
        kwargs["parent"] = self.kwargs["parent"]
        return kwargs

    def form_valid(self, form):
        self.request.POST = self.request.POST.copy()
        self.request.POST["name"] = ""
        self.request.POST["url"] = ""
        self.request.POST["email"] = ""
        self.request.POST["parent"] = self.kwargs["parent"]
        reply = post_comment(self.request, next=self.success_url)
        messages.success(self.request, _("Reply successfully created."))
        return reply
