import inspect
from itertools import tee

import simple_history
from django.db import models
from django.db.models.signals import pre_save

from core.middleware import get_current_request, get_current_user
from core.users.models import User

MODELS_TO_AUDIT = []


class CustomHistoricalModel(models.Model):
    """
    Abstract model for history models for adding extra fields
    """

    request_platform = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        abstract = True


def get_custom_history_model_name(original_model_name):
    # This defines historical model name and in turn the table name
    return original_model_name + "_Historical"


def get_current_user_for_simple_history(instance, request):
    # Instance and request are passed by django-simple-history but are of no use to us
    current_user = get_current_user()
    if isinstance(current_user, User):
        return current_user
    return None


def get_method_module_for_simple_history():
    call_stack = inspect.stack()

    for frame_info in reversed(call_stack):
        method_name = frame_info.function
        file_name = frame_info.filename

        # Exclude built-in and module level methods
        if method_name != "<module>" and file_name.startswith("/app/"):
            module_name = inspect.getmodule(frame_info[0]).__name__
            return f"{module_name}.{method_name}"


def pre_save_handler(**kwargs):
    if hasattr(kwargs["instance"], "history_change_reason"):
        current_request = get_current_request()
        if current_request:
            kwargs["instance"].history_change_reason = (
                current_request.method + " " + current_request.path
            )
            kwargs["instance"].request_platform = current_request.META.get(
                "HTTP_X_REQUEST_PLATFORM"
            )
        else:
            try:
                kwargs["instance"].history_change_reason = get_method_module_for_simple_history()
            except:
                kwargs["instance"].history_change_reason = None


for model in MODELS_TO_AUDIT:
    simple_history.register(
        model,
        get_user=get_current_user_for_simple_history,
        custom_model_name=get_custom_history_model_name,
        bases=(CustomHistoricalModel,),
    )

    app_name_str = model._meta.app_label
    model_name_str = model.__name__
    historical_model_name_str = get_custom_history_model_name(model_name_str)
    full_historical_model_name_str = f"{app_name_str}.{historical_model_name_str}"

    pre_save.connect(pre_save_handler, full_historical_model_name_str)


def pair_iterable_for_delta_changes(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def get_historical_data(obj):
    historical_data = []
    obj_iterator = obj.history.all().select_related("history_user").iterator()

    for record_pair in pair_iterable_for_delta_changes(obj_iterator):
        new_record, old_record = record_pair
        delta = new_record.diff_against(old_record)
        data = {
            "changed_by": new_record.history_user.email if new_record.history_user else "System",
            "history_date": new_record.history_date,
            "history_change_reason": new_record.history_change_reason,
            "changes": [],
        }
        # Skip records with no changes.
        if not delta.changes:
            continue

        for change in delta.changes:
            changes = {
                "field": change.field,
                "old_value": str(getattr(old_record, change.field)),
                "new_value": str(getattr(new_record, change.field)),
            }
            data["changes"].append(changes)

        historical_data.append(data)

    return historical_data


def print_human_readable_changes(obj):
    green = "\x1b[1;32m"
    yellow = "\x1b[1;33m"
    end = "\x1b[0m"

    historical_data = get_historical_data(obj)
    for h in historical_data:
        changed_by = h["changed_by"]
        history_date = h["history_date"]
        history_change_reason = h["history_change_reason"]
        changes = h["changes"]
        print(
            f"Changes by {green}{changed_by}{end} at {green}{history_date}{end} via {green}{history_change_reason}{end}"
        )
        for change in changes:
            field = change["field"]
            old = change["old_value"]
            new = change["new_value"]
            print(f"    {yellow}{field}{end} {old} => {new}")
