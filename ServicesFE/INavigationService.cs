using Converto_IT008_WPF.ViewModels;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.ServicesFE;

public interface INavigationService
{
    void Navigate<TViewModel>() where TViewModel : BaseViewModel;
}
