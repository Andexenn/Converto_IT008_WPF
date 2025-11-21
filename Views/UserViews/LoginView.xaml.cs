using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using Converto_IT008_WPF.ViewModels.UserViewModel;
using Microsoft.Extensions.DependencyInjection;

namespace Converto_IT008_WPF.Views.UserViews;

/// <summary>
/// Interaction logic for LoginView.xaml
/// </summary>
public partial class LoginView : UserControl
{
    public LoginView()
    {
        InitializeComponent();
        DataContext = App.ServiceProvider?.GetRequiredService<LoginViewModel>();
    }

    private void PasswordBox_PasswordChanged(object sender, RoutedEventArgs e)
    {
        if (DataContext != null)
            ((LoginViewModel)DataContext).Password = ((PasswordBox)sender).Password;
    }

    private void PlaceholderTextBox_TextChanged(object sender, TextChangedEventArgs e)
    {

    }
}
