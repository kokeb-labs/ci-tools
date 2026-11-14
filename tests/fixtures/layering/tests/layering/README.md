# Layering fixtures

`good/` must give no finding; each `bad/<case>/` must give exactly the rule ids in its `expect.txt`. Each case is a
tree of its own, laid out like the repository, checked with `../../rules.yml`.
