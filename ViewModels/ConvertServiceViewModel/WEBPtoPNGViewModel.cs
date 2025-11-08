using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ViewModels.ConvertServiceViewModel;

public partial class WEBPtoPNGViewModel : BaseViewModel
{
    INavigationService _navigationService;
    public WEBPtoPNGViewModel(INavigationService navigationService)
    {
        _navigationService = navigationService;
    }

    [RelayCommand]
    void GoBack()
    {
        _navigationService.Navigate<HomepageViewModel>();
    }
}
