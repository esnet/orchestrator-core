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

from dataclasses import asdict
from typing import Dict, List, Optional, Tuple, Type, TypeVar

import structlog

from orchestrator.types import SubscriptionLifecycle, is_list_type, is_optional_type, strEnum
from orchestrator.utils.datetime import nowtz

logger = structlog.get_logger(__name__)


class ProductLifecycle(strEnum):
    ACTIVE = "active"
    PRE_PRODUCTION = "pre production"
    PHASE_OUT = "phase out"
    END_OF_LIFE = "end of life"


_sub_type_per_lifecycle: Dict[Tuple[Type, Optional[SubscriptionLifecycle]], Type] = {}


def register_specialized_type(cls: Type, lifecycle: Optional[List[SubscriptionLifecycle]] = None) -> None:
    if lifecycle:
        for lifecycle_state in lifecycle:
            _sub_type_per_lifecycle[(cls.__base_type__, lifecycle_state)] = cls
    else:
        _sub_type_per_lifecycle[(cls.__base_type__, None)] = cls


def lookup_specialized_type(block: Type, lifecycle: Optional[SubscriptionLifecycle]) -> Type:
    if not hasattr(block, "__base_type__"):
        raise ValueError("Cannot instantiate a class that has no __base_type__ attribute")

    specialized_block = _sub_type_per_lifecycle.get((block.__base_type__, lifecycle), None)
    if specialized_block is None:
        specialized_block = _sub_type_per_lifecycle.get((block.__base_type__, None), None)
    if specialized_block is None:
        specialized_block = block
    return specialized_block


T = TypeVar("T")


def change_lifecycle(subscription: T, status: SubscriptionLifecycle) -> T:
    new_klass = lookup_specialized_type(subscription.__class__, status)
    data = asdict(subscription)

    data["status"] = status
    if data["start_date"] is None and status == SubscriptionLifecycle.ACTIVE:
        data["start_date"] = nowtz()
    if data["end_date"] is None and status == SubscriptionLifecycle.TERMINATED:
        data["end_date"] = nowtz()

    for product_block_field_name, product_block_field_type in new_klass._product_block_fields_.items():
        current = getattr(subscription, product_block_field_name)
        if is_list_type(product_block_field_type):
            data[product_block_field_name] = [asdict(item) for item in current]
        elif is_optional_type(product_block_field_type) and current is None:
            data[product_block_field_name] = None
        else:
            data[product_block_field_name] = asdict(current)

    return new_klass(**data)
