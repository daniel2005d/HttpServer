using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace HttpServer
{
    internal class Operations
    {
        
        
        
        public async Task Upload(string url, string file)
        {
            using (var httpclient = new HttpClient())
            {
                using(var form = new MultipartFormDataContent())
                {
                    using (var filestream = File.OpenRead(file))
                    {
                        var content = new StreamContent(filestream);
                        content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/octet-stream");
                        form.Add(content, "file", Path.GetFileName(file));
                        var response = await httpclient.PostAsync(url, form);
                        var responseString = await response.Content.ReadAsStringAsync();
                        Console.WriteLine(responseString);
                    }
                }
            }
        }
    }
}
