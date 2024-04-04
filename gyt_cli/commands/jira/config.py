import typer
from typing_extensions import Annotated
from gyt_cli.config.model import JiraProject
from gyt_cli.utils import load_config

def add_project(
    name: Annotated[
        str,
        typer.Option(
            help="The name of the Jira project",
        ),
    ],
    key: Annotated[
        str,
        typer.Option(
            help="The key of the Jira project for issues",
        ),
    ],
    subdomain: Annotated[
        str,
        typer.Option(
            help="The subdomain of the Jira Cloud instance on Atlassian",
        ),
    ],
    is_default: Annotated[
        bool,
        typer.Option(
            help="Set this project as the default for issues",
        ),
    ] = False,
):
    """
    Add a new Jira project mapping to the configuration.
    """
    gyt_config = load_config()
    if len(gyt_config.jira.projects) == 0:
        is_default = True
    gyt_config.jira.projects[key] = JiraProject(
        name=name,
        key=key,
        subdomain=subdomain,
        is_default=is_default,
    )
    gyt_config.save()
    print(f"Added project {name} to configuration")


def remove_project(
    key: Annotated[
        str,
        typer.Option(
            help="The key of the Jira project for issues",
        ),
    ]
):
    """
    Remove a Jira project mapping from the configuration.
    """
    gyt_config = load_config()
    proj = gyt_config.jira.projects.get(key, None)
    if not proj:
        raise ValueError(f"No project found in configuration with key {key}")
    del gyt_config.jira.projects[key]
    gyt_config.save()
    print(f"Removed project {key} from configuration")
