using CommunityToolkit.Mvvm.ComponentModel;
using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.ServicesFE;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ViewModels;

public partial class BaseViewModel : ObservableObject, IDisposable
{
    [ObservableProperty]
    private bool isBusy;

    public bool IsNotBusy => !IsBusy;

    [ObservableProperty]
    private bool acceptTermsAndConditionsStatus;
    partial void OnIsBusyChanged(bool value)
    {
        OnPropertyChanged(nameof(IsNotBusy));
    }


    [ObservableProperty]
    private bool isLoginedIn;
    public bool IsNotLoginedIn => !IsLoginedIn;

    partial void OnIsLoginedInChanged(bool value)
    {
        OnPropertyChanged(nameof(IsNotLoginedIn));
    }

    public LoginResponse LoginResponse = null!;

    public virtual void Dispose()
    {
    }

}
