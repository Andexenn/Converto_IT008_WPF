using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.ServicesFEImpl;
using Converto_IT008_WPF.Stores;
using Converto_IT008_WPF.ViewModels;
using Converto_IT008_WPF.Views;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Converto_IT008_WPF.DI;

public static class AppModule
{
    public static IServiceCollection RegisterDependency(this IServiceCollection services)
    {
        services.AddSingleton<NavigationStore>(); // :contentReference[oaicite:8]{index=8}
        services.AddScoped<INavigationService, NavigationServiceImpl>();
        services.AddScoped<INetworkMonitorService, NetworkMonitorServiceImpl>();

        //------------------ ViewModels ------------------
        //GeneralViewModel
        services.AddTransient<ViewModels.DisconnectViewModel>(); 
        services.AddTransient<ViewModels.MainWindowViewModel>(); 
        services.AddTransient<ViewModels.HomepageViewModel>();
        services.AddTransient<ViewModels.AboutUsViewModel>();
        services.AddTransient<ViewModels.HistoryViewModel>();

        //CompressViewModel
        services.AddTransient<ViewModels.CompressViewModel>();

        //UserViewModel
        services.AddTransient<ViewModels.UserViewModel.LoginViewModel>();
        services.AddTransient<ViewModels.UserViewModel.SignUpViewModel>();
        services.AddTransient<ViewModels.UserViewModel.MyAccountViewModel>();

        //------------------ Views ------------------
        services.AddSingleton<Views.MainWindow>();


        return services;
    }
}
