# HTTP Server

* **Server**: Receives requests from the client.  
* **Client**: A .NET application that allows uploading files via POST from Windows to the server.

# Server

Supports exposing multiple directories, includes shell integration, allows searching for files, and enables file uploads via POST.

## Installation

```bash
git clone https://github.com/daniel2005d/HttpServer.git
cd HttpServer/Server
pip install .
```


# Usage 

```bash
run-httpserver [-p/--port] [-f/--folder]
```

## Arguments

&nbsp;&nbsp;&nbsp;&nbsp;-p/--port Port where the server will listen.

&nbsp;&nbsp;&nbsp;&nbsp;-f/--folder Directory to expose on startup.

&nbsp;&nbsp;&nbsp;&nbsp;[-d/--defaults] CLoads default folders typically found in most Kali Linux distributions:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;/usr/share/windows-binaries,/opt/SharpCollection/,/opt/nishang/,../Client/Releases/

&nbsp;&nbsp;&nbsp;&nbsp;[-i/--ignore-config] If a configuration file exists, it will be ignored.

## Comands

### history

Displays the history of HTTP requests made.

### info

Shows currently exposed folders.

### add

Exposes a new path without needing to restart the server.
If *defaults* is used, the default Kali directories will be added.

## search

Searches for a file in the exposed directories.

## save

Saves the current configuration and navigation state.
When the server is restarted, it will load from this saved configuration.

## cd

Changes the exposed directory.
Running *cd* with no arguments resets to the initially defined folder.
You can also use an index number to switch to a different directory.

## exit

Exit the application.

# Demo

[![asciicast](https://asciinema.org/a/722173.svg)](https://asciinema.org/a/722173)

# Client

```powershell
.\Upload.exe http://server:port file1 file2 file3
.\Upload.exe http://server:port *.*
```