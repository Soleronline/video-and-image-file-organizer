#!/usr/bin/env python
import click
from organizer_file_helper import organization_file, ACTION_MOVE, ACTION_COPY


@click.group()
@click.version_option("0.1.0")  # , prog_name="file_organizer")
def mycommands():
    pass


@click.command()
@click.argument("directory", type=click.Path(exists=True), required=True)
@click.option(
    "--show_process", help="Show the process", is_flag=True, default=False
)
def info(directory, show_process):
    print("-->", directory, show_process)
    info_files = organization_file(directory, show_process=show_process)
    info_files.print()


@click.command()
@click.argument("directory_src",
                type=click.Path(exists=True),
                required=True
                )
@click.argument("directory_dst",
                type=click.Path(exists=True),
                required=True
                )
@click.option(
    "--show_process", help="Show the process", is_flag=True, default=False
)
def move(directory_src, directory_dst, show_process):
    print(directory_src, " -> ", directory_dst, "--->", show_process)
    info_files = organization_file(
        directory_src,
        directory_dst,
        action=ACTION_MOVE,
        show_process=show_process
    )
    info_files.print()


@click.command()
@click.argument("directory_src",
                type=click.Path(exists=True),
                required=True
                )
@click.argument("directory_dst",
                type=click.Path(exists=True),
                required=True
                )
@click.option(
    "--show_process", help="Show the process", is_flag=True, default=False
)
def copy(directory_src, directory_dst, show_process):
    print(directory_src, " -> ", directory_dst, "--->", show_process)
    info_files = organization_file(
        directory_src,
        directory_dst,
        action=ACTION_COPY,
        show_process=show_process
    )
    info_files.print()


mycommands.add_command(info)
mycommands.add_command(move)
mycommands.add_command(copy)

if __name__ == "__main__":
    mycommands()
