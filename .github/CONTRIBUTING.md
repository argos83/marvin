# Contributing Guidelines

## Quick Start

### Ideas

- File an [issue][issues].
- Explain why you want the feature. How does it help you? What for do you want the feature?

### Bugs

- File an [issue][issues].
- Ideally, write a failing test and send it as a Pull Request.

### Coding

- Marvin is written in [Python][].
- Marvin uses [Semantic Release](#sem-rel).

#### Recommended Workflow

1. Fork Marvin.
2. Create a feature branch.
3. Execute `source bin/setup-env`
4. Write tests.
5. Write code.
6. test what you created: `pytest tests/`
7. Send a Pull Request.
8. Make sure [test coverage][] didn't drop and all CI builds are passing.

<a name="sem-rel"></a>
#### Semantic Release and Conventional Changelog

Releasing of new Marvin versions to [Pypi][] is automatically managed by [Semantic Release][].
Semantic Release makes sure correct version numbers get bumped according to the **meaning**
of your changes once your PR gets merged to `master`.

To make it work, it's necessary to follow [Conventional Commits][]. That basically
means all commit messages in the project should follow a particular format:

```
<type>: <subject>
```

Where `<type>` is:

- `feat` - New functionality added
- `fix` - Broken functionality fixed
- `perf` - Performance improved
- `docs` - Documentation added/removed/improved/...
- `chore` - Package setup, CI setup, ...
- `refactor` - Changes in code, but no changes in behavior
- `test` - Tests added/removed/improved/...

In the rare cases when your changes break backwards compatibility, the message
must include string `BREAKING CHANGE:`. That will result in bumping the major version.

Seems hard?

- See [existing commits][] as a reference
- A `commit-msg` git hook validates the format of your messages

### Testing

Use `pytest tests/` to run all tests on your default python platform.
Use `tox` to run the tests in all supported platforms.

### Linting

Marvin uses [flake8][] to lint both Marvin and tests codebases. Execute `flake8 marvin tests`.

### Documentation

The main documentation is written in [Markdown][]. Marvin uses
[ReadTheDocs][] to build and publish the documentation:

- [https://marvin-test.readthedocs.io](https://marvin-test.readthedocs.io) - preferred long URL
- [http://marvin-test.rtfd.org](http://marvin-test.rtfd.org) - preferred short URL

Source of the documentation can be found in the [docs][] directory.

#### Note

The `docs/contributing.md` file is a [symbolic link][] to the
`.github/CONTRIBUTING.md` file, where the actual content lives.
This is to be able to serve the same content also as
[GitHub contributing guidelines][] when someone opens a Pull Request.

[symbolic link]: https://en.wikipedia.org/wiki/Symbolic_link
[contributing guidelines]: https://github.com/blog/1184-contributing-guidelines

### Coverage

Marvin strives for as much test coverage as possible. [CodeClimate][] help us to
monitor how successful we are in achieving the goal. If a Pull Request
introduces drop in coverage, it won't be accepted unless the author or reviewer
provides a good reason why an exception should be made.

The `tox` command will execute tests with coverage enabled. As a result an HTML report
will be generated. You can find it at `build/coverage/index.html`.


[Semantic Versioning]: http://semver.org/
[flake8]: http://flake8.pycqa.org
[Python]: https://www.python.org/
[Pypi]: https://pypi.python.org/pypi
[CodeClimate]: https://codeclimate.com/github/argos83/marvin
[Markdown]: https://en.wikipedia.org/wiki/Markdown
[ReadTheDocs]: https://readthedocs.org/
[test coverage]: https://codeclimate.com/github/argos83/marvin
[Semantic Release]: https://github.com/relekang/python-semantic-release
[Conventional Commits]: http://conventionalcommits.org/

[existing commits]: https://github.com/argos83/marvin/commits/master
[docs]: https://github.com/argos83/marvin/tree/master/docs

[issues]: https://github.com/argos83/marvin/issues