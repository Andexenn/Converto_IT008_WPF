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
/// Interaction logic for SignUpView.xaml
/// </summary>
public partial class SignUpView : UserControl
{
    public SignUpView()
    {
        InitializeComponent();
        DataContext = App.ServiceProvider?.GetRequiredService<SignUpViewModel>();
    }

    private void PasswordBox_PasswordChanged(object sender, RoutedEventArgs e)
    {
        if(DataContext != null) 
            ((SignUpViewModel)DataContext).Password = ((PasswordBox)sender).Password;
    }
}
