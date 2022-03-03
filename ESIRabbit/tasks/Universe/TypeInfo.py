from ESIRabbit.CeleryApp import app
from ESIRabbit.tasks.BaseTasks.BaseTask import BaseTask
from ESIRabbit.tasks.BaseTasks.ESIResqust import ESIRequest
from ESIRabbit.exceptions.tasks import InputValidationError
from .GroupInfo import GroupInfo
from celery.result import AsyncResult


class TypeInfo(ESIRequest):
    @classmethod
    def get_key(cls, type_id: int):
        return f"TypeInfo-{type_id}"

    @classmethod
    def route(cls, type_id: int):
        return f"/universe/types/{type_id}"

    @classmethod
    def _get_celery_async_result(cls, ignore_result: bool = False, **kwargs) -> AsyncResult:
        return GetTypeInfo.apply_async(kwargs=kwargs, ignore_result=ignore_result)

    @classmethod
    def _hook_after_esi_success(cls, esi_response: dict) -> None:
        group_id = esi_response.get("group_id")
        if group_id:
            GroupInfo.get_async(ignore_result=True, group_id=group_id)

    @classmethod
    def validate_inputs(cls, type_id: int) -> None:
        try:
            int(type_id)
        except ValueError:
            raise InputValidationError("Input parameter must be an integer.")


@app.task(base=BaseTask, bind=True, max_retries=3, retry_backoff=5, autoretry_for=(Exception,))
def GetTypeInfo(self, **kwargs) -> dict:
    """Gets the cached response or call ESI to get data.

    :param self: self reference for celery retries
    :param kwargs: ESI request parameters
    :return: Dictionary containing response from ESI.
    :rtype: dict
    """
    return TypeInfo._request_esi(GetTypeInfo.redis, **kwargs)
