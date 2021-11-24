from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import GEUser


class GEUserAdmin(ModelAdmin):
    model = GEUser
    menu_label = "User"  # ditch this to use verbose_name_plural from model
    menu_icon = "user"  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(GEUserAdmin)
