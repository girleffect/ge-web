from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Profile


class ProfileAdmin(ModelAdmin):
    model = Profile
    menu_label = "Profiles"  # ditch this to use verbose_name_plural from model
    menu_icon = "user"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = ("user", "gender", "location", "date_of_birth")
    list_export = ("user", "gender", "location", "date_of_birth")
    list_filter = ("gender", "date_of_birth")
    export_filename = "users"
    search_fields = ("gender", "location", "date_of_birth")


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(ProfileAdmin)
