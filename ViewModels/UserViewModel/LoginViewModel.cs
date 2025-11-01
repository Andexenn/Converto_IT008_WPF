using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace Converto_IT008_WPF.ViewModels.UserViewModel;

public partial class LoginViewModel : BaseViewModel
{
    public ICommand GoSignUpCommand { get; }
    private readonly INavigationService _nav;

    public LoginViewModel(INavigationService nav)
    {
        _nav = nav;
        GoSignUpCommand = new RelayCommand(() => _nav.Navigate<SignUpViewModel>());
    }


}
