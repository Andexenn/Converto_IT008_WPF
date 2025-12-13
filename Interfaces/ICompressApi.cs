using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Interfaces;

public interface ICompressApi
{
    public Task<byte[]> CompressAsync(string[] filepaths, string typeFormat, string Quality = "low", string Bitrate = "64k");
}
