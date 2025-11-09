using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.ViewModels.PopupViewModels;
using Converto_IT008_WPF.Views.Popups;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using Converto_IT008_WPF.ServicesFE.UserServices;
using Converto_IT008_WPF.ServicesFE;

namespace Converto_IT008_WPF.ViewModels.UserViewModel;

public partial class SignUpViewModel : BaseViewModel
{
    private readonly IAuthService _authService;
    [ObservableProperty]
    string firstName = string.Empty;
    [ObservableProperty]
    string lastName = string.Empty;
    [ObservableProperty]
    string email = string.Empty;
    [ObservableProperty]
    string password = string.Empty;

    private readonly INavigationService _nav;

    public SignUpViewModel(IAuthService authService, INavigationService navigationService)
    {
        _authService = authService;
        _nav = navigationService;
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

    bool checkCondition()
    {
        return AcceptTermsAndConditionsStatus & !string.IsNullOrEmpty(FirstName) & !string.IsNullOrEmpty(LastName)
            & !string.IsNullOrEmpty(Email) & !string.IsNullOrEmpty(Password);
    }

    [RelayCommand]
    async Task SignUp()
    {
        if (!checkCondition())
        {
            MessageBox.Show("Please fill in all fields and accept the terms and conditions.", "Incomplete Information", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        if(Password.Length <= 8 || !Password.Any(c => char.IsUpper(c)) || !Password.Any(c => char.IsLower(c)) || !Password.Any(c => char.IsDigit(c)) || !Password.Any(c => char.IsLetterOrDigit(c)))
        {
            MessageBox.Show("Password must be at least 8 characters long and include uppercase letters, lowercase letters, and digits.", "Weak Password", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }
        IsBusy = true;
        if (await _authService.CheckMailExisting(Email))
        {
            IsBusy = false;
            MessageBox.Show("The email is already registered. Please use a different email.", "Email Exists", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        SignUpRequest signUpRequest = new SignUpRequest()
        {
            FirstName = FirstName,
            LastName = LastName,
            Email = Email,
            Password = Password
        };

        try
        {
            
            SignUpResponse signUpReponse = await _authService.SignUp(signUpRequest);
            _nav.Navigate<HomepageViewModel>();
        }
        catch (Exception ex)
        {
            // Xử lý lỗi (hiển thị thông báo lỗi, ghi log, v.v.)
            MessageBox.Show($"Error during sign up: {ex.Message}", "Sign Up Error", MessageBoxButton.OK, MessageBoxImage.Error);
        }
        finally
        {
            IsBusy = false;
        }
    }
}
