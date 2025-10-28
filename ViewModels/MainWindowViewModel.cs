using CommunityToolkit.Mvvm.Input;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace Converto_IT008_WPF.ViewModels
{
    public partial class MainWindowViewModel : BaseViewModel
    {
        private readonly NavigationStore _navigationStore;
        public BaseViewModel CurrentViewModel => _navigationStore.CurrentViewModel;
        public ICommand GoDisconnectCommand { get; }
        public ICommand GoHomepageCommand { get; }
        public MainWindowViewModel(NavigationStore navigationStore, INavigationService nav)
        {
            _navigationStore = navigationStore;
            _navigationStore.PropertyChanged += (_, e) =>
            {
                if(e.PropertyName == nameof(_navigationStore.CurrentViewModel))
                {
                    OnPropertyChanged(nameof(CurrentViewModel));
                }
            };

            //goDisconnect.Navigate();
            //GoDisconnectCommand = new RelayCommand(() => goDisconnect.Navigate());
            GoDisconnectCommand = new RelayCommand(() => nav.Navigate<DisconnectViewModel>());
            GoHomepageCommand = new RelayCommand(() => nav.Navigate<HomepageViewModel>());
            nav.Navigate<HomepageViewModel>();
        }
    }

}

