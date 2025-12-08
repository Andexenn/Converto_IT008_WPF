using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using Converto_IT008_WPF.Dto;
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

    void goToLogin()
    {
        WeakReferenceMessenger.Default.Send(
            new CloseOverlayMessage { CloseLogin = false, CloseSignUp = true });
    }

    [RelayCommand]
    void Logout()
    {
        _sessionState.IsUserLoggedIn = false;
        if (_sessionState.LoginResponse != null)
        {
            _sessionState.LoginResponse.access_token = string.Empty;

            _sessionState.LoginResponse.user = null!;

            goToLogin();
        }
    }
}
