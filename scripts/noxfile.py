import nox

TEST_DEPS = [
    "pytest",
    "pytest-cov",
    "pytest-asyncio",
    "pytest-freezegun",
    "ipython",
    "pytest-mock",
    "pytest-env",
]

nox.options.reuse_existing_virtualenvs = True
nox.options.envdir = "../.nox"


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14"])
def tests(session):
    root_dir = session.invoked_from
    test_args = session.posargs or []

    session.chdir(root_dir)

    session.install(".[all]")
    session.install(*TEST_DEPS)
    session.run("pytest", *test_args)
