release:
	bumpversion patch
	git push
	git push origin $$(git tag --sort=-v:refname --list "v[0-9]*" | head -n 1)
