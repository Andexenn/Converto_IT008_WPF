using System.Configuration;
using System.Data;
using System.Windows;
using Converto_IT008_WPF.DI;
using Microsoft.Extensions.DependencyInjection;

namespace Converto_IT008_WPF;

/// <summary>
/// Interaction logic for App.xaml
/// </summary>
public partial class App : Application
{
    public static IServiceProvider? ServiceProvider { get; private set; }

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        var services = new ServiceCollection();

        services.RegisterDependency();
        ServiceProvider = services.BuildServiceProvider();
        var mainWindow = ServiceProvider.GetRequiredService<Views.MainWindow>();
        mainWindow.Show();

    }
}
