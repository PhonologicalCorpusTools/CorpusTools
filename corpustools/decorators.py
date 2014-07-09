
def check_for_unsaved_changes(function):
    def do_check(*args):
        carry_on = args[0].issue_changes_warning()
        if not carry_on:
            return
        function(args[0])

    return do_check
