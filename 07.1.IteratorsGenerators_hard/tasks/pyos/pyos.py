from abc import ABC, abstractmethod
from queue import Queue
from typing import Generator, Any


class SystemCall(ABC):
    """SystemCall yielded by Task to handle with Scheduler"""

    @abstractmethod
    def handle(self, scheduler: 'Scheduler', task: 'Task') -> bool:
        """
        :param scheduler: link to scheduler to manipulate with active tasks
        :param task: task which requested the system call
        :return: an indication that the task must be scheduled again
        """


Coroutine = Generator[SystemCall | None, Any, None]


class Task:
    def __init__(self, task_id: int, target: Coroutine) -> None:
        """
        :param task_id: id of the task
        :param target: coroutine to run. Coroutine can produce system calls.
        System calls are being executed by scheduler and the result sends back to coroutine.
        """
        self.task_id = task_id
        self.target = target
        self.sys_call_result = None
        self.children_ids: list[int] = []

    def set_syscall_result(self, result: Any) -> None:
        """
        Saves result of the last system call
        """
        self.sys_call_result = result

    def add_children(self, task_id: int) -> None:
        self.children_ids.append(task_id)

    def get_children(self) -> list[int]:
        return self.children_ids

    def step(self) -> SystemCall | None:
        """
        Performs one step of coroutine, i.e. sends result of last system call
        to coroutine (generator), gets yielded value and returns it.
        """
        try:
            if self.sys_call_result is not None:
                ret = self.target.send(self.sys_call_result)  # type: ignore
            else:
                ret = self.target.send(None)
            self.sys_call_result = None
            return ret
        except StopIteration:
            return FinishTask(self.task_id)


class Scheduler:
    """Scheduler to manipulate with tasks"""

    def __init__(self) -> None:
        self.task_id = 1
        self.task_queue: Queue[Task] = Queue()
        self.task_map: dict[int, Task] = {}  # task_id -> task
        self.wait_map: dict[int, list[Task]] = {}  # task_id -> list of waiting tasks
        self.killed: set[int] = set()
        self.empty_flag = False

    def _schedule_task(self, task: Task) -> None:
        """
        Add task into task queue
        :param task: task to schedule for execution
        """
        self.task_queue.put(task)

    def new(self, target: Coroutine) -> int:
        """
        Create and schedule new task
        :param target: coroutine to wrap in task
        :return: id of newly created task
        """
        task_id = self.task_id
        self.task_id += 1
        task = Task(task_id, target)
        self.task_map[task_id] = task
        self._schedule_task(task)
        return task_id

    def close_generator(self, task_id: int) -> bool:
        if task_id in self.task_map:
            self.task_map[task_id].target.close()
            return True
        return False

    def exit_task(self, task_id: int) -> bool:
        """
        PRIVATE API: can be used only from scheduler itself or system calls
        Hint: do not forget to reschedule waiting tasks
        :param task_id: task to remove from scheduler
        :return: true if task id is valid
        """
        if task_id in self.task_map:
            del self.task_map[task_id]
            self.killed.add(task_id)
            self._reschedule_waiting_tasks(task_id)
            return True
        return False

    def wait_task(self, task_id: int, wait_id: int) -> bool:
        """
        PRIVATE API: can be used only from scheduler itself or system calls
        :param task_id: task to hold on until another task is finished
        :param wait_id: id of the other task to wait for
        :return: true if task and wait ids are valid task ids
        """
        if task_id in self.task_map and wait_id in self.task_map:
            if wait_id not in self.wait_map:
                self.wait_map[wait_id] = []
            self.wait_map[wait_id].append(self.task_map[task_id])
            return True
        return False

    def run(self, ticks: int | None = None) -> None:
        """
        Executes tasks consequently, gets yielded system calls,
        handles them and reschedules task if needed
        :param ticks: number of iterations (task steps), infinite if not passed
        """
        for _ in range(ticks) if ticks is not None else iter(int, 1):
            if self.task_queue.empty() and not self.wait_map:
                break

            while not self.task_queue.empty():
                active_task = self.task_queue.get()
                if self.__is_waiting(active_task):
                    continue
                if active_task.task_id in self.killed:
                    continue
                result = active_task.step()

                if isinstance(result, SystemCall):
                    result.handle(self, active_task)
                    if active_task.task_id in self.task_map:
                        self._schedule_task(active_task)
                    break

                if active_task.task_id is not None:
                    self._schedule_task(active_task)
                break

    def __is_waiting(self, task: Task) -> bool:
        for k, v in self.wait_map.items():
            if task in v:
                return True
        return False

    def empty(self) -> bool:
        """Checks if there are some scheduled tasks"""
        return not bool(self.task_map)

    def _reschedule_waiting_tasks(self, completed_task_id: int) -> None:
        if completed_task_id in self.wait_map:
            waiting_tasks = self.wait_map.pop(completed_task_id)
            for task in waiting_tasks:
                self._schedule_task(task)


class GetTid(SystemCall):
    """System call to get current task id"""

    def handle(self, scheduler: Scheduler, task: Task) -> bool:
        task.set_syscall_result(task.task_id)
        return True


class NewTask(SystemCall):
    """System call to create new task from target coroutine"""

    def __init__(self, target: Coroutine) -> None:
        self.target = target

    def handle(self, scheduler: Scheduler, task: Task) -> bool:
        new_task_id = scheduler.new(self.target)
        task.set_syscall_result(new_task_id)
        task.add_children(new_task_id)
        return True


class KillTask(SystemCall):
    """System call to kill task with particular task id"""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id

    def handle(self, scheduler: Scheduler, task: Task) -> bool:
        scheduler.close_generator(self.task_id)
        result = scheduler.exit_task(self.task_id)
        task.set_syscall_result(result)
        return True


class WaitTask(SystemCall):
    """System call to wait task with particular task id"""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id

    def handle(self, scheduler: Scheduler, task: Task) -> bool:
        result = scheduler.wait_task(task.task_id, self.task_id)
        task.set_syscall_result(result)
        return True


class FinishTask(SystemCall):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id

    def handle(self, scheduler: Scheduler, task: Task) -> bool:
        scheduler.exit_task(self.task_id)
        return True
