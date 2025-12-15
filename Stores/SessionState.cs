using CommunityToolkit.Mvvm.ComponentModel;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.Dto.LoginDto;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.Stores;

public partial class SessionState : ObservableObject
{

    [ObservableProperty]
    LoginResponse? loginResponse = null;

    [ObservableProperty]
    UserPreferencesDto? userPreferences = null;

    public event PropertyChangedEventHandler PropertyChanged;
    protected void OnPropertyChanged([CallerMemberName] string propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
