from .server import cli, create_server
import sys

if len(sys.argv) > 1:
    cli()
else:
    create_server().run(transport="stdio")
