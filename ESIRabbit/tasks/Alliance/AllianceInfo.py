from ESIRabbit.CeleryApp import app
from ESIRabbit.tasks.BaseTasks.BaseTask import BaseTask
from ESIRabbit.tasks.BaseTasks.ESIResqust import ESIRequest
from ESIRabbit.exceptions.tasks import InputValidationError
from celery.result import AsyncResult


class AllianceInfo(ESIRequest):
    @classmethod
    def ttl_404(cls) -> int:
        return 3600  # current esi x-cached-seconds header

    @classmethod
    def get_key(cls, alliance_id: int):
        return f"AllianceInfo-{alliance_id}"

    @classmethod
    def route(cls, alliance_id: int):
        return f"/alliances/{alliance_id}"

    @classmethod
    def _get_celery_async_result(cls, ignore_result: bool = False, **kwargs) -> AsyncResult:
        return GetAllianceInfo.apply_async(kwargs=kwargs, ignore_result=ignore_result)

    @classmethod
    def validate_inputs(cls, alliance_id: int) -> None:
        try:
            int(alliance_id)
        except ValueError:
            raise InputValidationError("Input parameter must be an integer.")


@app.task(base=BaseTask, bind=True, max_retries=3, retry_backoff=5, autoretry_for=(Exception,))
def GetAllianceInfo(self, **kwargs) -> dict:
    """Gets the cached response or call ESI to get data.

    :param self: self reference for celery retries
    :param kwargs: ESI request parameters
    :return: Dictionary containing response from ESI.
    :rtype: dict
    """
    return AllianceInfo._request_esi(GetAllianceInfo.redis, **kwargs)
