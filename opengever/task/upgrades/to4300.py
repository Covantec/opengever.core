from ftw.upgrade import UpgradeStep


class DropOwner(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-opengever.task.upgrades:4300')
        self.update_workflow_security(['opengever_task_workflow'])
