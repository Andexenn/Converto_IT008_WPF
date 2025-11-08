using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.ViewModels.PopupViewModels;
using Converto_IT008_WPF.Views.Popups;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;

namespace Converto_IT008_WPF.ViewModels.UserViewModel;

public partial class SignUpViewModel : BaseViewModel
{

    public SignUpViewModel()
    {

    }





    [RelayCommand]
    void GoTermsAndConditions()
    {
        Terms_ConditionsPopup popup = new Terms_ConditionsPopup();

        var vm = new Terms_ConditionsPopupViewModel();
        popup.DataContext = vm;
        popup.Owner = Application.Current.MainWindow;

        vm.RequestClose += () =>
        {
            AcceptTermsAndConditionsStatus = vm.AcceptTermsAndConditionsStatus;

            // đóng popup
            popup.Close();
        };

        popup.ShowDialog();
    }
}
