# How to Contribute

You can find the full documentation on [Readthedocs](http://volontaria.readthedocs.io.).

The following is a set of guidelines for contributing to the Volontaria API, which is hosted in the [Volontaria Organization](https://github.com/Volontaria) on GitHub. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[Asking Questions](#asking-questions)

[Getting Started](#getting-started)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [Python Styleguide](#python-styleguide)
  * [Documentation Styleguide](#documentation-styleguide)

[Additional Notes](#additional-notes)
  * [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## Code of Conduct

This project and everyone participating in it is governed by the [Volontaria Code of Conduct](docs/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [volontaria@framalistes.org](mailto:volontaria@framalistes.org).


## Asking Questions

> **Note:** Please don't file an issue to ask a question. You'll get faster results by using the resources below.

You can join the Volontaria Slack team:

* [Join the Volontaria Slack Team](https://join.slack.com/t/volontaria/shared_invite/enQtMjcxODcyNjQwNTk3LTg4OWViMDk5YTQ4OWUxYTFhOWRlYjM2NmM0M2U3YTQ3NmFjYWM4MjlmNzk3NGYxZGVkNTUxYTgzZGU0YThjODg)
    * Even though Slack is a chat service, sometimes it takes several hours for community members to respond &mdash; please be patient!
    * Use the `#volontaria` channel for general questions or discussion about Volontaria
    * Use the `#api` channel for questions and discussion about the API
    * Use the `#website` channel for questions and discussion about the front-end
    * There are many other channels available, check the channel list

## Getting Started

First of all, Volontaria is a test-driven project. That means that a **test must be written before coding a new feature**.

Volontaria's issues can be found in the [Volontaria Github Page](https://github.com/Volontaria). The issues are also listed on [Waffle](https://waffle.io/Volontaria). Feel free to pick one and start contributing!

**Don't forget to comment on the issue before you begin to work on it (or assign it to yourself if you're a member of the organization).**

**Before submitting any contribution, you should really read the next sections.**

Check out the [Quickstart](http://volontaria.readthedocs.io/en/latest/Tutorial/Quickstart/) document to get you started in no time!


## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for Volontaria. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report). Fill out [the required template](.github/ISSUE_TEMPLATE.md), the information it asks for helps us resolve issues faster.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue on the repository and fill in [the template](.github/ISSUE_TEMPLATE.md) automatically generated in the issue text box.

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible. When listing steps, **don't just say what you did, but explain how you did it**.
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples. If you're providing snippets in the issue, use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Include screenshots and animated GIFs** which show you following the described steps and clearly demonstrate the problem. You can use [this tool](http://www.cockos.com/licecap/) to record GIFs on macOS and Windows, and [this tool](https://github.com/colinkeenan/silentcast) or [this tool](https://github.com/GNOME/byzanz) on Linux.
* **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened and share more information using the guidelines below.

Provide more context by answering these questions:

* **Did the problem start happening recently** or was this always a problem?
* If the problem started happening recently, **can you reproduce the problem in an older version?** What's the most recent version in which the problem doesn't happen?
* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens.

Include details about your configuration and environment:

* **What's the name and version of the OS you're using**?
* **Are you running in a virtual machine?** If so, which VM software are you using and which operating systems and versions are used for the host and the guest?
* **Which keyboard layout are you using?** Are you using a US layout or some other layout?

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Volontaria, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.

Before submitting a suggestion, be sure to check these things first:

* **Verify if the same suggestion has already been created on Feathub** so that you do not create a duplicate.
* **If a suggestion similar to yours**, comment on the existing suggestion instead of creating a new one.

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked in [Volontaria Feathub page](https://feathub.com/Volontaria/API-Volontaria).

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include copy/pasteable snippets which you use in those examples, as [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Explain why this enhancement would be useful** to most Volontaria users.
* **Specify the name and version of the OS you're using.**

### Your First Code Contribution

Unsure where to begin contributing to Volontaria? You can start by looking through these `good first issue` and `help-wanted` issues:

* [Good first issue issues][good first issue] - issues which should only require a few lines of code, and a test or two.
* [Help wanted issues][help-wanted] - issues which should be a bit more involved than `good first issue` issues.

### Pull Requests
* Branches naming convention: prefix + snake_case, ex: enhancement-create_new_cell, fix-pep8_standard_on_cell_model
* Fill in automatically generated [PR template](.github/PULL_REQUEST_TEMPLATE.md) in the PR text box
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the [Python Styleguide](#python-styleguide)
* Document new code based on the [Documentation Styleguide](#documentation-styleguide)
* End all files with a newline

## Styleguides

### Git Commit Messages
* Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit"
    >
    > "A paragraph describing what changed and its impact."


* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :non-potable_water: `:non-potable_water:` when plugging memory leaks
    * :memo: `:memo:` when writing docs
    * :penguin: `:penguin:` when fixing something on Linux
    * :apple: `:apple:` when fixing something on macOS
    * :checkered_flag: `:checkered_flag:` when fixing something on Windows
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :green_heart: `:green_heart:` when fixing the CI build
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings

### Python Styleguide

All Python must adhere to the [PEP8 Styleguide](https://www.python.org/dev/peps/pep-0008).

Start reading our code and you'll get the hang of it. We optimize for readability:

  * We indent using four spaces (soft tabs)
  * We ALWAYS put spaces after list items and method parameters (`[1, 2, 3]`, not `[1,2,3]`), around operators (`x += 1`, not `x+=1`), and around hash arrows.
  * We end multi-lines lists or dicts with a comma (
    ```
    mydict = {
      "key1": 1,
      "key2": 2,
      "key3": 3,
    }
    ```
    and not
    ```
    mydict = {
      "key1": 1,
      "key2": 2,
      "key3": 3
    }
    ```
  * When initializing an empty variable, use its type constructor
  ```
  mydict =  dict()
  mylist = list()
  myint = int()
  mybool = bool()
  etc.
  ```
  and not
  ```
  mydict = {}
  mylist = []
  etc.
  ```
  * This is open source software. Consider the people who will read your code, and make it look nice for them. It's sort of like driving a car: Perhaps you love doing donuts when you're alone, but with passengers the goal is to make the ride as smooth as possible.

## Additional Notes

### Issue  Labels

| Label name | `volontaria`‑org :mag_right: | Description |
| --- | --- | --- |
| `enhancement` | [search][search-volontaria-org-label-enhancement] | Feature requests. |
| `backlog` | [search][search-volontaria-org-label-backlog] | Issue to be addressed later. |
| `next` | [search][search-volontaria-org-label-next] | Issue to be addressed for next release. |
| `bug` | [search][search-volontaria-org-label-bug] | Confirmed bugs or reports that are very likely to be bugs. |
| `question` | [search][search-volontaria-org-label-question] | Questions more than bug reports or feature requests (e.g. how do I do X). |
| `help-wanted` | [search][search-volontaria-org-label-help-wanted] | The Volontaria team would appreciate help from the community in resolving these issues. |
| `good first issue` | [search][search-volontaria-org-label-good-first-issue] | Less complex issues which would be good first issues to work on for users who want to contribute to Volontaria. |
| `duplicate` | [search][search-volontaria-org-label-duplicate] | Issues which are duplicates of other issues, i.e. they have been reported before. |
| `invalid` | [search][search-volontaria-org-label-invalid] | Issues which aren't valid (e.g. user errors). |

[search-volontaria-org-label-enhancement]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3Aenhancement+user%3AVolontaria
[search-volontaria-org-label-backlog]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3Abacklog+user%3AVolontaria
[search-volontaria-org-label-next]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3Anext+user%3AVolontaria
[search-volontaria-org-label-bug]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3Abug+user%3AVolontaria
[search-volontaria-org-label-question]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3Aquestion+user%3AVolontaria
[search-volontaria-org-label-help-wanted]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3A"help+wanted"+user%3AVolontaria
[search-volontaria-org-label-good-first-issue]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+user%3AVolontaria+label%3A%22good+first+issue%22
[search-volontaria-org-label-documentation]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3Adocumentation+user%3AVolontaria
[search-volontaria-org-label-duplicate]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3Aduplicate+user%3AVolontaria
[search-volontaria-org-label-invalid]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3Ainvalid+user%3AVolontaria
[search-volontaria-org-label-review]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3Areview+user%3AVolontaria
[search-volontaria-org-label-in-progress]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3A"in+progress"+user%3AVolontaria

[good first issue]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+user%3AVolontaria+label%3A%22good+first+issue%22
[help-wanted]: https://github.com/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+archived%3Afalse+label%3A"help+wanted"+user%3AVolontaria

DISCLAIMER: This contributing document is highly based on [Atom's contributing.md](https://github.com/atom/atom/blob/master/CONTRIBUTING.md)
