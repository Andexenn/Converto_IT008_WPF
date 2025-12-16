using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.Dto.SignUpDto;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
using System;
using System.Collections.Generic;
using System.Diagnostics;
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
    private readonly IUserService _userService;
    private SessionState _sessionState;

    [ObservableProperty]
    string email = string.Empty;
    [ObservableProperty]
    string password = string.Empty;
    [ObservableProperty]
    string errorMessage = string.Empty;

    public LoginViewModel(INavigationService nav, IAuthService authService, SessionState sessionState, IUserService userService)
    {
        _nav = nav;
        GoSignUpCommand = new RelayCommand(() => _nav.Navigate<SignUpViewModel>());
        _authService = authService;
        _sessionState = sessionState;
        _userService = userService;
    }

    private void CloseOverlay()
    {
        WeakReferenceMessenger.Default.Send(
            new CloseOverlayMessageDto { CloseLogin = true, CloseSignUp = true });
    }

    async Task getUserPreference()
    {
        try
        {
            IsBusy = true;
            UserPreferencesDto prefs = await _userService.GetUserPreferencesAsync();
            _sessionState.UserPreferences = prefs;

        }
        catch(Exception ex)
        {
            MessageBox.Show($"Error fetching user preferences: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
        }
        finally
        {
            IsBusy = false;
        }
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

            if(!await _authService.CheckMailExisting(Email))
            {
                MessageBox.Show("Email does not exist. Please sign up first.", "Login Failed", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            _sessionState.LoginResponse = await _authService.Login(loginRequest);


            if(_sessionState.LoginResponse != null)
            {   
                Properties.Settings.Default.RefreshToken = _sessionState.LoginResponse.refresh_token;
                Properties.Settings.Default.Save();
                await getUserPreference();
                CloseOverlay();
                Email = Password = string.Empty;
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
    async Task SignInWithGoogle()
    {
        try
        {
            IsBusy = true;
            _sessionState.LoginResponse =  await _authService.SignInWithGoolge();

            if(_sessionState.LoginResponse != null)
            {
                Properties.Settings.Default.RefreshToken = _sessionState.LoginResponse.refresh_token;
                Properties.Settings.Default.Save();
                await getUserPreference();
                CloseOverlay();
                Email = Password = string.Empty;
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

    [RelayCommand]
    async Task LoginTmp()
    {
        CloseOverlay();
        _nav.Navigate<HomepageViewModel>();
    }

    [RelayCommand]
    async Task<LoginResponse> SignInWithGithub()
    {
        try
        {
            IsBusy = true; 
            _sessionState.LoginResponse = await _authService.SignInWithGithub();
            if (_sessionState.LoginResponse != null)
            {
                Properties.Settings.Default.RefreshToken = _sessionState.LoginResponse.refresh_token;
                Debug.WriteLine("GitHub login successful. Refresh Token: " + _sessionState.LoginResponse.refresh_token + "Access Token: " + _sessionState.LoginResponse.access_token);
                Properties.Settings.Default.Save();
                await getUserPreference();
                CloseOverlay();
                Email = Password = string.Empty;
                _nav.Navigate<HomepageViewModel>();
                return _sessionState.LoginResponse;
            }
            else
            {
                MessageBox.Show("GitHub login failed. Please try again.", "Login Failed", MessageBoxButton.OK, MessageBoxImage.Error);
                return null;
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Error during GitHub login: {ex.Message}", "GitHub Login Error", MessageBoxButton.OK, MessageBoxImage.Error);
            return null;
        }
        finally
        {
            IsBusy = false;
        }
    }

}
