using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.Dto.LoginDto;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
using Converto_IT008_WPF.ViewModels.SideServices;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;

namespace Converto_IT008_WPF.ViewModels
{
    public partial class MainWindowViewModel : BaseViewModel
    {
        private bool _isLoginVisible;
        private bool _isSignUpVisible;

        private readonly NavigationStore _navigationStore;
        private readonly INavigationService _nav;
        private readonly INetworkMonitorService _networkMonitorService;
        private readonly IAuthService _authService;
        private readonly IUserService _userService;
        private readonly IQuoteService _quoteService;
        public SessionState _sessionState { get; }
        public BaseViewModel CurrentViewModel => _navigationStore.CurrentViewModel;
        public ICommand GoHomepageCommand { get; }
        public ICommand GoAboutUsCommand { get; }
        public ICommand GoHistoryCommand { get; }
        public ICommand GoCompressCommand { get; }
        public ICommand GoMyAccountCommand { get; }
        public ICommand GoMarkdownToTextCommand { get; set; }
        public ICommand GoRemoveBackgroundCommand { get; }
        public ICommand GoConvertCommand { get; set; }

        public ICommand ShowLoginOverlayCommand { get; set; }
        public ICommand HideLoginOverlayCommand { get; set; }
        public ICommand ShowSignUpOverlayCommand { get; set; }
        public ICommand HideSignUpOverlayCommand { get; set; }

        public MainWindowViewModel(NavigationStore navigationStore, INavigationService nav, INetworkMonitorService networkMonitorService, SessionState sessionState, IAuthService authService, IUserService userService,
                                    IQuoteService quoteService)
        {
            _navigationStore = navigationStore;
            _networkMonitorService = networkMonitorService;
            _sessionState = sessionState;
            _authService = authService;
            _userService = userService;
            _quoteService = quoteService;
            _nav = nav;

            _sessionState.DailyQuote = _quoteService.GetQuoteofTheDay();

            _ = AutoLogin();

            _navigationStore.PropertyChanged += (_, e) =>
            {
                if (e.PropertyName == nameof(_navigationStore.CurrentViewModel))
                {
                    OnPropertyChanged(nameof(CurrentViewModel));
                }
            };

            WeakReferenceMessenger.Default.Register<CloseOverlayMessageDto>(this, (r, m) =>
            {
                if (m.CloseLogin)
                    IsLoginVisible = false;
                if (!m.CloseLogin)
                    IsLoginVisible = true;
                if (!m.CloseSignUp)
                    IsSignUpVisible = true;
                if (m.CloseSignUp)
                    IsSignUpVisible = false;
            });

            GoHomepageCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<HomepageViewModel>(); });
            GoAboutUsCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<AboutUsViewModel>(); });
            GoHistoryCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<HistoryViewModel>(); });
            GoCompressCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<CompressViewModel>(); });
            GoMyAccountCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<UserViewModel.MyAccountViewModel>(); });
            GoMarkdownToTextCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<SideServices.MarkdownToTextViewModel>(); });
            GoRemoveBackgroundCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<SideServices.RemoveBackgroundViewModel>(); });
            GoConvertCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<ConvertViewModel>(); });
            

            ShowLoginOverlayCommand = new RelayCommand(() =>
            {
                IsLoginVisible = true;
                IsSignUpVisible = false;
            });

            ShowSignUpOverlayCommand = new RelayCommand(() =>
            {
                IsSignUpVisible = true;
                IsLoginVisible = false;
            });

            HideLoginOverlayCommand = new RelayCommand(() => IsLoginVisible = false);
            HideSignUpOverlayCommand = new RelayCommand(() => IsSignUpVisible = false);

            //ktra mang
            _networkMonitorService.Start();
            
        }


        public bool IsLoginVisible
        {
            get { return _isLoginVisible; }
            set
            {
                _isLoginVisible = value;
                OnPropertyChanged();
            }
        }

        public bool IsSignUpVisible
        {
            get { return _isSignUpVisible; }
            set { _isSignUpVisible = value; OnPropertyChanged(); }
        }

        private async Task AutoLogin()
        {
            try
            {
                IsBusy = true;
                Debug.WriteLine($"refresh token: {Properties.Settings.Default.RefreshToken}");
                LoginResponse response = await _authService.RefreshAccessTokenAsync(Properties.Settings.Default.RefreshToken);
                if (response == null)
                    IsLoginVisible = true;
                else
                {
                    _sessionState.LoginResponse = response;
                    _sessionState.UserPreferences = response.user_preferences;
                    IsLoginVisible = false;
                    _nav.Navigate<HomepageViewModel>();
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"AutoLogin failed: {ex.Message}");
            }
            finally
            {
                IsBusy = false;
            }
        }

        [RelayCommand]
        private async Task Logout()
        {
            //_sessionState.IsUserLoggedIn = false;
            if (_sessionState.LoginResponse != null)
            {
                _sessionState.LoginResponse.access_token = string.Empty;

                _sessionState.LoginResponse.user = null!;

                IsLoginVisible = true;

                await _userService.Logout();
            }
        }

        ~MainWindowViewModel()
        {
            _networkMonitorService.Stop();
            WeakReferenceMessenger.Default.UnregisterAll(this);
        }
    }

}

