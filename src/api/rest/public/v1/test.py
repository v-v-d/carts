from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from app.interfaces.task_producer import ITaskProducer
from containers import Container

router = APIRouter()


@router.get("/")
@inject
async def test(task_producer: ITaskProducer = Depends(Provide[Container.task_producer])) -> str:
    await task_producer.enqueue_test_task()
    return "hello from REST api"

