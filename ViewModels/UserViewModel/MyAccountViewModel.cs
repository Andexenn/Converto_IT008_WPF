using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
using System;
using System.Collections.Generic;
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
        DateOfBirth = _sessionState.LoginResponse.user.DateOfBirth ?? DateTime.Now;

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
            // Handle exceptions if necessary
        }

        
    }
}
