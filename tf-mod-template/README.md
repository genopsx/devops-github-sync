This repo is maintained by the **GenOpsX DevOps** team.

Please see the `examples/` directory for deployment information.

[README-TF.md](./README-TF.md) for the documentation for this module.
[variables.tf](./variables.tf) for full list of input variables and descriptions.
[label-mod.tf](./label-mod.tf) for label module declaration and variables.
[outputs.tf](./outputs.tf) for full list of output variables and descriptions.

The GenOpsX DevOps team welcome PRs for this repo;
- Using a Jira ticket number as the branch name, e.g:
    - `git checkout -b JIRA-213`
- Using semantic commit messages, incorporating the jira ticket, e.g:
    - `git commit -am "fix: JIRA-123 update variable typo"`
- We use [pre-commit](https://pre-commit.com/#install).  Please use the following commands before committing:
    - `$ pre-commit install`
    - `$ pre-commit run -a`
- With Conventional commit messages, also with a Jira ticket enclosed.  See [.releaserc.yml](./.releaserc.yml) for hints for commit message structure.
