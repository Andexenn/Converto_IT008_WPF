using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
using Converto_IT008_WPF.ViewModels;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

class NavigationServiceImpl : INavigationService
{
    private readonly NavigationStore _store;
    private readonly IServiceProvider _serviceProvider;
    public NavigationServiceImpl(NavigationStore store, IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
        _store = store;
    }

    public void Navigate<TViewModel>() where TViewModel : BaseViewModel =>  _store.CurrentViewModel = _serviceProvider.GetRequiredService<TViewModel>();
}
