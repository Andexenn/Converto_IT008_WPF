using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ViewModels;

public partial class DisconnectViewModel : BaseViewModel
{
    private readonly INetworkMonitorService _networkMonitorService;
    private readonly INavigationService _navigationService;

    public DisconnectViewModel(INetworkMonitorService networkMonitorService, INavigationService navigationService)
    {
        _networkMonitorService = networkMonitorService;
        _navigationService = navigationService;
        //_networkMonitorService.NetworkStatusChanged += OnNetworkStatusChanged;
    }

    [RelayCommand]
    async Task Reload()
    {
        IsBusy = true;
        await Task.Delay(2500);
        if (_networkMonitorService.IsOnline)
            _navigationService.Navigate<HomepageViewModel>();
        IsBusy = false;
    }

}

