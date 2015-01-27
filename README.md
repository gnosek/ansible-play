# Group statements with common items/conditions

This module executes all modules just like a top-level play
but allows all normal task attributes (e.g. with_items).
It is useful as a replacement of include when it would be
awkward (e.g. creating one/two line included files), factoring
out repetitive task attributes (when/sudo/remote_user etc.)
including the unsupported include/with_items combination.

All variables set (by e.g. register) are propagated outside
the play and may be used in subsequent tasks

**Note**: gather_facts defaults to false in embedded plays

**Note**: This module (ab)uses internal Ansible APIs and is not
guaranteed to work across all possible versions. Currently tested
and working with 1.7.x (should work with many other versions too)

## Supported constructs (as `play` parameters):

- `tasks`, `pre_tasks` (also with embedded `include`)
- `roles`
- `gather_facts` (defaults to false)
- `hosts` (but please don't use it)
- `include` of whole plays

## Unsupported constructs

- `handlers`, `notify` (only `notify` on the `play` task itself
    is supported)
- `vars`
- `vars_prompt`
- `tags` (tags are applied to the `play` task as a whole)

## Installation
Simply copy (or symlink) the two files into your playbook directory
(preserving directory structure), for example:

	mkdir -p ~/playbooks/library ~/playbooks/action_plugins
	ln -s `pwd`/action_plugins/play.py ~/playbooks/action_plugins/
	ln -s `pwd`/library/play ~/playbooks/library/

## EXAMPLES
### Run a couple of tasks as a different user
    - play:
        tasks:
        - postgresql_user: name=someuser
        - postgresql_db: name=somedb owner=someuser
      sudo: true
      sudo_user: postgres

### Loop over a couple of tasks
    - play:
        tasks:
        - git: repo=http://example.com/{{ item.git }} dest=/usr/local/src/{{ item }}
        - command: make install chdir=/usr/local/src/{{ item }}
      with_items:
      - foo
      - bar

### The elusive include with_items
    - play:
        tasks:
        - include: install.yml pkg={{ item }}
      with_items:
      - foo
      - bar
