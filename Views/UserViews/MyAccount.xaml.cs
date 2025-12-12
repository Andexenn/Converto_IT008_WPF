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

namespace Converto_IT008_WPF.Views.UserViews;

/// <summary>
/// Interaction logic for MyAccount.xaml
/// </summary>
public partial class MyAccount : UserControl
{
    public MyAccount()
    {
        InitializeComponent();
        DataContext = App.ServiceProvider?.GetRequiredService<MyAccountViewModel>();
    }

    private void PasswordBox_PasswordChanged(object sender, RoutedEventArgs e)
    {
        if (DataContext != null)
        {
            ((MyAccountViewModel)DataContext).Password = ((PasswordBox)sender).Password;
        }
    }

    private void PasswordBox_PasswordChanged_1(object sender, RoutedEventArgs e)
    {
        if (DataContext != null)
        {
            ((MyAccountViewModel)DataContext).ConfirmPassword = ((PasswordBox)sender).Password;
        }
    }

    private void PasswordBox_PreviewMouseWheel(object sender, MouseWheelEventArgs e)
    {
        e.Handled = true;

        var eventArg = new MouseWheelEventArgs(e.MouseDevice, e.Timestamp, e.Delta);
        eventArg.RoutedEvent = UIElement.MouseWheelEvent;
        eventArg.Source = sender;

        var parent = ((Control)sender).Parent as UIElement;

        parent?.RaiseEvent(eventArg);
    }
}
