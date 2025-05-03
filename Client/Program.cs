using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace HttpServer
{
    internal class Program
    {

        static List<string> ResolveFilePattern(string inputPath)
        {
            var files = new List<string>();

            if (inputPath.Contains("*") || inputPath.Contains("?"))
            {
                // Es un patrón
                string directory = Path.GetDirectoryName(inputPath);
                string pattern = Path.GetFileName(inputPath);

                if (Directory.Exists(directory))
                {
                    files.AddRange(Directory.GetFiles(directory, pattern));
                }
            }
            else
            {
                // Es una ruta específica
                if (File.Exists(inputPath))
                {
                    files.Add(inputPath);
                }
            }

            return files;
        }

        static async Task Main(string[] args)
        {
            try
            {
                var operation = new Operations();
                string server = string.Empty;
                List<string> files = new List<string>();

                foreach (var arg in args)
                {
                    if (arg.ToLower().StartsWith("http"))
                    {
                        server = arg;
                    }
                    else
                    {

                        files.AddRange(ResolveFilePattern(arg));

                    }
                }

                foreach (string file in files)
                {
                    Console.WriteLine($"Uploading {file}");
                    await operation.Upload(server, file);
                }
            }
            catch(Exception e)
            {
                Console.WriteLine(e.ToString());
            }
            
            
        }
    }
}
