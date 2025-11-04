using CommunityToolkit.Mvvm.Input;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace Converto_IT008_WPF.ViewModels.PopupViewModels;

public partial class Terms_ConditionsPopupViewModel : BaseViewModel
{
    public event Action? RequestClose;

    [RelayCommand]
    void ClosePopup()
    {
        RequestClose?.Invoke();
    }
}
