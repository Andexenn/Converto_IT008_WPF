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
        // Store điều hướng
        services.AddSingleton<NavigationStore>(); // :contentReference[oaicite:8]{index=8}
        services.AddSingleton<INavigationService, NavigationServiceImpl>();

        // ViewModels
        services.AddTransient<ViewModels.DisconnectViewModel>(); // :contentReference[oaicite:9]{index=9}
        services.AddTransient<ViewModels.MainWindowViewModel>(); // :contentReference[oaicite:10]{index=10}
        services.AddTransient<ViewModels.HomepageViewModel>();

        // Navigation services (đi thẳng tới DisconnectViewModel)
        //services.AddTransient<INavigationService>(sp =>
        //    new NavigationServiceImpl<ViewModels.DisconnectViewModel>(
        //        sp.GetRequiredService<NavigationStore>(),
        //        () => sp.GetRequiredService<ViewModels.DisconnectViewModel>())); // 

        //services.AddTransient(typeof(INavigationService<>), typeof(NavigationServiceImpl<>));

        // MainWindow + DataContext
        //services.AddSingleton<Views.MainWindow>(sp =>
        //    new Views.MainWindow(sp.GetRequiredService<MainWindowViewModel>()));
        services.AddSingleton<Views.MainWindow>();

        return services;
    }
}
