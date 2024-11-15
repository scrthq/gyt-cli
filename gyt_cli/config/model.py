import sys
from pydantic import BaseModel, ConfigDict, Field
import yaml

from gyt_cli.constants import APP_CONFIG_PATH


class ConfigBaseModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


class JiraProject(ConfigBaseModel):
    name: str
    key: str
    subdomain: str
    is_default: bool = Field(default=False)


class JiraConfig(ConfigBaseModel):
    include_comment: bool = Field(default=False)
    projects: dict[str, JiraProject] = Field(default_factory=dict)

    def get_issue_url(self, issue: str) -> str:
        key = issue.split('-')[0]
        if key in self.projects:
            return f'https://{self.projects[key].subdomain}.atlassian.net/browse/{issue}'
        else:
            print(f"No Jira project found for {issue}, finding default project", file=sys.stderr)
            for project in self.projects.values():
                if project.is_default:
                    return f'https://{project.subdomain}.atlassian.net/browse/{issue}'

        raise ValueError(f"No Jira project found for {issue} and no default identified!")


class CommitConfig(ConfigBaseModel):
    default_type: str = Field(default='feat')
    push_on_commit: bool = Field(default=True)


class GytCliConfig(ConfigBaseModel):
    config_path: str = Field(default=str(APP_CONFIG_PATH))
    jira: JiraConfig = Field(default_factory=JiraConfig)
    commit: CommitConfig = Field(default_factory=CommitConfig)

    def model_post_init(self, __context):
        super().model_post_init(__context)
        with open(self.config_path, 'r') as f:
            # Update self with the loaded config
            self.__dict__.update(yaml.safe_load(f))

    def save(self):
        with open(self.config_path, 'w') as f:
            f.write(yaml.dump(self.model_dump()))
        print(f"Configuration saved @ {self.config_path}")
        return self
