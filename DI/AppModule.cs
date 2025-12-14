using Converto_IT008_WPF.Api;
using Converto_IT008_WPF.Interfaces;
using Converto_IT008_WPF.ServicesFE;
using Converto_IT008_WPF.ServicesFEImpl;
using Converto_IT008_WPF.Stores;
using Converto_IT008_WPF.ViewModels.SideServices;
using Converto_IT008_WPF.Views;
using Converto_IT008_WPF.Views.UserViews;
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
        //------------------ Stores ------------------
        services.AddSingleton<NavigationStore>();
        services.AddSingleton<SessionState>();

        //------------------ Services ------------------

        services.AddScoped<INavigationService, NavigationServiceImpl>();
        services.AddScoped<INetworkMonitorService, NetworkMonitorServiceImpl>();
        services.AddScoped<IAuthService, AuthServiceImpl>();
        services.AddScoped<IRemoveBackgroundService, RemoveBackgroundServiceImpl>();
        services.AddScoped<IUserService, UserServiceImpl>();
        services.AddScoped<IProcessImageService, ProcessImageServiceImpl>();
        services.AddScoped<ITaskService, TaskServiceImpl>();
        services.AddScoped<ICompressService, CompressServiceImpl>();
        services.AddScoped<IConvertService, ConvertServiceImpl>();

        //------------------ APIs ------------------

        services.AddHttpClient<IAuthApi, AuthApi>();
        services.AddHttpClient<IRemoveBackgroundApi, RemoveBackgroundApi>();
        services.AddHttpClient<IUserApi, UserApi>();
        services.AddHttpClient<ITaskApi, TaskApi>();
        services.AddHttpClient<ICompressApi, CompressApi>();
        services.AddHttpClient<IConvertApi, ConvertApi>();

        //------------------ ViewModels ------------------
        //GeneralViewModel
        services.AddTransient<ViewModels.DisconnectViewModel>(); 
        services.AddTransient<ViewModels.MainWindowViewModel>(); 
        services.AddTransient<ViewModels.HomepageViewModel>();
        services.AddTransient<ViewModels.AboutUsViewModel>();
        services.AddTransient<ViewModels.HistoryViewModel>();

        services.AddTransient<ViewModels.SideServices.MarkdownToTextViewModel>();
        services.AddTransient<ViewModels.SideServices.RemoveBackgroundViewModel>();
        services.AddTransient<ViewModels.ConvertViewModel>();
        services.AddTransient<CompressViewModel>();

        services.AddTransient<ViewModels.UserViewModel.LoginViewModel>();
        services.AddTransient<ViewModels.UserViewModel.SignUpViewModel>();
        services.AddTransient<ViewModels.UserViewModel.MyAccountViewModel>();

        //PopupViewModel
        services.AddTransient<ViewModels.PopupViewModels.Terms_ConditionsPopupViewModel>();

        //------------------ Views ------------------
        services.AddSingleton<Views.MainWindow>();
        services.AddSingleton<Views.Popups.Terms_ConditionsPopup>();
        services.AddTransient<Views.UserViews.LoginView>();
        services.AddTransient<Views.UserViews.SignUpView>();


        return services;
    }
}
