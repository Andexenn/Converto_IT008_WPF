using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.ServicesFE.UserServices;
using Converto_IT008_WPF.Stores;
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
    private readonly SessionState _sessionState;

    [ObservableProperty]
    string email = string.Empty;
    [ObservableProperty]
    string password = string.Empty;

    public LoginViewModel(INavigationService nav, IAuthService authService, SessionState sessionState)
    {
        _nav = nav;
        GoSignUpCommand = new RelayCommand(() => _nav.Navigate<SignUpViewModel>());
        _authService = authService;
        _sessionState = sessionState;
    }

    [RelayCommand]
    async Task Login()
    {
        try
        {
            IsBusy = true;
            LoginRequest loginRequest = new LoginRequest()
            {
                Email = Email,
                Password = Password
            };

            _sessionState.LoginResponse = await _authService.Login(loginRequest);
            if(_sessionState.LoginResponse != null)
            {
                // Navigate to the main application view upon successful login
                
                _sessionState.IsUserLoggedIn = true;
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
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    async Task LoginWithGoogle()
    {
        try
        {
            IsBusy = true;
            _sessionState.LoginResponse =  await _authService.SignInWithGoolge();

            if(_sessionState.LoginResponse != null)
            {
                // Navigate to the main application view upon successful login
                _sessionState.IsUserLoggedIn = true;
                _nav.Navigate<HomepageViewModel>();
            }
            else
            {
                MessageBox.Show("Google login failed. Please try again.", "Login Failed", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Error during Google login: {ex.Message}", "Google Login Error", MessageBoxButton.OK, MessageBoxImage.Error);
        }
        finally
        {
            IsBusy = false;
        }
    }

}
