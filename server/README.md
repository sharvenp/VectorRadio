# Vector Radio Music Server Configuration

## Dependencies

- [Python (3.9.x)](https://www.python.org/downloads/)
- [pydub](https://pypi.org/project/pydub/)
- [python-websocket-server](https://github.com/Pithikos/python-websocket-server)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Setting Up and Running

Create a `.env` file at the same level as `server.py` and specify the following environment variables:

- `SERVER_PORT` - The port the Vector Radio server will run on
- `SONG_DIR` - Absolute path to the directory with MP3 music

Run `server.py` to run server
