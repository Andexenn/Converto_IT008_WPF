using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class ConvertServiceImpl : IConvertService
{
    public IConvertApi _convertApi;
    public ConvertServiceImpl(IConvertApi convertApi)
    {
        _convertApi = convertApi;
    }

    public async Task<byte[]> ConvertFileAsync(string[] filepaths, string toFormat, string originalTypeFormat) => await _convertApi.ConvertFileAsync(filepaths, toFormat, originalTypeFormat);
}
