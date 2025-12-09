using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Interfaces;

public interface IRemoveBackgroundApi
{
    public Task<byte[]> RemoveBackgroundAsync(string[] filepaths);
}
