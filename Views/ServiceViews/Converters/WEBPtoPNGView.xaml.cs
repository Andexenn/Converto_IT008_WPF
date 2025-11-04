using Converto_IT008_WPF.ViewModels.ConvertServiceViewModel;
using Converto_IT008_WPF.ViewModels.UserViewModel;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace Converto_IT008_WPF.Views.ServiceViews.Converters;

/// <summary>
/// Interaction logic for WEBPtoPNGView.xaml
/// </summary>
public partial class WEBPtoPNGView : UserControl
{
    public WEBPtoPNGView()
    {
        InitializeComponent();
        DataContext = App.ServiceProvider?.GetRequiredService<WEBPtoPNGViewModel>();
    }
}
