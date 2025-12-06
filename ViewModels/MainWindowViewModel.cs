using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Mvvm.Messaging;
using Converto_IT008_WPF.Dto;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
using Converto_IT008_WPF.ViewModels.SideServices;
using System;
using System.Collections.Generic;
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
        private readonly INetworkMonitorService _networkMonitorService;
        public SessionState _sessionState { get; }
        public BaseViewModel CurrentViewModel => _navigationStore.CurrentViewModel;
        public ICommand GoHomepageCommand { get; }
        public ICommand GoAboutUsCommand { get; }
        public ICommand GoHistoryCommand { get; }
        public ICommand GoCompressCommand { get; }
        public ICommand GoLoginCommand { get; }
        public ICommand GoSignUpCommand { get; }
        public ICommand GoMyAccountCommand { get; }
        public ICommand GoMarkdownToTextCommand { get; set; }
        public ICommand GoRemoveBackground { get; }

        public ICommand ShowLoginOverlayCommand { get; set; }
        public ICommand HideLoginOverlayCommand { get; set; }
        public ICommand ShowSignUpOverlayCommand { get; set; }
        public ICommand HideSignUpOverlayCommand { get; set; }

        public MainWindowViewModel(NavigationStore navigationStore, INavigationService nav, INetworkMonitorService networkMonitorService, SessionState sessionState)
        {
            _navigationStore = navigationStore;
            _networkMonitorService = networkMonitorService;
            _sessionState = sessionState;
            IsLoginVisible = true;
            _navigationStore.PropertyChanged += (_, e) =>
            {
                if (e.PropertyName == nameof(_navigationStore.CurrentViewModel))
                {
                    OnPropertyChanged(nameof(CurrentViewModel));
                }
            };
            
            WeakReferenceMessenger.Default.Register<CloseOverlayMessage>(this, (r, m) =>
            {
                if(m.CloseLogin)
                    IsLoginVisible = false;
                if (!m.CloseLogin)
                    IsLoginVisible = true;
                if (!m.CloseSignUp)
                    IsSignUpVisible = true;
                if(m.CloseSignUp)
                    IsSignUpVisible = false;
            });

            GoHomepageCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<HomepageViewModel>(); });
            GoAboutUsCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<AboutUsViewModel>(); });
            GoHistoryCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<HistoryViewModel>(); });
            GoCompressCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<CompressViewModel>(); });
            GoLoginCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<UserViewModel.LoginViewModel>(); });
            GoSignUpCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<UserViewModel.SignUpViewModel>(); });
            GoMyAccountCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<UserViewModel.MyAccountViewModel>(); });
            GoMarkdownToTextCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<SideServices.MarkdownToTextViewModel>(); });
            GoRemoveBackground = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<SideServices.RemoveBackgroundViewModel>(); });
            nav.Navigate<HomepageViewModel>();

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

        [RelayCommand]
        private void CloseApp()
        {
            MessageBoxResult msg = MessageBox.Show("Are you sure you want to exit?", "Confirmation", MessageBoxButton.YesNo, MessageBoxImage.Question);
            if(msg == MessageBoxResult.Yes)
            {
                Application.Current.Shutdown();
            }
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

        ~MainWindowViewModel()
        {
            _networkMonitorService.Stop();
            WeakReferenceMessenger.Default.UnregisterAll(this);
        }
    }

}

