using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.Stores;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ViewModels.UserViewModel;

public partial class MyAccountViewModel : BaseViewModel
{
    private readonly SessionState _sessionState;
    public MyAccountViewModel(SessionState sessionState)
    {
        _sessionState = sessionState;
    }

    [RelayCommand]
    void Logout()
    {
        _sessionState.IsUserLoggedIn = false;
        _sessionState.LoginResponse = null;
    }
}
