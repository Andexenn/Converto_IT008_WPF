using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
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
        private readonly NavigationStore _navigationStore;
        private readonly INetworkMonitorService _networkMonitorService;
        public BaseViewModel CurrentViewModel => _navigationStore.CurrentViewModel;
        public ICommand GoHomepageCommand { get; }
        public ICommand GoAboutUsCommand { get; }
        public ICommand GoHistoryCommand { get; }
        public ICommand GoCompressCommand { get; }
        public ICommand GoLoginCommand { get; }
        public ICommand GoSignUpCommand { get; }
        public ICommand GoMyAccountCommand { get; }
        public ICommand GoTextToImage { get; }
        public ICommand GoRemoveBackground { get; }

        public MainWindowViewModel(NavigationStore navigationStore, INavigationService nav, INetworkMonitorService networkMonitorService)
        {
            _navigationStore = navigationStore;
            _networkMonitorService = networkMonitorService;
            _navigationStore.PropertyChanged += (_, e) =>
            {
                if (e.PropertyName == nameof(_navigationStore.CurrentViewModel))
                {
                    OnPropertyChanged(nameof(CurrentViewModel));
                }
            };

            GoHomepageCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<HomepageViewModel>(); });
            GoAboutUsCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<AboutUsViewModel>(); });
            GoHistoryCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<HistoryViewModel>(); });
            GoCompressCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<CompressViewModel>(); });
            GoLoginCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<UserViewModel.LoginViewModel>(); });
            GoSignUpCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<UserViewModel.SignUpViewModel>(); });
            GoMyAccountCommand = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<UserViewModel.MyAccountViewModel>(); });
            GoTextToImage = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<SideServices.TextToImageViewModel>(); });
            GoRemoveBackground = new RelayCommand(() => { if (_networkMonitorService.checkIsOnline()) nav.Navigate<SideServices.RemoveBackgroundViewModel>(); });
            nav.Navigate<HomepageViewModel>();

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
    }

}

