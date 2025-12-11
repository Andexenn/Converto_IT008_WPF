using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Converto_IT008_WPF.ViewModels.UserViewModel;

public partial class MyAccountViewModel : BaseViewModel
{
    private SessionState _sessionState;
    [ObservableProperty]  
    string _avatarUrl = "pack://application:,,,/Resources/Images/default_avatar.png";
    [ObservableProperty]
    string _firstName = "John";
    [ObservableProperty]
    string _lastName = "Doe";
    [ObservableProperty]
    string _email = "";
    [ObservableProperty]
    DateTime _memberSince = DateTime.Now;
    [ObservableProperty]
    string _city = "Unknown";
    [ObservableProperty]
    string _address = "Unknown";
    [ObservableProperty]
    string _phoneNumber = "Unknown";
    [ObservableProperty]
    DateTime _dateOfBirth = DateTime.Now;
    [ObservableProperty]
    string _username = "";
    [ObservableProperty]
    string _defaultOutputFolder = string.Empty;
    [ObservableProperty]
    string _language = string.Empty;

    public string Password = string.Empty;
    public string ConfirmPassword = string.Empty;

    [ObservableProperty]
    ObservableCollection<string> languages = new ObservableCollection<string>();

    private IUserService _userService;

    public MyAccountViewModel(SessionState sessionState, IUserService userService)
    {
        _sessionState = sessionState;
        AvatarUrl = _sessionState.LoginResponse.user.ProfilePictureURL;
        FirstName = _sessionState.LoginResponse.user.FirstName;
        LastName = _sessionState.LoginResponse.user.LastName;
        Email = _sessionState.LoginResponse.user.Email;
        MemberSince = _sessionState.LoginResponse.user.MemberSince ?? DateTime.Now;
        City = _sessionState.LoginResponse.user.City ?? "Unknown";
        Address = _sessionState.LoginResponse.user.Address ?? "Unknown";
        PhoneNumber = _sessionState.LoginResponse.user.PhoneNumber ?? "Unknown";
        DateOfBirth = DateTime.Now;
        Username = FirstName;

        DefaultOutputFolder = _sessionState.UserPreferences.DefaultOutputFolder;
    

        Languages = new ObservableCollection<string> {
                "Vietnamese", "English"
            };

        Language = Languages[1];

        _userService = userService;
    }

    void goToLogin()
    {
        WeakReferenceMessenger.Default.Send(
            new CloseOverlayMessageDto { CloseLogin = false, CloseSignUp = true });
    }

    [RelayCommand]
    void Logout()
    {
        //_sessionState.IsUserLoggedIn = false;
        if (_sessionState.LoginResponse != null)
        {
            _sessionState.LoginResponse.access_token = string.Empty;

            _sessionState.LoginResponse.user = null!;

            goToLogin();
        }
    }

    [RelayCommand]
    private async Task ChangeAvatarUrl()
    {
        try
        {
            var OpenFileDialog = new OpenFileDialog
            {
                Multiselect = false,
                Filter = "Image Files|*.jpg;*.jpeg;*.png;",
                Title = "Select an Avatar Image"
            };

            if (OpenFileDialog.ShowDialog() == DialogResult.OK)
            {
                string selectedFilePath = OpenFileDialog.FileName;
                AvatarUrl = selectedFilePath;
                _sessionState.LoginResponse.user.ProfilePictureURL = selectedFilePath;
                await _userService.UpdateUserInfoAsync(_sessionState.LoginResponse.user);
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error changing avatar: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task DeleteAccount()
    {
        try
        {
            goToLogin();
            await _userService.DeleteAccount();
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error deleting account: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task SaveChanges()
    {
        try
        {
            _sessionState.LoginResponse.user.FirstName = FirstName;
            _sessionState.LoginResponse.user.LastName = LastName;
            _sessionState.LoginResponse.user.City = City;
            _sessionState.LoginResponse.user.Address = Address;
            _sessionState.LoginResponse.user.PhoneNumber = PhoneNumber;
            _sessionState.LoginResponse.user.DateOfBirth = DateOfBirth.ToString("yyyy-MM-dd");

            await _userService.SaveChanges(_sessionState.LoginResponse.user);
            Username = FirstName;
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error saving changes: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task ChangePassword()
    {
        try
        {
            await _userService.ChangePassword(Password);
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error changing password: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task ChangeDefaultOutputFolder()
    {
        try
        {
            var OpenFolderDialog = new FolderBrowserDialog
            {
                Description = "Select Default Output Folder",
                Multiselect = false,
            };
            if (OpenFolderDialog.ShowDialog() == DialogResult.OK)
            {
                DefaultOutputFolder = OpenFolderDialog.SelectedPath;
                _sessionState.UserPreferences.DefaultOutputFolder = DefaultOutputFolder;
                await _userService.UpdateUserPreference(_sessionState.UserPreferences);
            }
            
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error changing default output folder: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task ChangeLanguage()
    {
        try
        {
            _sessionState.UserPreferences.Language = Language;
            await _userService.UpdateUserPreference(_sessionState.UserPreferences);
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error changing language: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task CancelChangeInfo()
    {
        try
        {
            FirstName = _sessionState.LoginResponse.user.FirstName;
            LastName = _sessionState.LoginResponse.user.LastName;
            City = _sessionState.LoginResponse.user.City ?? "Unknown";
            Address = _sessionState.LoginResponse.user.Address ?? "Unknown";
            PhoneNumber = _sessionState.LoginResponse.user.PhoneNumber ?? "Unknown";
            DateOfBirth = DateTime.Parse(_sessionState.LoginResponse.user.DateOfBirth ?? DateTime.Now.ToString());
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error cancelling changes: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task CancelChangePassword()
    {
        try
        {
            Password = string.Empty;
            ConfirmPassword = string.Empty;
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Error cancelling password change: {ex.Message}");
        }
    }
}
