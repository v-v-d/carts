from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status, Header

from app.app_layer.interfaces.tasks.producer import ITaskProducer
from app.containers import Container

router = APIRouter()


@router.post("/produce", status_code=status.HTTP_202_ACCEPTED)
@inject
async def produce(
    cart_id: UUID,
    auth_data: str = Header(..., alias="Authorization"),
    task_producer: ITaskProducer = Depends(Provide[Container.events.rq_task_producer]),
) -> None:
    await task_producer.enqueue_example_task(auth_data=auth_data, cart_id=cart_id)
