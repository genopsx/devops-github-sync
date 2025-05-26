#!/usr/bin/env python
'''
Update GitHub repositories at scale in an organization.

Example:
  python github_repos.py $orgName -r $repoName -b $branchName --repo-settings allow_merge_commit=false --branch-settings allow_force_pushes=false --slack-webhook $webhookURL
'''
import argparse
import os
import requests
import json
from datetime import datetime as dt

from github import Github, GithubException

# Default settings for each repo
MANDATED_REPO_SETTINGS = {
    'allow_merge_commit': False,  # No merge commit
    'allow_rebase_merge': False,  # No rebase merge
    'allow_squash_merge': True,  # Only squash merge
    'delete_branch_on_merge': True,  # Delete feature branch on merge
}

# Default settings for each protected branch
MANDATED_PROTECTED_BRANCH_SETTINGS = {
    'enforce_admins': True,  # Enforce restrictions on admins as well
    'required_approving_review_count': 1,  # Require separate approval from 1 before merging a PR
    'allow_force_pushes': False,  # Don't allow force pushes to protected branches
    'required_conversation_resolution': True,  # Require all conversations are resolved
}

# Repos that should not have branch protection
EXCLUDE_REPOS = (
    'try-',
    'demo-',
    'example-',
    'nexar-bridge-notes',
    'nexar-client-cs',
    'nexar-client-login',
    'nexar-client-token',
    'nexar-gists',
    'nexar-manufacture-test-ss',
    'nexar-templates',
    'nexar-token-cs',
    'nexar-try-cpp',
    'nexar-tye',
    'PCBViewer',
    'tf-deploy-account-baseline'
)


def edit_branch_protection(branch, settings):
    '''
    Patch function to add branch protection for all supported settings.
    Latest version of PyGithub doesn't support all settings.
    '''
    from github import Consts
    required_params = ('enforce_admins',
                       'required_status_checks',
                       'restrictions')
    post_parameters = {}
    for k, v in settings.items():
        if k in ('dismiss_stale_reviews',
                 'require_code_owner_reviews',
                 'required_approving_review_count'):
            if 'required_pull_request_reviews' not in post_parameters:
                post_parameters['required_pull_request_reviews'] = {}
            post_parameters['required_pull_request_reviews'][k] = v
        else:
            post_parameters[k] = v
    for k in required_params:
        if k not in post_parameters:
            post_parameters[k] = None
    return branch._requester.requestJsonAndCheck(
        'PUT',
        branch.protection_url,
        headers={'Accept': Consts.mediaTypeRequireMultipleApprovingReviews},
        input=post_parameters,
    )


def parse_var(s):
    '''
    Parse a key, value pair, separated by '='
    That's the reverse of ShellArgs.

    On the command line (argparse) a declaration will typically look like:
        foo=hello
    or
        foo="hello world"
    '''
    items = s.split('=')
    key = items[0].strip()  # we remove blanks around keys, as is logical
    if len(items) > 1:
        # rejoin the rest:
        value = '='.join(items[1:])
    if value.lower() in ['true']:
        value = True
    elif value.lower() in ['false']:
        value = False
    return (key, value)


def parse_vars(items):
    d = {}
    if items:
        for item in items:
            key, value = parse_var(item)
            d[key] = value
    return d


def settings_changed(current_settings, desired_settings):
    '''
    Compare current settings with desired settings to determine if changes are needed.
    '''
    for key, value in desired_settings.items():
        if key not in current_settings or current_settings[key] != value:
            return True
    return False


