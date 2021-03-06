# Copyright 2019-2020 SURF.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from http import HTTPStatus
from typing import Optional

from aiocache import Cache
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from oauth2_lib.fastapi import OIDCUserModel
from starlette.background import BackgroundTasks

from orchestrator.api.error_handling import raise_status
from orchestrator.db import EngineSettingsTable
from orchestrator.schemas import EngineSettingsBaseSchema, EngineSettingsSchema, GlobalStatusEnum
from orchestrator.security import oidc_user
from orchestrator.services import settings
from orchestrator.services.processes import SYSTEM_USER
from orchestrator.settings import app_settings

router = APIRouter()


@router.delete("/cache/{name}", status_code=HTTPStatus.NO_CONTENT)
async def clear_cache(name: str, background_tasks: BackgroundTasks) -> None:
    cache = Cache(Cache.REDIS, endpoint=app_settings.CACHE_HOST, port=app_settings.CACHE_PORT)
    if name == "all":
        background_tasks.add_task(cache.delete, "/*")
    else:
        background_tasks.add_task(cache.delete, f"/{name}*")


@router.put("/status", response_model=EngineSettingsSchema)
def set_global_status(
    body: EngineSettingsBaseSchema, user: Optional[OIDCUserModel] = Depends(oidc_user)
) -> EngineSettingsSchema:
    """
    Update the global status of the engine to a new state.

    Args:
        body: The GlobalStatus object

    Returns:
        The updated global status object

    """

    engine_settings = EngineSettingsTable.query.with_for_update().one()

    result = settings.marshall_processes(engine_settings, body.global_lock)
    if not result:
        raise_status(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Something went wrong while updating the database aborting, possible manual intervention required",
        )
    if app_settings.SLACK_ENGINE_SETTINGS_HOOK_ENABLED:
        user_name = user.user_name if user else SYSTEM_USER
        settings.post_update_to_slack(EngineSettingsSchema.from_orm(result), user_name)

    return generate_engine_status_response(result)


@router.get("/status", response_model=EngineSettingsSchema)
def get_global_status() -> EngineSettingsSchema:
    """
    Retrieve the global status object.

    Returns:
        The global status of the engine

    """
    engine_settings = EngineSettingsTable.query.one()
    return generate_engine_status_response(engine_settings)


def generate_engine_status_response(engine_settings: EngineSettingsTable) -> EngineSettingsSchema:
    """
    Generate the correct engine status response.

    Args:
        engine_settings: Engine settings database object

    Returns:
        Engine StatusEnum

    """

    if engine_settings.global_lock and engine_settings.running_processes > 0:
        result = EngineSettingsSchema.from_orm(engine_settings)
        result.global_status = GlobalStatusEnum.PAUSING
        return result
    elif engine_settings.global_lock and engine_settings.running_processes == 0:
        result = EngineSettingsSchema.from_orm(engine_settings)
        result.global_status = GlobalStatusEnum.PAUSED
        return result

    result = EngineSettingsSchema.from_orm(engine_settings)
    result.global_status = GlobalStatusEnum.RUNNING
    return result
