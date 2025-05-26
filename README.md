# devops-github-sync-files
Files common to all DevOps repos that we need to keep in sync.

Even with [template](https://github.com/genopsx/tf-mod-template)  type repositories in GitHub, files in repositories created from the source template can drift out of sync with the original copy.

This repository syncs out copies of those files to specified destination repositories by making uses of the [repo-file-sync-action](https://github.com/genopsx/tf-mod-template).

## How this works

The `.github/sync.yml` file defines files that exist in this repo that are to be synced out to other repos.

The workflow, defined in `.github/workflows/sync_template_files.yml`, defines high level options, such as PR and branch styles on the destination, and also reviewers.

To allow us to sync out lots of types of files from this repo, we group the repos by directory, eg, `tf-mod-template` and put files in that directory that we want to reach repos associated with that template.

A branch and PR are created in the destination repo with the changed files.  Approvals are requested from the persons listed in the Actions configuration.

The following config pushes the `.releaserc.yml` file out from the `tf-mod-template` directory to the listed destination repos.
```
group:
  repos: |
    genopsx/tf-mod-template
  files:
    - source: tf-mod-template/.releaserc.yml
      dest: .releaserc.yml
```
