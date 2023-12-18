from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.app_layer.interfaces.task_producer import ITaskProducer
from app.containers import Container

router = APIRouter()


@router.post("/produce", status_code=status.HTTP_202_ACCEPTED)
@inject
async def produce(
    task_producer: ITaskProducer = Depends(Provide[Container.events.task_producer]),
) -> None:
    await task_producer.enqueue_example_task()
