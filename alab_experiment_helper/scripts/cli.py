"""
Useful CLI tools for the alab_management package.
"""

import click
from .launch import launch_server 

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group("cli", context_settings=CONTEXT_SETTINGS)
def cli():
    """Submitting jobs and viewing results for the ALab v1.0 platform."""
    click.echo("---ALab Experiment Helper Started---")


@cli.command("launch", short_help="Start to run the lab")
@click.option(
    "--host",
    default="127.0.0.1",
)
@click.option("-p", "--port", default="8995", type=int)
@click.option("--debug", default=False, is_flag=True)
def launch_lab_cli(host, port, debug):
    click.echo(
        f"The alab_helper API and dashboard will be served at http://{host}:{port}"
    )
    launch_server(host, port, debug)
