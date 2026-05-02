# Issue tracker: GitHub

Issues und PRDs leben als GitHub Issues in `noledge5/NovaTerrum`. Alle Operationen über die `gh` CLI.

## Conventions

- **Issue erstellen**: `gh issue create --title "..." --body "..."`
- **Issue lesen**: `gh issue view <number> --comments`
- **Issues listen**: `gh issue list --state open --json number,title,body,labels,comments`
- **Kommentar**: `gh issue comment <number> --body "..."`
- **Labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Schließen**: `gh issue close <number> --comment "..."`

## When a skill says "publish to the issue tracker"

GitHub Issue erstellen.

## When a skill says "fetch the relevant ticket"

`gh issue view <number> --comments` ausführen.
