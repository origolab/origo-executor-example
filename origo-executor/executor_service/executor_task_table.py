from executor.executor import TaskStatus
from flask_table import Table, Col


class TaskTable(Table):
    border = True
    contract_address = Col('Contract Address')
    status = Col('Status')
    progress = Col('Progress')
    finished_task = Col('Finished Task #')
    successful_task = Col('Successful Task #')
    failed_task_info = Col('Failed Tasks info')
    info = Col('Information')


class TaskTableItem(object):
    def __init__(self, task_status):
        """
        The task status item which should be presented by TaskTable
        Args:
            task_status:
        """
        self.contract_address = task_status['contract_address']
        self.status = TaskStatus.get_status_info(task_status['status'])
        self.progress = task_status['progress']
        self.finished_task = task_status['finished_task']
        self.successful_task = task_status['successful_task']
        self.info = task_status['info']
        failed_tasks = []
        for execution_id, info in task_status['failed_tasks'].items():
            failed_tasks.append('Execution ID ' + str(execution_id) + ': ' + str(info))
        self.failed_task_info = '\n'.join(failed_tasks)
