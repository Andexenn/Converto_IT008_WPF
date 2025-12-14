using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFE;

public interface IConvertService
{
    public Task<byte[]> ConvertFileAsync(string[] filepaths, string toFormat, string originalTypeFormat);
}
