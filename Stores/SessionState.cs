using CommunityToolkit.Mvvm.ComponentModel;
using Converto_IT008_WPF.Dto.LoginDto;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Stores;

public partial class SessionState : ObservableObject
{
    [ObservableProperty]
    private bool isUserLoggedIn;
    public bool IsUserLoggedOut => !IsUserLoggedIn;

    partial void OnIsUserLoggedInChanged(bool value)
    {
        OnPropertyChanged(nameof(IsUserLoggedOut));
    }

    [ObservableProperty]
    LoginResponse? loginResponse = null;
}
