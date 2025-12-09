using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class RemoveBackgroundServiceImpl : IRemoveBackgroundService
{
    IRemoveBackgroundApi removeBackgroundApi;
    public RemoveBackgroundServiceImpl(IRemoveBackgroundApi removeBackgroundApi)
    {
        this.removeBackgroundApi = removeBackgroundApi;
    }

    public async Task<byte[]> RemoveBackgroundAsync(string[] filepaths)
    {
        return await removeBackgroundApi.RemoveBackgroundAsync(filepaths);
    }
}
