using Converto_IT008_WPF.Api;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.ServicesFEImpl;
using Converto_IT008_WPF.Stores;
using Converto_IT008_WPF.ViewModels;
using Converto_IT008_WPF.Views;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Http;
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
        //------------------ Services ------------------
        services.AddSingleton<NavigationStore>();
        services.AddSingleton<SessionState>();

        //------------------ Services ------------------

        services.AddScoped<INavigationService, NavigationServiceImpl>();
        services.AddScoped<INetworkMonitorService, NetworkMonitorServiceImpl>();
        services.AddScoped<IAuthService, AuthServiceImpl>();

        //------------------ Services ------------------

        services.AddHttpClient<IAuthApi, AuthApi>();

        //------------------ ViewModels ------------------
        //GeneralViewModel
        services.AddTransient<ViewModels.DisconnectViewModel>(); 
        services.AddTransient<ViewModels.MainWindowViewModel>(); 
        services.AddTransient<ViewModels.HomepageViewModel>();
        services.AddTransient<ViewModels.AboutUsViewModel>();
        services.AddTransient<ViewModels.HistoryViewModel>();
        services.AddTransient<ViewModels.SideServices.MarkdownToTextViewModel>();
        services.AddTransient<ViewModels.SideServices.RemoveBackgroundViewModel>();


        //CompressViewModel
        services.AddTransient<ViewModels.CompressViewModel>();

        //ConvertViewModel
        services.AddTransient<ViewModels.ConvertServiceViewModel.WEBPtoPNGViewModel>();

        //UserViewModel
        services.AddTransient<ViewModels.UserViewModel.LoginViewModel>();
        services.AddTransient<ViewModels.UserViewModel.SignUpViewModel>();
        services.AddTransient<ViewModels.UserViewModel.MyAccountViewModel>();

        //PopupViewModel
        services.AddTransient<ViewModels.PopupViewModels.Terms_ConditionsPopupViewModel>();

        //------------------ Views ------------------
        services.AddSingleton<Views.MainWindow>();
        services.AddSingleton<Views.Popups.Terms_ConditionsPopup>();

        return services;
    }
}
