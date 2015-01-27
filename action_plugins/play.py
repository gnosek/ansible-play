from ansible import utils
from ansible import callbacks
from ansible.callbacks import call_callback_module, banner
from ansible.utils import template
from ansible.playbook import PlayBook
from ansible.runner.return_data import ReturnData


class EmbeddedPlayBook(PlayBook):

    def __init__(self, **kwargs):
        self.play_kwargs = kwargs.pop('play')
        self.play_kwargs.setdefault('gather_facts', False)
        super(EmbeddedPlayBook, self).__init__(**kwargs)

    def _load_playbook_from_file(self, path, vars={}, vars_files=[]):
        return ([self.play_kwargs], ('.'))


class EmbeddedPlaybookCallbacks(object):

    def __getattr__(self, attr):
        def dummy_cb(*args, **kwargs):
            pass
        return dummy_cb

    skip_task = False


class ActionModule(object):

    def __init__(self, runner):
        self.runner = runner
        self.basedir = runner.basedir

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
        args = {}
        if complex_args:
            args.update(complex_args)

        kv = utils.parse_kv(module_args)
        args.update(kv)

        runner = self.runner
        module_path = None  # don't add any new dirs to module path
        forks = 1  # don't fan out the forks again
        cb = EmbeddedPlaybookCallbacks()
        stats = callbacks.AggregateStats()
        extra_vars = {}  # ?
        only_tags = None  # XXX?
        skip_tags = None  # XXX?
        force_handlers = False  # XXX?

        play = args
        play.setdefault('hosts', runner.pattern)

        pb = EmbeddedPlayBook(
            playbook='(embedded playbook)',
            module_path=module_path,
            inventory=runner.inventory,
            forks=forks,
            remote_user=runner.remote_user,
            remote_pass=runner.remote_pass,
            runner_callbacks=runner.callbacks,
            callbacks=cb,
            stats=stats,
            timeout=runner.timeout,
            transport=runner.transport,
            sudo=runner.sudo,
            sudo_user=runner.sudo_user,
            sudo_pass=runner.sudo_pass,
            extra_vars=extra_vars,
            private_key_file=runner.private_key_file,
            only_tags=only_tags,
            skip_tags=skip_tags,
            check=runner.check,
            diff=runner.diff,
            su=runner.su,
            su_pass=runner.su_pass,
            su_user=runner.su_user,
            vault_password=runner.vault_pass,
            force_handlers=force_handlers,

            play=play,
        )
        pb.run()

        if stats.failures or stats.dark:
            result = dict(failed=True)
        elif stats.changed:
            result = dict(changed=True)
        else:
            result = dict(ok=True)

        return ReturnData(conn=conn, result=result)