def main(org_name, token, repo_name=None, repo_settings=None, branch_names=None, branch_settings=None, force=False, slack_webhook=None):
    g = Github(token)
    org = g.get_organization(org_name)
    repos = []
    if repo_name:
        repos.append(org.get_repo(repo_name))
    else:
        repos = org.get_repos()
    ret = 0
    changes = []  # List to collect change messages

    for repo in repos:
        print(f'Processing {repo.name}')
        if repo.archived or any([repo.name.startswith(exclude) for exclude in EXCLUDE_REPOS]):
            print(f'Ignoring {repo.name}')
            print('-' * 10)
            continue
        
        # Fetch current repository settings
        current_repo_settings = {
            'allow_merge_commit': repo.allow_merge_commit,
            'allow_rebase_merge': repo.allow_rebase_merge,
            'allow_squash_merge': repo.allow_squash_merge,
            'delete_branch_on_merge': repo.delete_branch_on_merge,
        }

        # Update repo settings if they differ from desired settings
        if settings_changed(current_repo_settings, repo_settings):
            if not force:
                response = input(f'Update repo "{org_name}/{repo.name}" with {repo_settings}? [N/y]: ')
            if force or response.strip().upper() == 'Y':
                try:
                    repo.edit(**repo_settings)
                    change_msg = f'"{org_name}/{repo.name}" updated with {repo_settings}.'
                    changes.append(f"{org_name}/{repo.name}")
                except GithubException as err:
                    print(f'Error updating "{org_name}/{repo.name}": {err}')
                    ret = 1

        # Update branch settings
        branches = []
        if branch_names:
            branches.extend(branch_names)
        branches.append(repo.default_branch)
        for branch_name in branches:
            branch = repo.get_branch(branch_name)
            
            # Fetch current branch protection settings
            try:
                current_branch_protection = branch.get_protection()
                current_branch_settings = {
                    'enforce_admins': current_branch_protection.raw_data['enforce_admins']['enabled'],
                    'required_approving_review_count': current_branch_protection.raw_data['required_pull_request_reviews'].get('required_approving_review_count'),
                    'allow_force_pushes': current_branch_protection.raw_data['allow_force_pushes']['enabled'],
                    'required_conversation_resolution': current_branch_protection.raw_data['required_conversation_resolution']['enabled'],
                }
            except GithubException as err:
                if err.status == 404:
                    print(f'Branch protection not found for "{org_name}/{repo.name}#{branch_name}".')
                    current_branch_settings = {}
                else:
                    print(f'Error fetching protection settings for "{org_name}/{repo.name}#{branch_name}": {err}')
                    ret = 1
                    continue
            
            # Update branch protection if settings differ from desired settings
            if settings_changed(current_branch_settings, branch_settings):
                if not force:
                    response = input(f'Update branch "{org_name}/{repo.name}#{branch_name}" with {branch_settings}? [N/y]: ')
                if force or response.strip().upper() == 'Y':
                    try:
                        edit_branch_protection(branch, branch_settings)
                        change_msg = f'"{org_name}/{repo.name}#{branch_name}" updated with {branch_settings}.'
                        print(change_msg)
                        changes.append(f"{org_name}/{repo.name}#{branch_name}")
                    except GithubException as err:
                        print(f'Error updating "{org_name}/{repo.name}#{branch_name}": {err}')
                        ret = 1
        print('-' * 10)
    
    # Send a Slack message if there are any changes
    if slack_webhook and changes:
        send_slack_webhook(slack_webhook, "\n".join(changes), org_name)

    return ret

def send_slack_webhook(url, changes, org):
    payload = {
        "attachments": [
            {
                "mrkdwn_in": ["pretext", "footer"],
                "pretext": f"GitHub Repository Settings Updated for *{org}*",
                "color": "#FFA500",
                "fields": [
                    {
                        "title": "The following updates were made:",
                        "value": changes,
                        "short": False
                    }
                ],
                "footer": "(https://github.com/genopsx/devops-github-sync/tree/main/.github/workflows)",  # noqa: E501
                "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",  # noqa: E501
                "ts": int(dt.now().timestamp())
            }
        ]
    }

    requests.post(url, json=payload)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('org_name', help='github organization name')
    parser.add_argument('-r', '--repo-name',
                        help='specific repository to configure - otherwise update all repos within the org')
    parser.add_argument('-b', '--branches', metavar='BRANCH_NAME', nargs='+',
                        help='specific branches to add protection to - otherwise update default branch only')
    parser.add_argument('-t', '--token', default=os.getenv('GITHUB_TOKEN'), help='github token')
    parser.add_argument('--repo-settings', metavar='KEY=VALUE', nargs='+',
                        help='key="value" pairs for repo settings - e.g. default_branch=main')
    parser.add_argument('--branch-settings', metavar='KEY=VALUE', nargs='+',
                        help='key="value" pairs for branch settings - e.g. allow_force_pushes=false')
    parser.add_argument('-s', '--slack-webhook', help='URL for slack webhook')
    parser.add_argument('-f', '--force', action='store_true', help='whether to force update without prompts')
    args = parser.parse_args()
    repo_settings = parse_vars(args.repo_settings)
    branch_settings = parse_vars(args.branch_settings)
    # Use mandated settings
    repo_settings.update(MANDATED_REPO_SETTINGS)
    branch_settings.update(MANDATED_PROTECTED_BRANCH_SETTINGS)
    # Prepare messaging
    prep_msg = f'Preparing to edit settings for github org "{args.org_name}".'
    detail_msg = f'This will potentially overwrite existing configuration.\nrepo settings: {repo_settings}\nbranch settings: {branch_settings}\n'
    if args.force:
        print(prep_msg)
        print(detail_msg)
        response = 'Y'
    else:
        input(f'{prep_msg} Press Enter to continue (^C to quit): ')
        response = input(f'{detail_msg} Are you sure you want to proceed? [N/y]: ')
    if response.strip().upper() == 'Y':
        parser.exit(main(org_name=args.org_name, token=args.token, repo_name=args.repo_name, branch_names=args.branches,
                         repo_settings=repo_settings, branch_settings=branch_settings, force=args.force, slack_webhook=args.slack_webhook))

