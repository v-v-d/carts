# flake8: noqa
# from typing import Any
#
# from dependency_injector.wiring import Provide, inject
#
# from app.app_layer.interfaces.use_cases.example.items_list import IItemsListUseCase
# from app.containers import Container
#
#
# @inject
# async def example_task(
#     ctx: [str, Any],
#     use_case: IItemsListUseCase = Provide[Container.items_list_use_case],
# ) -> None:
#     await use_case.execute()
