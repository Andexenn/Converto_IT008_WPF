using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Stores;

public class SessionState : ObservableObject
{
    [ObservableProperty]
    private bool isUserLoggedIn;
    public bool IsUserLoggedOut => !IsUserLoggedIn;

    partial void OnIsUserLoggedInChanged(bool value)
    {
        OnPropertyChanged(nameof(IsUserLoggedOut));
    }
}
