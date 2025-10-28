using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.Stores;
using Converto_IT008_WPF.ViewModels;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFEImpl;

public class NavigationServiceImpl<TViewModel> : INavigationService
    where TViewModel : BaseViewModel
{
    private readonly NavigationStore _store;
    private readonly Func<TViewModel> _factory;
    public NavigationServiceImpl(NavigationStore store, Func<TViewModel> factory)
    {
        _store = store;
        _factory = factory;
    }

    public void Navigate() => _store.CurrentViewModel = _factory();
}
