using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class CompressServiceImpl : ICompressService
{
    private ICompressApi _compressApi;
    public CompressServiceImpl(ICompressApi compressApi)
    {
        _compressApi = compressApi;
    }

    public Task<byte[]> CompressAsync(string[] filepaths, string typeFormat, string Quality = "low", string Bitrate = "64k")
    {
        return _compressApi.CompressAsync(filepaths, typeFormat, Quality, Bitrate);
    }
}
