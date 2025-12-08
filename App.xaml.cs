using System.Configuration;
using System.Data;
using System.Windows;
using Converto_IT008_WPF.DI;
using Microsoft.Extensions.DependencyInjection;
using DotNetEnv;
using Converto_IT008_WPF.Config;

namespace Converto_IT008_WPF;

/// <summary>
/// Interaction logic for App.xaml
/// </summary>
public partial class App : Application
{
    public static IServiceProvider? ServiceProvider { get; private set; }
    public static AppConfig AppConfig { get; private set; } = new AppConfig();


    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        var services = new ServiceCollection();

        Env.Load();

        AppConfig.GoogleClientSecret = Environment.GetEnvironmentVariable("GOOGLE_CLIENT_SECRET") ?? string.Empty;
        AppConfig.GoogleClientID = Environment.GetEnvironmentVariable("GOOGLE_CLIENT_ID") ?? string.Empty;
        AppConfig.BaseURL = Environment.GetEnvironmentVariable("BASEURL") ?? string.Empty;
        AppConfig.GithubClientID = Environment.GetEnvironmentVariable("GITHUB_CLIENT_ID") ?? string.Empty;
        AppConfig.GithubClientSecret = Environment.GetEnvironmentVariable("GITHUB_CLIENT_SECRET") ?? string.Empty;

        services.RegisterDependency();
        ServiceProvider = services.BuildServiceProvider();
        var mainWindow = ServiceProvider.GetRequiredService<Views.MainWindow>();
        mainWindow.Show();

    }
}
