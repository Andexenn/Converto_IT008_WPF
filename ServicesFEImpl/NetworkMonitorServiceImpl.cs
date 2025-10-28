using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.ViewModels;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;

namespace Converto_IT008_WPF.ServicesFEImpl
{
    public sealed class NetworkMonitorServiceImpl : INetworkMonitorService
    {
        private readonly INavigationService _navigationService;
        private readonly HttpClient _http;
        private readonly Uri _healthCheckpoint;
        private CancellationTokenSource? _cts;
        private Task? _loopTask;
        private TimeSpan _interval = TimeSpan.FromSeconds(5);

        private volatile bool _isOnline = true;
        public bool IsOnline => _isOnline;

        public event Action<bool>? NetworkStatusChanged;

        public NetworkMonitorServiceImpl(INavigationService navigationService)
        {
            _navigationService = navigationService;
            _http = new HttpClient();
            _healthCheckpoint = new Uri("https://www.google.com/");
        }

        public void Start(TimeSpan? interval = null)
        {
            if (_loopTask != null) return;

            _interval = interval ?? _interval;
            _cts = new CancellationTokenSource();
            _loopTask = Task.Run( () => MonitorLoopAsync(_cts.Token));
        }

        public void Stop()
        {
            try
            {
                _cts?.Cancel();
            }
            catch {  /* ignore */}
            _loopTask = null;
            _cts = null;
        }

        private async Task MonitorLoopAsync(CancellationToken ct)
        {
            var timer = new PeriodicTimer(_interval);

            await CheckOnceAsync(ct).ConfigureAwait(false);

            while(await timer.WaitForNextTickAsync(ct).ConfigureAwait(false))
            {
                await CheckOnceAsync(ct).ConfigureAwait(false);
            }
        }

        private async Task CheckOnceAsync(CancellationToken ct)
        {
            bool onlineNow = await ProbeAsync(ct).ConfigureAwait(false);

            if (onlineNow != _isOnline)
            {
                _isOnline = onlineNow;
                // Bắn sự kiện cho ai quan tâm (log, toast, v.v.)
                NetworkStatusChanged?.Invoke(_isOnline);

                if (!_isOnline)
                {
                    // Mất mạng → điều hướng sang Disconnect
                    // Không đụng UI thread: Navigator/Store sẽ lo phần binding.
                    _navigationService.Navigate<DisconnectViewModel>();
                }
                // (Tuỳ ý) khi online trở lại có thể tự động quay về một trang mặc định:
                // else { _navigator.Navigate<HomeViewModel>(); }
            }
        }

        private async Task<bool> ProbeAsync(CancellationToken ct)
        {
            try
            {
                using var req = new HttpRequestMessage(HttpMethod.Head, _healthCheckpoint);
                using var resp = await _http.SendAsync(req, HttpCompletionOption.ResponseHeadersRead, ct)
                                            .ConfigureAwait(false);

                // generate_204 trả 204 No Content khi online
                return resp.IsSuccessStatusCode || (int)resp.StatusCode == 204;
            }
            catch
            {
                return false;
            }
        }

        public void Dispose()
        {
            Stop();
        }

    }
}
