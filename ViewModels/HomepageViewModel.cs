using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace Converto_IT008_WPF.ViewModels;

public partial class HomepageViewModel : BaseViewModel
{
    public ICommand GoToWEBPtoPNGCommand { get; set; }
    private readonly INavigationService _nav;
    public HomepageViewModel(INavigationService nav)
    {
        _nav = nav;
        GoToWEBPtoPNGCommand = new RelayCommand(() => _nav.Navigate<ConvertServiceViewModel.WEBPtoPNGViewModel>());
    }
}
