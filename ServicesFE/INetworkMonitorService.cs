using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFE
{
    public interface INetworkMonitorService : IDisposable
    {
        void Start(TimeSpan? timeSpan = null!);
        void Stop();
        event Action<bool> NetworkStatusChanged;
        bool IsOnline { get; }
    }
}
