using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.ServicesFE.UserServices;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;

namespace Converto_IT008_WPF.ViewModels.UserViewModel;

public partial class LoginViewModel : BaseViewModel
{
    public ICommand GoSignUpCommand { get; }
    private readonly IAuthService _authService;
    private readonly INavigationService _nav;

    [ObservableProperty]
    string email = string.Empty;
    [ObservableProperty]
    string password = string.Empty;

    public LoginViewModel(INavigationService nav, IAuthService authService)
    {
        _nav = nav;
        GoSignUpCommand = new RelayCommand(() => _nav.Navigate<SignUpViewModel>());
        _authService = authService;
    }

    [RelayCommand]
    async Task Login()
    {
        try
        {
            LoginRequest loginRequest = new LoginRequest()
            {
                Email = Email,
                Password = Password
            };

            bool ok = await _authService.Login(loginRequest);
            if(ok)
            {
                // Navigate to the main application view upon successful login
                _nav.Navigate<HomepageViewModel>();
            }
            else
            {
                MessageBox.Show("Invalid email or password. Please try again.", "Login Failed", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Error during login: {ex.Message}", "Sign Up Error", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

}
