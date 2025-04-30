Servidor HTTP

* Server: Recibe las peticiones del cliente
* Client: Aplicación en .Net que permite subir archivos por medio de POST desde Windows hacia el Servidor.

# Servidor 

## Instalación

```bash
git clone https://github.com/daniel2005d/HttpServer.git
cd HttpServer/Server
pip install .
```

# Uso 

```bash
run-httpserver [-p/--port] [-f/--folder]
```

# Cliente

```powershell
.\Upload.exe http://server:port file1 file2 file3
.\Upload.exe http://server:port *.*
```